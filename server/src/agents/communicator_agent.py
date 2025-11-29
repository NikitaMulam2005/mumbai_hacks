"""Communicator Agent - Tailors verification results into audience-appropriate explanations."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal
import pyttsx3
from src.agents.verifier_agent import VerificationResult
from loguru import logger

AudienceType = Literal["kids", "elderly", "general", "expert"]

@dataclass
class TailoredExplanation:
    """Structured explanation tailored for a specific audience."""
    audience: AudienceType
    explanation: str
    key_points: List[str]
    simple_summary: str
    confidence_level: str
    verdict_explanation: str

class CommunicatorAgent:
    """Agent that adapts verification results for different audiences with optional voice output."""
    
    def __init__(self):
        self.audience_strategies = {
            "kids": {
                "tone": "simple and friendly",
                "complexity": "very low",
                "confidence_descriptors": {"high": "very sure", "medium": "pretty sure", "low": "not completely sure"}
            },
            "elderly": {
                "tone": "clear and respectful",
                "complexity": "low",
                "confidence_descriptors": {"high": "very confident", "medium": "reasonably confident", "low": "less certain"}
            },
            "general": {
                "tone": "neutral and factual",
                "complexity": "moderate",
                "confidence_descriptors": {"high": "high confidence", "medium": "moderate confidence", "low": "low confidence"}
            },
            "expert": {
                "tone": "precise and technical",
                "complexity": "high",
                "confidence_descriptors": {"high": "high confidence", "medium": "moderate confidence", "low": "low confidence"}
            }
        }
        
        # Initialize TTS engine for optional voice output
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_available = True
            # Set default voice properties
            self.tts_engine.setProperty('rate', 180)
            self.tts_engine.setProperty('volume', 0.9)
        except Exception:
            self.tts_engine = None
            self.tts_available = False
            logger.warning("Text-to-speech engine not available")

    def communicate(self, verification_result: VerificationResult, audience: AudienceType = "general") -> TailoredExplanation:
        """Generate an audience-appropriate explanation of the verification result."""
        if audience not in self.audience_strategies:
            raise ValueError(f"Unsupported audience: {audience}")
        
        strategy = self.audience_strategies[audience]
        
        explanation = self._generate_explanation(verification_result, strategy)
        key_points = self._generate_key_points(verification_result)
        simple_summary = self._generate_simple_summary(verification_result, strategy)
        confidence_level = self._format_confidence(verification_result.confidence, strategy)
        verdict_explanation = self._generate_verdict_explanation(verification_result, strategy)
        
        return TailoredExplanation(
            audience=audience,
            explanation=explanation,
            key_points=key_points,
            simple_summary=simple_summary,
            confidence_level=confidence_level,
            verdict_explanation=verdict_explanation
        )

    def speak_explanation(self, explanation: TailoredExplanation, generate_audio_file: bool = False) -> Optional[str]:
        """Convert the tailored explanation to spoken audio."""
        if not self.tts_available:
            raise RuntimeError("Text-to-speech engine is not available")
        
        # Use simple summary for voice output as it's the most concise
        text_to_speak = explanation.simple_summary
        
        if generate_audio_file:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                audio_file_path = temp_file.name
                self.tts_engine.save_to_file(text_to_speak, audio_file_path)
                self.tts_engine.runAndWait()
                return audio_file_path
        else:
            # Direct playback
            self._configure_voice_for_audience(explanation.audience)
            self.tts_engine.say(text_to_speak)
            self.tts_engine.runAndWait()
            return None

    def _configure_voice_for_audience(self, audience: AudienceType):
        """Configure voice properties based on the target audience."""
        if not self.tts_available:
            return
        
        if audience == "kids":
            self.tts_engine.setProperty('rate', 200)  # Slightly faster and more engaging
        elif audience == "elderly":
            self.tts_engine.setProperty('rate', 140)  # Slower for better comprehension
        else:
            self.tts_engine.setProperty('rate', 180)  # Standard rate

    def _generate_explanation(self, result: VerificationResult, strategy: Dict) -> str:
        """Generate the main explanation tailored to the specified audience."""
        verdict = result.verdict
        
        if strategy["complexity"] == "very low":  # Kids
            explanations = {
                "true": "This information is true. People checked carefully and found proof that shows this really happened.",
                "false": "This information is not true. When people looked carefully, they found out that this is wrong.",
                "unverified": "We don't know yet if this information is true. There isn't enough information to be sure.",
                "mixed": "Some information says this is true, but other information says it is not true."
            }
        elif strategy["tone"] == "clear and respectful":  # Elderly
            explanations = {
                "true": "After careful examination, reliable sources have confirmed that this information is accurate.",
                "false": "After thorough investigation, reliable sources have determined that this information is incorrect.",
                "unverified": "There is currently not enough reliable information available to determine whether this information is true or false.",
                "mixed": "There is conflicting information available, with some sources supporting the claim and others contradicting it."
            }
        elif strategy["tone"] == "neutral and factual":  # General
            explanations = {
                "true": "The available evidence supports the claim and confirms its accuracy.",
                "false": "The available evidence contradicts the claim and shows it to be incorrect.",
                "unverified": "There is insufficient reliable evidence available to determine whether the claim is true or false.",
                "mixed": "There is substantial evidence both supporting and contradicting the claim."
            }
        else:  # Expert
            explanations = {
                "true": "The verification process has determined that the claim is supported by the available evidence.",
                "false": "The verification process has determined that the claim is contradicted by the available evidence.",
                "unverified": "There is insufficient corroborating evidence to establish the veracity of the claim.",
                "mixed": "The evidence base contains substantial contradictory information regarding the claim."
            }
        
        base_explanation = explanations.get(verdict, f"The claim has been evaluated and determined to be {verdict}.")
        return f"{base_explanation} {result.rationale}"

    def _generate_key_points(self, result: VerificationResult) -> List[str]:
        """Generate key points summarizing the verification result."""
        key_points = [f"The claim has been determined to be {result.verdict}."]
        
        supporting_count = len([e for e in result.evidence if e.stance == "support"])
        contradicting_count = len([e for e in result.evidence if e.stance == "refute"])
        
        if supporting_count > 0:
            evidence_summary = f"{supporting_count} source{'s' if supporting_count > 1 else ''} support this claim"
            if contradicting_count > 0:
                evidence_summary += f" and {contradicting_count} source{'s' if contradicting_count > 1 else ''} contradict it"
            key_points.append(evidence_summary)
        elif contradicting_count > 0:
            key_points.append(f"{contradicting_count} source{'s' if contradicting_count > 1 else ''} contradict this claim")
        else:
            key_points.append("No conclusive supporting or contradicting evidence was found")
        
        return key_points

    def _generate_simple_summary(self, result: VerificationResult, strategy: Dict) -> str:
        """Generate a concise, one-sentence summary."""
        summaries = {
            "true": "The claim has been verified as true.",
            "false": "The claim has been determined to be false.",
            "unverified": "There is not enough reliable evidence to verify the claim.",
            "mixed": "There is conflicting evidence both supporting and contradicting the claim."
        }
        return summaries.get(result.verdict, "The claim could not be conclusively verified.")

    def _format_confidence(self, confidence: float, strategy: Dict) -> str:
        """Format the confidence level appropriately for the audience."""
        descriptors = strategy["confidence_descriptors"]
        if confidence >= 0.8:
            return descriptors["high"]
        elif confidence >= 0.6:
            return descriptors["medium"]
        else:
            return descriptors["low"]

    def _generate_verdict_explanation(self, result: VerificationResult, strategy: Dict) -> str:
        """Generate a specific explanation of what the verdict means."""
        explanations = {
            "true": "This means the available evidence confirms that the information is accurate.",
            "false": "This means the available evidence shows that the information is incorrect.",
            "unverified": "This means there is not enough reliable evidence to determine whether the information is true or false.",
            "mixed": "This means there is reliable evidence both supporting and contradicting the information."
        }
        return explanations.get(result.verdict, "The determination about the accuracy of the information could not be conclusively established.")

# Create singleton instance
communicator_agent = CommunicatorAgent()

if __name__ == "__main__":
    # Example usage
    from src.verifier.verifier_agent import VerificationResult
    
    # Mock verification result for testing
    mock_result = VerificationResult(
        claim="The capital of France is Paris.",
        verdict="true",
        confidence=0.98,
        rationale="Multiple authoritative sources consistently identify Paris as the capital city of France.",
        evidence=[]
    )
    
    # Generate explanations for different audiences
    for audience in ["kids", "elderly", "general"]:
        explanation = communicator_agent.communicate(mock_result, audience)
        print(f"\n--- Explanation for {audience} audience ---")
        print(f"Simple Summary: {explanation.simple_summary}")
        print(f"Main Explanation: {explanation.explanation}")
        print("Key Points:")
        for point in explanation.key_points:
            print(f"  • {point}")
        print(f"Confidence Level: {explanation.confidence_level}")