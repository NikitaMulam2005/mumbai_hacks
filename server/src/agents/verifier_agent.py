# src/agents/verifier_agent.py
"""NATIONAL-LEVEL Professional Fact-Checker — Works for ALL India (2025 Ready)"""

from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import List, Literal, Optional
import re
from loguru import logger

from config import GROQ_API_KEY
from src.rag.vectorstore.faiss_manager import faiss_manager
from src.utils.rss_parser import rss_parser
from groq import Groq

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

VerdictLabel = Literal["true", "false", "unverified", "mixed"]


@dataclass
class EvidenceItem:
    title: str
    url: str = ""
    summary: str = ""
    stance: Literal["support", "refute", "neutral"] = "neutral"
    published: Optional[str] = None
    source_domain: Optional[str] = None
    origin: Literal["dataset", "rss"] = "dataset"


@dataclass
class VerificationResult:
    claim: str
    verdict: VerdictLabel
    confidence: float
    rationale: str
    evidence: List[EvidenceItem] = field(default_factory=list)

    def model_dump(self) -> dict:
        return {**asdict(self), "evidence": [asdict(e) for e in self.evidence]}


class VerifierAgent:
    def verify_claim(self, claim: str) -> VerificationResult:
        logger.info(f"Verifying (India-wide): {claim}")
        evidence = []
        seen = set()

        # DYNAMIC, SMART SEARCH QUERIES — works for any Indian state, board, or event
        base_queries = [
            claim,
            claim + " official",
            claim + " government announcement",
            claim + " 2025",
            claim + " latest update"
        ]

        # Add context-specific queries based on keywords
        claim_lower = claim.lower()
        extra_queries = []

        if any(state in claim_lower for state in ["delhi", "up", "uttar pradesh", "maharashtra", "bihar", "tamil nadu", "kerala", "gujarat", "rajasthan"]):
            extra_queries.extend([
                f"{claim} school holiday calendar 2025-26",
                f"{claim} education department circular"
            ])

        if "cbse" in claim_lower:
            extra_queries.extend(["CBSE official circular", "CBSE datesheet 2026", "cbseacademic.nic.in"])
        if "up board" in claim_lower or "upmsp" in claim_lower:
            extra_queries.append("UP Board official announcement 2025-26")
        if "neet" in claim_lower or "jee" in claim_lower:
            extra_queries.append("NTA official notification")

        all_queries = base_queries + extra_queries

        # Search FAISS deeply
        for query in all_queries:
            try:
                results = faiss_manager.vectorstore.similarity_search_with_score(query, k=50)
                for doc, score in results:
                    url = doc.metadata.get("url", "")
                    title = doc.metadata.get("title", "")
                    key = url or title
                    if key in seen or score > 0.90:
                        continue
                    seen.add(key)
                    evidence.append(EvidenceItem(
                        title=title,
                        url=url,
                        summary=doc.page_content[:1800],
                        stance="neutral",
                        published=doc.metadata.get("published") or doc.metadata.get("date"),
                        source_domain=url.split("/")[2] if url else None,
                        origin="dataset"
                    ))
            except Exception as e:
                logger.debug(f"FAISS search error: {e}")

        # Add fresh RSS news (critical for breaking updates)
        try:
            for doc in rss_parser.fetch_recent(days=120, max_per_feed=30):
                url = doc.metadata.get("url", "")
                if url in seen:
                    continue
                seen.add(url)
                evidence.append(EvidenceItem(
                    title=doc.metadata.get("title", "News"),
                    url=url,
                    summary=doc.page_content[:1800],
                    stance="neutral",
                    published=doc.metadata.get("published"),
                    origin="rss"
                ))
        except Exception as e:
            logger.warning(f"RSS failed: {e}")

        # Build professional evidence summary
        evidence_text = "\n\n".join([
            f"[{i+1}] {e.source_domain or 'News'} | {e.published or 'Recent'}\n"
            f"{e.title}\n"
            f"{e.summary[:1100].strip()}"
            for i, e in enumerate(evidence[:20])
        ]) if evidence else "No credible sources found."

        # PROFESSIONAL, NEUTRAL, NATION-WIDE PROMPT
        prompt = f"""You are India's top fact-checking AI. Current date: November 29, 2025.

CLAIM:
"{claim}"

EVIDENCE FROM OFFICIAL GOVT SOURCES, NEWS, AND KNOWLEDGE BASE:
{evidence_text}

INSTRUCTIONS:
- Use only the evidence above + your knowledge up to November 2025.
- Trust official domains: gov.in, nic.in, cbse.gov.in, nta.ac.in, pib.gov.in
- Be accurate for all states: Delhi, UP, Bihar, Maharashtra, Tamil Nadu, etc.
- Do not assume — only conclude if evidence confirms.

Answer EXACTLY in this format:

VERDICT: TRUE / FALSE / MIXED
CONFIDENCE: 0.XX
REASON: One clear, professional sentence.
"""

        if not groq_client:
            verdict = "unverified"
            confidence = 0.3
            reason = "Verification service unavailable"
        else:
            try:
                resp = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                    max_tokens=130,
                    timeout=20
                )
                output = resp.choices[0].message.content.strip()

                v = re.search(r"VERDICT:\s*(TRUE|FALSE|MIXED)", output, re.I)
                c = re.search(r"CONFIDENCE:\s*([0-9]*\.?[0-9]+)", output)
                r = re.search(r"REASON:\s*(.+)", output, re.DOTALL)

                verdict = v.group(1).lower() if v else "unverified"
                confidence = float(c.group(1)) if c else 0.5
                reason = r.group(1).strip() if r else "Analysis completed"

            except Exception as e:
                logger.error(f"Groq error: {e}")
                verdict, confidence, reason = "unverified", 0.3, "Service error"

        logger.success(f"VERDICT: {verdict.upper()} ({confidence:.3f}) → {claim[:60]}...")

        return VerificationResult(
            claim=claim,
            verdict=verdict,
            confidence=round(confidence, 3),
            rationale=reason,
            evidence=evidence[:20]
        )


# Global instance
verifier_agent = VerifierAgent()