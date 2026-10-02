from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from ...models.schemas import GrievanceSubmission, GrievanceRecord, GrievanceStatusResponse
from ...core.grievance_manager import grievance_manager

router = APIRouter(prefix="/grievance", tags=["Citizen Grievance Redressal (Lokshahi)"])

class UpdateStatusPayload(BaseModel):
    new_status: str
    remark: str
    officer_name: str

@router.post("/submit", response_model=GrievanceRecord)
def submit_grievance(sub: GrievanceSubmission):
    return grievance_manager.create_grievance(sub)

@router.get("/track/{token_id}", response_model=GrievanceStatusResponse)
def track_grievance(token_id: str):
    rec = grievance_manager.get_by_token(token_id)
    if not rec:
        return GrievanceStatusResponse(
            found=False,
            record=None,
            message=f"No grievance found with Token ID '{token_id}'. Please verify your token number."
        )
    return GrievanceStatusResponse(found=True, record=rec, message="Record retrieved successfully.")

@router.get("/list", response_model=List[GrievanceRecord])
def list_grievances(limit: int = 50):
    return grievance_manager.list_all(limit=limit)

@router.post("/update-status/{token_id}", response_model=GrievanceRecord)
def update_grievance_status(token_id: str, payload: UpdateStatusPayload):
    updated = grievance_manager.update_status(
        token_id=token_id,
        new_status=payload.new_status,
        remark=payload.remark,
        updated_by=payload.officer_name
    )
    if not updated:
        raise HTTPException(status_code=404, detail=f"Grievance #{token_id} not found.")
    return updated
