from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from backend.schemas import ClaimRequest, PredictResponse, ClaimResponse
from backend.ml_service import ml_service
from backend.db import insert_claim_and_result, get_claim_with_result

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RISKGuard API", description="ML-backed QA Lab Backend", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict", response_model=PredictResponse)
def predict_claim(claim: ClaimRequest):
    # Pydantic has already validated types and numeric boundaries.
    # The prompt specified "business-rule violation -> 400"
    valid_categories = {'AUTO', 'HOME', 'HEALTH', 'LIFE', 'TRAVEL'}
    if claim.claim_category.upper() not in valid_categories:
        raise HTTPException(status_code=400, detail=f"Invalid claim_category. Must be one of {valid_categories}")

    try:
        # 1. Run ML Prediction
        result = ml_service.predict_risk(
            claim_amount=claim.claim_amount,
            previous_claim_count=claim.previous_claim_count,
            days_since_last_claim=claim.days_since_last_claim,
            claim_category=claim.claim_category.upper()
        )
        
        # 2. Database Transaction
        claim_id = insert_claim_and_result(
            claim_data=claim.dict(),
            risk_score=result["risk_score"],
            prediction=result["prediction"]
        )

        # 3. Return JSON Response
        return PredictResponse(
            claim_id=claim_id,
            risk_score=result["risk_score"],
            prediction=result["prediction"]
        )
    except RuntimeError as e:
        logger.error(f"Backend processing error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected backend failure")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Unexpected backend failure")

@app.get("/claim/{claim_id}", response_model=ClaimResponse)
def get_claim(claim_id: str):
    if not claim_id.isdigit():
        raise HTTPException(status_code=400, detail="Invalid ID format")
        
    try:
        claim_data = get_claim_with_result(int(claim_id))
        if not claim_data:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        return ClaimResponse(**claim_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database read error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve claim")
