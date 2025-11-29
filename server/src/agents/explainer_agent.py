"""Explainer Agent – generates plain-language reasoning based on verification results."""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import pyttsx3
import threading
from loguru import logger
from src.agents.detector_agent import DetectionResult
from src.agents.verifier_agent import VerificationResult, EvidenceItem

@dataclass
class ExplanationResult:
    """Structured explanation output for downstream agents/UI."""
    verdict: str
    explanation: str
    key_points: List[str]
    sources_summary: str
    confidence_note: str

    def model_dump(self) -> Dict:
        return asdict(self)

class VoiceManager:
    """Manages voice output to prevent overlap between multiple agents."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        try:
            self.tts_engine = pyttsx3.init()
            self.is_speaking = False
            self._initialized = True
        except Exception:
            self.tts_engine = None
            self.is_speaking = False

    def speak(self, text: str, agent_name: str) -> bool:
        """Attempt to speak the given text. Returns True if speaking was started."""
        if self.tts_engine is None:
            return False

        if self.is_speaking:
            return False

        self.is_speaking = True
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        finally:
            self.is_speaking = False

    def can_speak(self) -> bool:
        """Check if speech can be initiated."""
        return not self.is_speaking

class ExplainerAgent:
    """Converts technical verification results into plain-language explanations."""

    def __init__(self):
        self.voice_manager = VoiceManager()

    def explain(self, verification: VerificationResult, detection: Optional[DetectionResult] = None) -> ExplanationResult:
        """Generate human-friendly explanation from verification results using exact specified phrasing."""
        explanation = self._build_explanation(verification, detection)
        key_points = self._extract_key_points(verification)
        sources_summary = self._summarize_sources(verification)
        confidence_note = self._build_confidence_note(verification.confidence)

        result = ExplanationResult(
            verdict=verification.verdict,
            explanation=explanation,
            key_points=key_points,
            sources_summary=sources_summary,
            confidence_note=confidence_note,
        )
        return result

    def speak_explanation(self, explanation_result: ExplanationResult) -> bool:
        """Speak the explanation without overlapping other voice output."""
        return self.voice_manager.speak(explanation_result.explanation, "explainer")

    def _build_explanation(self, verification: VerificationResult, detection: Optional[DetectionResult]) -> str:
        """Generate explanation using the exact specified phrasing."""
        verdict = verification.verdict
        
        if verdict == "true":
            return "This claim is correct according to verified sources."
        elif verdict == "false":
            return "This claim is false. Verified sources show no evidence supporting it."
        else:  # unverified
            return "No reliable information found; be cautious."

    def _extract_key_points(self, verification: VerificationResult) -> List[str]:
        """Extract key points from evidence."""
        points = []
        rss_sources = [e.source or e.title for e in verification.evidence if e.origin == "rss" and e.reliable]
        
        if rss_sources:
            points.append(f"Verified sources: {', '.join(rss_sources)}")
        
        # Add evidence counts
        dataset_count = sum(1 for e in verification.evidence if e.origin == "dataset")
        rss_count = sum(1 for e in verification.evidence if e.origin == "rss")
        fact_check_count = sum(1 for e in verification.evidence if e.origin == "fact_check")
        
        if dataset_count > 0:
            points.append(f"Checked {dataset_count} historical records")
        if rss_count > 0:
            points.append(f"Reviewed {rss_count} recent official updates")
        if fact_check_count > 0:
            points.append(f"Examined {fact_check_count} fact-checking reports")
        
        return points[:4]

    def _summarize_sources(self, verification: VerificationResult) -> str:
        """Summarize the verified sources, focusing on RSS sources."""
        rss_sources = [e.source or e.title for e in verification.evidence if e.origin == "rss" and e.reliable]
        
        if not rss_sources:
            return "No verified sources available"
        
        if len(rss_sources) == 1:
            return f"Verified by: {rss_sources[0]}"
        elif len(rss_sources) == 2:
            return f"Verified by: {rss_sources[0]} and {rss_sources[1]}"
        else:
            return f"Verified by: {', '.join(rss_sources[:-1])}, and {rss_sources[-1]}"

    def _build_confidence_note(self, confidence: float) -> str:
        """Build confidence note based on confidence level."""
        if confidence >= 0.8:
            return "High confidence - multiple reliable sources agree"
        elif confidence >= 0.6:
            return "Moderate confidence - sources generally agree"
        elif confidence >= 0.4:
            return "Low confidence - limited evidence available"
        else:
            return "Very low confidence - insufficient evidence"

# Singleton instance
explainer_agent = ExplainerAgent()