from pydantic import BaseModel, Field, validator
from typing import Optional

class ClaimRequest(BaseModel):
    claim_amount: float = Field(..., ge=0.0, description="Amount of the claim, must be non-negative")
    previous_claim_count: int = Field(..., ge=0, description="Number of previous claims, must be non-negative")
    days_since_last_claim: int = Field(..., ge=0, description="Days since last claim, must be non-negative")
    claim_category: str = Field(..., description="Category of the claim")

class PredictResponse(BaseModel):
    claim_id: int
    risk_score: float
    prediction: str

class ClaimResponse(BaseModel):
    claim_id: int
    claim_amount: float
    previous_claim_count: int
    days_since_last_claim: int
    claim_category: str
    risk_score: float
    prediction: str
