import os
import joblib
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Path relative to the project root
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'risk_model.joblib')

class MLService:
    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        """Loads the serialized joblib model pipeline."""
        if not os.path.exists(MODEL_PATH):
            logger.error(f"Model file not found at {MODEL_PATH}")
            raise FileNotFoundError("The ML model file is missing. Please ensure it is trained and saved.")
        
        try:
            self.model = joblib.load(MODEL_PATH)
            logger.info("ML model pipeline loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load the ML model: {e}")
            raise RuntimeError("The ML model file is corrupt or invalid.") from e

    def predict_risk(self, claim_amount: float, previous_claim_count: int, days_since_last_claim: int, claim_category: str) -> dict:
        """
        Receives raw claim features, processes them through the saved pipeline,
        and returns the prediction and risk score.
        """
        if self.model is None:
            raise RuntimeError("Model is not loaded.")

        # Reconstruct the expected input structure (a DataFrame with exactly the column names used during training)
        input_data = pd.DataFrame([{
            'claim_amount': claim_amount,
            'previous_claim_count': previous_claim_count,
            'days_since_last_claim': days_since_last_claim,
            'claim_category': claim_category
        }])

        try:
            # 1. Get the categorical prediction (NORMAL / REVIEW)
            prediction = self.model.predict(input_data)[0]

            # 2. Get the probability of the 'REVIEW' class (which we use as the risk_score)
            # predict_proba returns an array of shape (n_samples, n_classes).
            # e.g., [[prob_NORMAL, prob_REVIEW]]
            probabilities = self.model.predict_proba(input_data)[0]
            
            # The classes_ attribute tells us the order of probabilities
            review_index = list(self.model.classes_).index('REVIEW')
            risk_score = float(probabilities[review_index])

            return {
                "prediction": prediction,
                "risk_score": round(risk_score, 4)
            }
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            raise RuntimeError(f"ML Inference failed: {e}") from e

# Initialize a singleton instance to be imported by FastAPI
ml_service = MLService()

if __name__ == "__main__":
    # Quick verification when script is run directly
    print("--- ML Service Verification ---")
    try:
        service = MLService()
        result = service.predict_risk(
            claim_amount=85000.0, 
            previous_claim_count=5, 
            days_since_last_claim=30, 
            claim_category='AUTO'
        )
        print(f"Sample Input: Amount=85000.0, Count=5, Days=30, Category=AUTO")
        print(f"Prediction Output: {result}")
        print("Verification successful.")
    except Exception as ex:
        print(f"Verification failed: {ex}")
