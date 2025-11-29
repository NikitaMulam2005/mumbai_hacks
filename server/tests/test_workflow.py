import sys
import os
from datetime import datetime

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.graph.workflow import (
    run_verification_workflow, 
    extract_verification_result
)
from src.agents.explainer_agent import explainer_agent
from src.agents.communicator_agent import communicator_agent

def test_workflow_complete_pipeline(claim, audience="general"):
    """Test the complete verification pipeline using the graph workflow."""
    
    print(f"Testing claim through complete workflow: {claim}")
    print("=" * 80)
    
    # Execute the complete workflow through the graph
    start_time = datetime.now()
    final_state = run_verification_workflow(claim)
    end_time = datetime.now()
    
    print(f"Workflow execution time: {end_time - start_time}")
    print()
    
    # Extract and display results
    verification_result = extract_verification_result(final_state)
    
    if verification_result is None:
        print("ERROR: Verification failed to complete.")
        messages = final_state.get("messages", [])
        if messages:
            print("Workflow messages:")
            for message in messages:
                print(f"  {message.get('role', 'unknown')}: {message.get('content', 'No content')}")
        return None
    
    print(f"VERDICT: {verification_result.verdict}")
    print(f"CONFIDENCE: {verification_result.confidence:.2f}")
    print(f"EVIDENCE ITEMS: {len(verification_result.evidence)}")
    
    # Generate explanation using the explainer agent
    detection_result = final_state.get("detection_result")
    explanation_result = explainer_agent.explain(verification_result, detection_result)
    
    print("\nEXPLANATION:")
    print(f"{explanation_result.explanation}")
    print(f"\nSOURCES: {explanation_result.sources_summary}")
    
    print("\nKEY POINTS:")
    for i, point in enumerate(explanation_result.key_points, 1):
        print(f"  {i}. {point}")
    
    print(f"\nCONFIDENCE NOTE: {explanation_result.confidence_note}")
    
    # Generate audience-tailored communication
    tailored_explanation = communicator_agent.communicate(verification_result, audience)
    
    print(f"\nCOMMUNICATION FOR {audience.upper()} AUDIENCE:")
    print(f"SIMPLE SUMMARY: {tailored_explanation.simple_summary}")
    print(f"VERDICT EXPLANATION: {tailored_explanation.verdict_explanation}")
    
    return {
        "final_state": final_state,
        "verification_result": verification_result,
        "explanation_result": explanation_result,
        "tailored_explanation": tailored_explanation
    }

def run_test_suite():
    """Run a comprehensive test suite using the workflow."""
    
    test_claims = [
        "Mumbai Airport flights have been cancelled due to security threat.",
        "All schools in Delhi have been closed for the next two weeks.",
        "India has reported 500 new cases of a deadly new virus variant.",
        "There is currently a massive power outage across entire Mumbai city.",
        "Stock market has crashed by 15% today due to global recession fears."
    ]
    
    print("=== Verification Workflow Test Suite ===\n")
    
    successful_tests = 0
    
    for i, claim in enumerate(test_claims, 1):
        print(f"\nTEST CASE {i}:")
        print(f"Claim: {claim}")
        print("-" * 80)
        
        result = test_workflow_complete_pipeline(claim)
        if result is not None:
            successful_tests += 1
        
        print("\n" + "=" * 80)
    
    print(f"\nTest suite completed. Successfully processed {successful_tests} out of {len(test_claims)} claims.")

def test_single_claim(claim):
    """Test a single specific claim through the complete workflow."""
    return test_workflow_complete_pipeline(claim)

def test_different_audiences(claim):
    """Test the same claim with different audience types."""
    
    print(f"Testing claim with different audiences: {claim}")
    print("=" * 80)
    
    final_state = run_verification_workflow(claim)
    verification_result = extract_verification_result(final_state)
    
    if verification_result is None:
        print("Verification failed to produce a result.")
        return
    
    audiences = ["general", "kids", "elderly", "expert"]
    
    for audience in audiences:
        print(f"\nCommunication for {audience} audience:")
        print("-" * 40)
        tailored_explanation = communicator_agent.communicate(verification_result, audience)
        print(f"Simple Summary: {tailored_explanation.simple_summary}")
        print(f"Confidence Level: {tailored_explanation.confidence_level}")
        print(f"Explanation: {tailored_explanation.explanation[:200]}...")
        print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Allow testing a single claim via command line argument
        if sys.argv[1] == "single":
            if len(sys.argv) > 2:
                claim_to_test = " ".join(sys.argv[2:])
                print(f"Testing single claim: {claim_to_test}")
                test_single_claim(claim_to_test)
            else:
                print("Usage: python test_workflow.py single \"your claim here\"")
        elif sys.argv[1] == "audiences":
            if len(sys.argv) > 2:
                claim_to_test = " ".join(sys.argv[2:])
                test_different_audiences(claim_to_test)
            else:
                print("Usage: python test_workflow.py audiences \"your claim here\"")
        else:
            # Treat the argument as a single claim to test
            test_single_claim(" ".join(sys.argv[1:]))
    else:
        # Default behavior: run the comprehensive test suite
        run_test_suite()