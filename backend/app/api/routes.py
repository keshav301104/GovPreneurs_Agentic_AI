from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import shutil
from langgraph.graph import StateGraph, END

# Import the state and agents we just defined in agent.py
from rag.agent import AgentState, DrafterAgent, EvaluatorAgent

router = APIRouter()

# --- INPUT MODELS ---
class Project(BaseModel):
    project_name: str
    naics_codes: List[str]
    standards: List[str]

class UserProfile(BaseModel):
    company_name: str
    capabilities_statement: str
    past_performance: List[Project]

class ProposalRequest(BaseModel):
    opportunity_id: str
    pdf_path: str
    user_profile: UserProfile

# --- PIPELINE CONSTRUCTION ---
def build_pipeline():
    drafter = DrafterAgent()
    evaluator = EvaluatorAgent()
    
    # Initialize the Graph with our AgentState
    workflow = StateGraph(AgentState)

    # Define the Nodes
    workflow.add_node("draft_proposal", drafter.draft)
    workflow.add_node("evaluate_proposal", evaluator.evaluate)

    # Define the Flow
    workflow.set_entry_point("draft_proposal")
    workflow.add_edge("draft_proposal", "evaluate_proposal")

    # The Loop Logic: Check score or max iterations
    def should_continue(state: AgentState):
        if state.get("compliance_score", 0) >= 90 or state.get("iterations", 0) >= 3:
            return END
        return "draft_proposal"

    workflow.add_conditional_edges(
        "evaluate_proposal", 
        should_continue, 
        {END: END, "draft_proposal": "draft_proposal"}
    )

    return workflow.compile()

# Global pipeline instance
app_pipeline = build_pipeline()

# --- ENDPOINTS ---

@router.post("/generate-proposal")
async def generate_proposal(request: ProposalRequest):
    try:
        # Prepare the initial state from the frontend payload
        initial_state = {
            "opportunity_id": request.opportunity_id,
            "pdf_path": request.pdf_path,
            "user_profile": request.user_profile.model_dump(),
            "draft_proposal": "",
            "compliance_score": 0,
            "auditor_notes": "",
            "iterations": 0
        }
        
        # Run the autonomous agent loop
        final_state = app_pipeline.invoke(initial_state)
        
        return {
            "draft_proposal": final_state["draft_proposal"],
            "final_compliance_score": final_state["compliance_score"],
            "auditor_notes": final_state["auditor_notes"],
            "iterations_required": final_state["iterations"]
        }
    except Exception as e:
        print(f"Pipeline Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    # Create data directory if missing
    os.makedirs("data", exist_ok=True)
    
    # Save the file locally
    file_path = f"data/{file.filename.replace(' ', '_')}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"message": "Upload successful", "file_path": file_path}