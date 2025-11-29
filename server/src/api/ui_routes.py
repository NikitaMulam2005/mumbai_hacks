# src/api/routes.py
import json
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from loguru import logger

from src.agents.verifier_agent import verifier_agent

router = APIRouter()

# === PERSISTENCE: Save claims to JSON file ===
CLAIMS_DB_PATH = Path("data") / "verified_claims.json"
CLAIMS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Load existing claims on startup
def load_claims() -> List[dict]:
    if CLAIMS_DB_PATH.exists():
        try:
            with open(CLAIMS_DB_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as e:
            logger.warning(f"Failed to load claims DB: {e}. Starting fresh.")
    return []

def save_claims(claims: List[dict]):
    try:
        with open(CLAIMS_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(claims, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to save claims to disk: {e}")

# Global in-memory store (persisted to disk)
VERIFIED_CLAIMS = load_claims()


# === Models ===
class VerifyRequest(BaseModel):
    claim: str


class EvidenceSource(BaseModel):
    title: str
    url: Optional[str] = None
    stance: str = "Neutral"
    published: Optional[str] = None
    similarity: Optional[float] = None


class VerifyResponse(BaseModel):
    claim: str
    verdict: str
    confidence: float
    rationale: str
    category: str = "General"
    evidence: List[EvidenceSource] = []
    sources_count: int
    consistency_score: float
    verified_at: str
    verified_by: str = "TruthPulse Engine"


# === ROUTES ===

@router.post("/verify", response_model=VerifyResponse)
async def verify_claim(request: VerifyRequest):
    claim_text = request.claim.strip()
    
    if len(claim_text) < 10:
        raise HTTPException(status_code=400, detail="Claim too short (min 10 characters).")
    if len(claim_text) > 2000:
        raise HTTPException(status_code=400, detail="Claim too long (max 2000 characters).")

    logger.info(f"Verifying: {claim_text[:120]}{'...' if len(claim_text) > 120 else ''}")

    try:
        result = verifier_agent.verify_claim(claim_text)

        # Safely extract category — avoids AttributeError if structured_claim is missing
        category = "General"
        if hasattr(result, "structured_claim") and result.structured_claim:
            category = getattr(result.structured_claim, "domain", "General")
        elif hasattr(result, "category"):
            category = result.category
        # Optional: simple keyword-based fallback
        elif any(word in claim_text.lower() for word in ["school", "education", "exam", "student"]):
            category = "Education"
        elif any(word in claim_text.lower() for word in ["election", "modi", "rahul", "bjp", "congress"]):
            category = "Politics"

        response = VerifyResponse(
            claim=getattr(result, "claim", claim_text),
            verdict=result.verdict.upper() if hasattr(result, "verdict") else "UNKNOWN",
            confidence=round(float(result.confidence), 3) if hasattr(result, "confidence") else 0.5,
            rationale=getattr(result, "rationale", "No rationale provided."),
            category=category,
            evidence=[
                EvidenceSource(
                    title=ev.title or "Untitled Source",
                    url=ev.url,
                    stance=(ev.stance or "neutral").capitalize(),
                    published=ev.published,
                    similarity=round(ev.similarity, 3) if hasattr(ev, "similarity") and ev.similarity is not None else None
                )
                for ev in (result.evidence[:10] if hasattr(result, "evidence") else [])
            ],
            sources_count=len(result.evidence) if hasattr(result, "evidence") else 0,
            consistency_score=round(float(getattr(result, "consistency_score", 0.0)), 3),
            verified_at=datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            verified_by="TruthPulse Engine v2"
        )

        # === SAVE TO DATABASE (memory + disk) ===
        claim_record = response.model_dump()
        claim_record["id"] = len(VERIFIED_CLAIMS) + 1
        claim_record["original_claim"] = claim_text
        claim_record["saved_at"] = datetime.utcnow().isoformat() + "Z"
        
        VERIFIED_CLAIMS.append(claim_record)
        save_claims(VERIFIED_CLAIMS)

        logger.success(f"VERDICT: {response.verdict} (confidence: {response.confidence}) | Saved as ID {claim_record['id']}")

        return response

    except Exception as e:
        logger.error(f"Verification failed: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Verification engine error. Please try again later."
        )


# === Get all saved claims (for Analytics Dashboard) ===
@router.get("/claims")
async def get_all_claims(
    limit: int = 100,
    skip: int = 0,
    verdict: Optional[str] = None
):
    filtered = VERIFIED_CLAIMS.copy()

    if verdict:
        verdict_lower = verdict.strip().lower()
        filtered = [c for c in filtered if c.get("verdict", "").lower() == verdict_lower]

    total = len(filtered)
    claims = filtered[skip:skip + limit]

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total,
        "claims": claims
    }


# === Get single claim by ID ===
@router.get("/claims/{claim_id}")
async def get_claim_by_id(claim_id: int):
    for claim in VERIFIED_CLAIMS:
        if claim.get("id") == claim_id:
            return claim
    raise HTTPException(status_code=404, detail="Claim not found")


# === Health check ===
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_verified_claims": len(VERIFIED_CLAIMS)
    }