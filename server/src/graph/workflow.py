from typing import Literal,Optional,List, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from src.agents.detector_agent import detector_agent
from src.agents.verifier_agent import verifier_agent,VerificationResult

from .state import (
    VerificationState, 
    should_continue_execution, 
    set_detection_result, 
    set_verification_result
)

def detect_claim(state: VerificationState) -> VerificationState:
    """Node that performs claim detection and structuring."""
    claim = state["claim"]
    
    try:
        detection_result = detector_agent.detect(claim)
        updated_state = set_detection_result(state, detection_result)
        return {
            **updated_state,
            "should_continue": True,
            "next_node": "verify"
        }
    except Exception as e:
        return {
            **state,
            "should_continue": False,
            "verification_result": None,
            "messages": state["messages"] + [{
                "role": "system",
                "content": f"Detection failed with error: {str(e)}"
            }]
        }

def verify_claim(state: VerificationState) -> VerificationState:
    """Node that performs comprehensive claim verification."""
    detection_result = state.get("detection_result")
    
    try:
        verification_result = verifier_agent.verify_claim(
            state["claim"],
            detection=detection_result
        )
        
        updated_state = set_verification_result(state, verification_result)
        
        return {
            **updated_state,
            "should_continue": False,  # Verification is complete
            "retrieved_evidence": verification_result.evidence
        }
    except Exception as e:
        return {
            **state,
            "should_continue": False,
            "verification_result": None,
            "messages": state["messages"] + [{
                "role": "system",
                "content": f"Verification failed with error: {str(e)}"
            }]
        }

def should_verify(state: VerificationState) -> Literal["verify", END]:
    """Conditional edge that determines whether verification should proceed."""
    if state.get("detection_result") is None:
        return "detect"
    
    # If detection has been performed, proceed to verification
    return "verify"

def verification_complete(state: VerificationState) -> Literal["end", "__end__"]:
    """Final decision node after verification is complete."""
    return END

def create_verification_workflow():
    """Create and configure the verification workflow graph."""
    
    # Define the workflow as a state graph
    workflow = StateGraph(VerificationState)
    
    # Add nodes to the workflow
    workflow.add_node("detect", detect_claim)
    workflow.add_node("verify", verify_claim)
    
    # Define the entry point
    workflow.set_entry_point("detect")
    
    # Define conditional edges
    workflow.add_conditional_edges(
        "detect",
        should_verify,
        {
            "detect": "detect",  # If no detection result, go back to detect
            "verify": "verify"
        }
    )
    
    # After verification is complete, end the workflow
    workflow.add_edge("verify", END)
    
    # Compile the workflow into a runnable graph
    verification_graph = workflow.compile()
    
    return verification_graph

def run_verification_workflow(
    claim: str, 
    user_id: Optional[str] = None,
    verification_id: Optional[str] = None
) -> VerificationState:
    """Execute the complete verification workflow."""
    
    initial_state: VerificationState = {
        "claim": claim,
        "user_id": user_id,
        "detection_result": None,
        "verification_result": None,
        "should_continue": True,
        "next_node": None,
        "messages": [],
        "verification_id": verification_id,
        "timestamp": None,
        "search_queries": None,
        "retrieved_evidence": None,
        "evidence_analysis": None
    }
    
    # Create and execute the workflow
    verification_graph = create_verification_workflow()
    
    try:
        final_state = verification_graph.invoke(initial_state)
        return final_state
    except Exception as e:
        # In case of workflow execution error, return error state
        error_state = {
            **initial_state,
            "verification_result": None,
            "should_continue": False,
            "messages": initial_state["messages"] + [{
                "role": "system",
                "content": f"Workflow execution failed with error: {str(e)}"
            }]
        }
        return error_state

# Optional: Workflow utilities

def extract_verification_result(state: VerificationState) -> Optional[VerificationResult]:
    """Extract the verification result from the workflow state."""
    return state.get("verification_result")

def is_verification_successful(state: VerificationState) -> bool:
    """Check if the verification workflow completed successfully."""
    verification_result = state.get("verification_result")
    return verification_result is not None

def get_workflow_messages(state: VerificationState) -> List[Dict[str, Any]]:
    """Extract all messages generated during workflow execution."""
    return state.get("messages", [])

def create_verification_response(state: VerificationState) -> Dict:
    """Create a standardized response from the workflow state."""
    verification_result = state.get("verification_result")
    
    if verification_result is None:
        return {
            "success": False,
            "message": "Verification failed to complete",
            "messages": get_workflow_messages(state)
        }
    
    return {
        "success": True,
        "verification_result": verification_result.model_dump(),
        "messages": get_workflow_messages(state),
        "evidence": [evidence.model_dump() for evidence in state.get("retrieved_evidence", [])]
    }