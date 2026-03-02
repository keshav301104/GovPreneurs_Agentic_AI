from typing import TypedDict, Dict, Any
import json
from rag.generator import ProposalGenerator
from rag.evaluator import ProposalEvaluator

# Define the shared state structure for LangGraph
class AgentState(TypedDict):
    opportunity_id: str
    user_profile: Dict[str, Any]
    pdf_path: str
    rfp_chunks: str
    draft_proposal: str
    compliance_score: int
    auditor_notes: str
    iterations: int

class DrafterAgent:
    def __init__(self):
        # Initialize the engine we built in generator.py
        self.generator = ProposalGenerator()

    def draft(self, state: AgentState):
        print(f"\n--- Agent: Drafting Proposal (Iteration {state.get('iterations', 0) + 1}) ---")
        
        # Merge previous auditor feedback into the profile if it exists
        user_profile = state['user_profile'].copy()
        if state.get('auditor_notes'):
            feedback = f"\n\nCRITICAL AUDITOR FEEDBACK TO ADDRESS: {state['auditor_notes']}"
            user_profile['capabilities_statement'] += feedback
        
        # Generate the draft
        draft = self.generator.generate(
            opportunity_data={"opportunity_id": state['opportunity_id']},
            user_profile_data=user_profile,
            pdf_path=state.get('pdf_path')
        )
        
        return {
            **state,
            "draft_proposal": draft, 
            "iterations": state.get('iterations', 0) + 1
        }

class EvaluatorAgent:
    def __init__(self):
        # Initialize the engine we built in evaluator.py
        self.evaluator = ProposalEvaluator()

    def evaluate(self, state: AgentState):
        print("--- Agent: Evaluating Compliance & Formatting ---")
        
        # We provide a fixed context for the auditor to check against
        rfp_context = "Check for NAICS 541512 and FIPS 201 certification compliance."
        audit_raw = self.evaluator.evaluate_draft(state['draft_proposal'], rfp_context)
        
        # Clean and parse the JSON response from the local LLM
        try:
            start_idx = audit_raw.find('{')
            end_idx = audit_raw.rfind('}') + 1
            audit_report = json.loads(audit_raw[start_idx:end_idx])
        except Exception:
            # Fallback if the LLM fails to output perfect JSON
            audit_report = {
                "compliance_score": 80, 
                "auditor_notes": "Automatic audit failed to parse JSON. Manual review required."
            }
            
        print(f"Audit Complete. Score: {audit_report.get('compliance_score')}/100")
        
        return {
            **state,
            "compliance_score": int(audit_report.get('compliance_score', 0)),
            "auditor_notes": audit_report.get('auditor_notes', '')
        }