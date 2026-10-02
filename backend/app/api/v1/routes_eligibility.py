from fastapi import APIRouter
from ...models.schemas import EligibilityRequest, EligibilityResponse
from ...core.eligibility_engine import eligibility_engine

router = APIRouter(prefix="/eligibility", tags=["Eligibility Engine"])

@router.post("/check", response_model=EligibilityResponse)
def check_eligibility(payload: EligibilityRequest):
    return eligibility_engine.evaluate(payload)
