import json
import os
import re
import azure.functions as func
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from groq import Groq

# Configuration
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "https://creativa-hackathon-vb.search.windows.net")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY", "")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX", "creativa-hackathon-pc")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

GROUNDING_SYSTEM_PROMPT = """You are a citation-bound clinical evidence assistant for sickle cell disease. Your purpose is to synthesize evidence-based clinical guidance strictly and exclusively from the provided guideline passages.

Rules:
1. Strict Context Grounding: Answer ONLY using the evidence passages provided in the prompt. Do not use outside medical knowledge.
2. Claim-to-Evidence Parity: Every clinical statement in "recommendation" must be directly traceable to and supported by the text in "evidence".
3. Zero Citation Fabrication: Never invent chunk_ids or document names. Citations must reference chunks physically present in the evidence.
4. Output Schema: Return your response strictly as a JSON object matching this schema:
   {
     "recommendation": "Markdown-formatted clinical synthesis (using structured headings, bullet points, protocol criteria, or comparative tables when appropriate)",
     "evidence": "Verbatim or tightly summarized supporting passage(s) extracted from the retrieved text",
     "citations": [
       {
         "document": "Document identifier or title",
         "section": "Section name",
         "page": 1,
         "chunk_id": "exact chunk_id from evidence"
       }
     ],
     "confidence": "high" | "medium" | "low" | "insufficient"
   }

Safety Rules:
5. Absolute Prohibition on Individualized Medical Advice: Do not diagnose, prescribe, calculate custom dosages, or recommend individualized regimens for a specific patient.
6. Treatment of Patient-Specific Prompts: If a question supplies individual clinical parameters (e.g. "What dose should I give my 12-year-old?"), REFUSE immediately. Set confidence to "insufficient", evidence to "", citations to [].
7. General guideline criteria, trial thresholds (e.g., ">= 3 VOCs in 12 months"), and standard starting dose ranges (e.g., "15–20 mg/kg/day per protocol") MAY be presented strictly as general guideline standards.
"""

PATIENT_SPECIFIC_PATTERNS = [
    r"\b(my|i am|i'm|he is|she is|patient is)\b.*\b(years old|yo|months old)\b",
    r"\b(what|which)\s+(dose|dosage|amount|medication|medicine)\s+(should|can|do)\s+(i|we|my|he|she)\s+(take|give|use)\b",
    r"\b(should|can)\s+(i|we|my child|my son|my daughter|he|she)\s+(take|give|use|start|stop)\b",
    r"\b(what should i give (my|for my|to my) (child|son|daughter|kid|baby))\b",
    r"\b(diagnose|prescribe|calculate dose)\b",
    r"\b(weight|weighs|kg|lbs)\s*[:=]?\s*\d+",
    r"\b(creatinine|hemoglobin|hb|hgb|wbc|platelet|gfr|alt|ast)\s*[:=]?\s*\d+",
]

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Content-Type": "application/json"
}

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

def is_patient_specific(query: str) -> bool:
    normalized = query.lower().strip()
    for pattern in PATIENT_SPECIFIC_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return True
    return False

@app.route(route="health", methods=["GET", "OPTIONS"])
def health_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=CORS_HEADERS)
    
    payload = {
        "status": "healthy",
        "model": GROQ_MODEL,
        "index": AZURE_SEARCH_INDEX,
        "runtime": "Azure Function Serverless (v4/Python)"
    }
    return func.HttpResponse(json.dumps(payload), status_code=200, headers=CORS_HEADERS)

@app.route(route="query", methods=["POST", "OPTIONS"])
def query_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "OPTIONS":
        return func.HttpResponse(status_code=204, headers=CORS_HEADERS)

    try:
        req_body = req.get_json()
        query = req_body.get("query", "").strip()
        top_k = int(req_body.get("top_k", 7))
        
        if not query:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'query' field in request body"}),
                status_code=400,
                headers=CORS_HEADERS
            )

        # 1. Check Patient Safety Gate
        if is_patient_specific(query):
            refusal = {
                "query": query,
                "recommendation": (
                    "**Clinical Boundary Notice:** This system provides population-level guideline evidence "
                    "and is prohibited from providing patient-specific medical advice or individualized dosing regimens. "
                    "For patient management decisions, please consult ASH / NHLBI guideline protocols or a licensed hematologist."
                ),
                "evidence": "",
                "citations": [],
                "confidence": "insufficient",
                "verification_status": [{"chunk_id": "none", "status": "blocked by patient safety gate", "passed": True}]
            }
            return func.HttpResponse(json.dumps(refusal), status_code=200, headers=CORS_HEADERS)

        # 2. Retrieve Evidence from Azure AI Search
        search_client = SearchClient(
            endpoint=AZURE_SEARCH_ENDPOINT,
            index_name=AZURE_SEARCH_INDEX,
            credential=AzureKeyCredential(AZURE_SEARCH_KEY)
        )
        
        search_results = search_client.search(
            search_text=query,
            select=["chunk_id", "document_id", "title", "citation", "section", "page_number", "content"],
            top=top_k
        )

        chunks = []
        for r in search_results:
            chunks.append({
                "chunk_id": str(r.get("chunk_id", f"chunk_{len(chunks)}")),
                "document": str(r.get("document_id", "SCD Guideline")),
                "title": str(r.get("title", "")),
                "citation": str(r.get("citation", "ASH / NHLBI Guidelines")),
                "section": str(r.get("section", "Clinical Protocols")),
                "page": int(r.get("page_number", 1) or 1),
                "text": str(r.get("content", "")),
                "score": float(r.get("@search.score", 1.0))
            })

        if not chunks:
            insufficient = {
                "query": query,
                "recommendation": "No matching clinical evidence was found in the indexed guidelines for this query.",
                "evidence": "",
                "citations": [],
                "confidence": "insufficient",
                "verification_status": []
            }
            return func.HttpResponse(json.dumps(insufficient), status_code=200, headers=CORS_HEADERS)

        # 3. Formulate LLM Prompt & Run Groq
        context = "\n\n---\n\n".join([
            f"[chunk_id: {c['chunk_id']} | document: {c['document']} | section: {c['section']} | page: {c['page']}]\n{c['text']}"
            for c in chunks
        ])
        user_prompt = f"Evidence:\n{context}\n\nQuestion: {query}\n\nReturn ONLY the JSON object described in system rules."

        groq_client = Groq(api_key=GROQ_API_KEY)
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            temperature=0.0,
            max_tokens=1200,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": GROUNDING_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        raw_content = response.choices[0].message.content
        parsed = json.loads(raw_content)
        
        # 4. Verify Citations
        evidence_by_id = {e["chunk_id"]: e for e in chunks}
        verification = []
        for c in parsed.get("citations", []):
            cid = c.get("chunk_id")
            if cid in evidence_by_id:
                verification.append({"chunk_id": cid, "status": "passed", "passed": True})
            else:
                verification.append({"chunk_id": cid or "unknown", "status": "unverified", "passed": False})
        
        result_payload = {
            "query": query,
            "recommendation": parsed.get("recommendation", ""),
            "evidence": parsed.get("evidence", ""),
            "citations": parsed.get("citations", []),
            "confidence": parsed.get("confidence", "medium"),
            "verification_status": verification
        }
        return func.HttpResponse(json.dumps(result_payload), status_code=200, headers=CORS_HEADERS)

    except Exception as e:
        error_payload = {
            "query": req_body.get("query", "") if 'req_body' in locals() else "",
            "recommendation": f"Error processing clinical query: {str(e)}",
            "evidence": "",
            "citations": [],
            "confidence": "insufficient",
            "verification_status": []
        }
        return func.HttpResponse(json.dumps(error_payload), status_code=500, headers=CORS_HEADERS)
