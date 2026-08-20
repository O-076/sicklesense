import json
from groq import Groq
from app.services.safety import (
    is_patient_specific,
    PATIENT_SAFETY_REFUSAL,
    INSUFFICIENT_EVIDENCE_REFUSAL,
)

GROUNDING_SYSTEM_PROMPT = """You are a citation-bound clinical evidence assistant for sickle cell disease.

Rules:
1. Answer ONLY using the evidence passages provided below. Do not use outside medical knowledge.
2. Every claim in "recommendation" must be directly supported by the text in "evidence".
3. Return the answer as a JSON object matching exactly this structure:
   {
     "recommendation": "...",
     "evidence": "...",
     "citations": [{"document": "...", "section": "...", "page": N, "chunk_id": "..."}],
     "confidence": "high" | "medium" | "low" | "insufficient"
   }
4. If the evidence does not contain enough information to answer with confidence, confidence is set to "insufficient", "evidence" and "citations" are left empty, and "recommendation" contains a plain refusal rather than a guess.
5. Citations are never invented. A refusal is never softened into a partial guess.
6. Patient-specific medical advice is strictly prohibited. Do not diagnose, prescribe, calculate, recommend, or select a treatment, dose, frequency, duration, monitoring schedule, or treatment change for a specific or implied individual patient.
7. Do not apply general clinical recommendations, thresholds, formulas, weight-based doses, age-based recommendations, laboratory values, or other guideline criteria to the characteristics of an individual patient. General clinical information may be provided only when it is clearly presented as general guidance rather than an individualized recommendation.
8. Treat a question as patient-specific when it provides characteristics of an individual, such as age, weight, symptoms, laboratory values, diagnosis, medical history, current medications, or treatment response, and asks what should be done for that individual. If so, refuse the personalized request even when the supplied evidence contains enough information to answer it.
9. Do not perform arithmetic, calculations, or other transformations on guideline information when doing so would produce a personalized dose, treatment recommendation, monitoring decision, or other clinical decision. When refusing a patient-specific request, set "confidence" to "insufficient" and leave "evidence" and "citations" empty. The "recommendation" should briefly explain that the system provides general clinical information and cannot make individualized medical decisions.
"""

# Calibrated relevance cutoff for Azure AI Search RRF scores
RETRIEVAL_THRESHOLD = 0.020

def verify_citations(answer: dict, evidence_blocks: list) -> list:
    """Verifies that every cited chunk_id was in retrieved context and checks lexical overlap."""
    evidence_by_id = {e["chunk_id"]: e for e in evidence_blocks}
    report = []
    
    for c in answer.get("citations", []):
        cid = c.get("chunk_id")
        if cid not in evidence_by_id:
            report.append({
                "chunk_id": cid or "unknown",
                "status": "fabricated citation: chunk_id not present in retrieved evidence",
                "passed": False
            })
            continue
            
        real_text = evidence_by_id[cid]["text"].lower()
        rec_words = answer.get("recommendation", "").lower().split()[:6]
        overlap_ok = any(word in real_text for word in rec_words)
        
        status = "passed" if overlap_ok else "flagged for manual review: low lexical overlap"
        report.append({
            "chunk_id": cid,
            "status": status,
            "passed": True
        })
    return report

def run_grounded_rag(query: str, retrieved_chunks: list, groq_client: Groq, model: str) -> dict:
    """Runs the 4-gate grounded generation pipeline."""
    # Gate 1: Patient-specific safety gate
    if is_patient_specific(query):
        res = PATIENT_SAFETY_REFUSAL.copy()
        res["verification_status"] = [{"chunk_id": "none", "status": "blocked by patient safety gate", "passed": True}]
        return res

    # Gate 2: Evidence relevance threshold gate
    top_score = retrieved_chunks[0]["score"] if retrieved_chunks else 0.0
    if top_score < RETRIEVAL_THRESHOLD:
        res = INSUFFICIENT_EVIDENCE_REFUSAL.copy()
        res["verification_status"] = [{"chunk_id": "none", "status": f"score ({top_score:.4f}) below threshold", "passed": True}]
        return res

    # Context construction
    context = "\n\n---\n\n".join([
        f"[chunk_id: {c['chunk_id']} | document: {c['document']} | section: {c['section']} | page: {c['page']}]\n{c['text']}"
        for c in retrieved_chunks
    ])
    user_prompt = f"Evidence:\n{context}\n\nQuestion: {query}\n\nThe response is the JSON object described in the system rules, with no additional text."

    # Gate 3: Constrained JSON generation via Groq
    response = groq_client.chat.completions.create(
        model=model,
        temperature=0.0,
        max_tokens=1200,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": GROUNDING_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    
    raw = response.choices[0].message.content
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "recommendation": "Internal error: Generation output was not valid JSON.",
            "evidence": "",
            "citations": [],
            "confidence": "insufficient",
            "verification_status": [{"chunk_id": "none", "status": "json_decode_error", "passed": False}]
        }

    # Gate 4: Citation verification
    verification = verify_citations(parsed, retrieved_chunks)
    
    # If any citation was fabricated, mark confidence as insufficient
    if any(not v["passed"] for v in verification):
        parsed["confidence"] = "insufficient"
        
    parsed["verification_status"] = verification
    return parsed
