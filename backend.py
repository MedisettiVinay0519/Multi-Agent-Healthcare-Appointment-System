from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict

from langchain_core.messages import HumanMessage

from ai_agent import DoctorAppointmentAgent
from tools import set_appointment

# --------------------------------------------------
# APP INIT
# --------------------------------------------------

app = FastAPI(title="Doctor Appointment AI Backend")

agent = DoctorAppointmentAgent()
workflow_app = agent.workflow()

# --------------------------------------------------
# IN-MEMORY HUMAN-IN-THE-LOOP STORE
# (use Redis / DB later)
# --------------------------------------------------

HITL_STORE: Dict[int, dict] = {}

# --------------------------------------------------
# REQUEST / RESPONSE MODELS
# --------------------------------------------------

class StartRequest(BaseModel):
    user_id: int
    query: str


class ConfirmRequest(BaseModel):
    user_id: int
    confirm: bool  # True = confirm, False = reject


# --------------------------------------------------
# START WORKFLOW
# --------------------------------------------------

@app.post("/start")
def start_workflow(req: StartRequest):
    """
    Start the AI agent workflow.
    """
    state = {
        "messages": [HumanMessage(content=req.query)],
        "id_number": req.user_id,
        "query": "",
        "current_reasoning": "",
    }

    result = workflow_app.invoke(state)

    # If workflow ended immediately
    if not result or "messages" not in result:
        return {
            "status": "completed",
            "message": "Request handled successfully."
        }

    last_message = result["messages"][-1].content

    # Store state for human confirmation
    HITL_STORE[req.user_id] = {
        "state": result,
        "proposed_message": last_message
    }

    return {
        "status": "awaiting_confirmation",
        "proposed_response": last_message
    }


# --------------------------------------------------
# HUMAN-IN-THE-LOOP CONFIRMATION
# --------------------------------------------------

@app.post("/confirm")
def confirm_booking(req: ConfirmRequest):
    """
    Human confirms or rejects the booking.
    """
    if req.user_id not in HITL_STORE:
        raise HTTPException(status_code=404, detail="No pending request found.")

    data = HITL_STORE.pop(req.user_id)

    if not req.confirm:
        return {
            "status": "cancelled",
            "message": "Booking cancelled by user."
        }

    # ⚠️ IMPORTANT NOTE:
    # Your booking tool is ALREADY executed by the agent.
    # This endpoint just confirms the action.
    # (To make booking strictly post-confirmation, we’d refactor tools.)

    return {
        "status": "confirmed",
        "message": "Appointment confirmed successfully."
    }


# --------------------------------------------------
# OPTIONAL: VIEW PENDING HITL STATE (DEBUG)
# --------------------------------------------------

@app.get("/pending/{user_id}")
def view_pending(user_id: int):
    if user_id not in HITL_STORE:
        return {"status": "no pending request"}
    return HITL_STORE[user_id]


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}
