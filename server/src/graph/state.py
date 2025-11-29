from typing import TypedDict, Annotated, List, Optional, Dict, Any
from dataclasses import dataclass
from typing_extensions import TypedDict

from src.agents.detector_agent import DetectionResult
from src.agents.verifier_agent import VerificationResult, EvidenceItem

class VerificationState(TypedDict):
    """State object that is passed between nodes in the verification workflow."""
    
    # Input data
    claim: str
    user_id: Optional[str]
    
    # Intermediate results
    detection_result: Optional[DetectionResult]
    verification_result: Optional[VerificationResult]
    
    # Workflow control
    should_continue: bool
    next_node: Optional[str]
    
    # Additional metadata
    messages: Annotated[List[Dict[str, Any]], "append"]
    verification_id: Optional[str]
    timestamp: Optional[str]
    
    # Cache and intermediate data
    search_queries: Optional[List[str]]
    retrieved_evidence: Optional[List[EvidenceItem]]
    evidence_analysis: Optional[Dict[str, Any]]

@dataclass
class AgentState:
    """State specifically for agent execution within the workflow."""
    claim: str
    detection_result: Optional[DetectionResult] = None
    verification_result: Optional[VerificationResult] = None
    retrieved_documents: List[EvidenceItem] = None
    intermediate_results: Dict[str, Any] = None

def update_messages(state: VerificationState, message: Dict[str, Any]) -> VerificationState:
    """Helper function to append messages to the state."""
    return {
        **state,
        "messages": state["messages"] + [message]
    }

def set_detection_result(state: VerificationState, detection_result: DetectionResult) -> VerificationState:
    """Helper function to set the detection result in state."""
    return {
        **state,
        "detection_result": detection_result,
        "search_queries": detection_result.search_queries if detection_result else None
    }

def set_verification_result(state: VerificationState, verification_result: VerificationResult) -> VerificationState:
    """Helper function to set the verification result in state."""
    return {
        **state,
        "verification_result": verification_result
    }

def should_continue_execution(state: VerificationState) -> bool:
    """Determine whether the workflow should continue to the next node."""
    return state.get("should_continue", True)