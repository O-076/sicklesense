import re

PATIENT_SPECIFIC_PATTERNS = [
    r'\bmy (son|daughter|child|wife|husband|patient|father|mother)\b',
    r'\bi (have|am|take|was diagnosed)\b',
    r'\bshould i (take|give|start|stop)\b',
    r'\bwhat dose should i\b',
    r'\bcan i give\b',
    r'\bis it safe for me\b',
]

PATIENT_SAFETY_REFUSAL = {
    "recommendation": (
        "I can't provide individualized dosing or treatment instructions for a specific patient. "
        "The appropriate approach should be determined by a qualified clinician using the patient's clinical assessment."
    ),
    "evidence": "",
    "citations": [],
    "confidence": "insufficient",
}

INSUFFICIENT_EVIDENCE_REFUSAL = {
    "recommendation": (
        "The indexed guidelines do not appear to cover this topic with enough confidence for an answer. "
        "Rephrasing may help, or the topic may fall outside the indexed evidence scope."
    ),
    "evidence": "",
    "citations": [],
    "confidence": "insufficient",
}

def is_patient_specific(question: str) -> bool:
    """Checks for patient-specific phrases to trigger the safety gate."""
    lowered = question.lower()
    return any(re.search(p, lowered) for p in PATIENT_SPECIFIC_PATTERNS)
