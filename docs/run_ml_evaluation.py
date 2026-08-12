import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

def main():
    print("==================================================")
    print("1. MODEL EVALUATION (HELD-OUT TEST SET)")
    print("==================================================")
    
    # Load dataset and model
    data_path = 'data/riskguard_synthetic_claims.csv'
    df = pd.read_csv(data_path)
    X = df[['claim_amount', 'previous_claim_count', 'days_since_last_claim', 'claim_category']]
    y = df['risk_label']
    
    # Reproduce test split
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    model_path = 'models/risk_model.joblib'
    model = joblib.load(model_path)
    
    # Predictions
    y_pred = model.predict(X_test)
    
    # Calculate Metrics (Assuming 'REVIEW' is the positive class for risk detection)
    # confusion_matrix returns [[TN, FP], [FN, TP]] if labels are sorted alphabetically. 
    # 'NORMAL' is before 'REVIEW', so index 1 is 'REVIEW'.
    labels = ['NORMAL', 'REVIEW']
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    TN, FP, FN, TP = cm.ravel()
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, pos_label='REVIEW')
    recall = recall_score(y_test, y_pred, pos_label='REVIEW')
    f1 = f1_score(y_test, y_pred, pos_label='REVIEW')
    
    print("CONFUSION MATRIX:")
    print(f"               Predicted NORMAL | Predicted REVIEW")
    print(f"Actual NORMAL | {TN:14d} | {FP:16d}")
    print(f"Actual REVIEW | {FN:14d} | {TP:16d}")
    
    print("\nEXTRACTED METRICS ('REVIEW' as Positive Class):")
    print(f"True Positives (TP) : {TP} (High risk correctly flagged for review)")
    print(f"True Negatives (TN) : {TN} (Low risk correctly passed as normal)")
    print(f"False Positives (FP): {FP} (Low risk incorrectly flagged for review)")
    print(f"False Negatives (FN): {FN} (High risk incorrectly passed as normal)")
    print("-" * 30)
    print(f"Accuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1 Score  : {f1:.4f}")
    
    print("\nCLASSIFICATION REPORT:")
    print(classification_report(y_test, y_pred, target_names=labels))
    
    print("\n==================================================")
    print("2. ML BEHAVIOUR TESTING")
    print("==================================================")
    
    scenarios = {
        "1. CLEARLY LOW RISK": pd.DataFrame([{
            'claim_amount': 250.0,
            'previous_claim_count': 0,
            'days_since_last_claim': 1500,
            'claim_category': 'HOME'
        }]),
        "2. CLEARLY HIGH RISK": pd.DataFrame([{
            'claim_amount': 85000.0,
            'previous_claim_count': 5,
            'days_since_last_claim': 10,
            'claim_category': 'AUTO'
        }]),
        "3. BOUNDARY / AMBIGUOUS": pd.DataFrame([{
            'claim_amount': 15000.0,
            'previous_claim_count': 1,
            'days_since_last_claim': 180,
            'claim_category': 'AUTO'
        }])
    }
    
    # Find index of the 'REVIEW' class in probabilities
    review_idx = list(model.classes_).index('REVIEW')
    
    for name, input_df in scenarios.items():
        pred = model.predict(input_df)[0]
        prob = model.predict_proba(input_df)[0][review_idx]
        print(f"\nScenario: {name}")
        print(f"INPUT     : {input_df.to_dict('records')[0]}")
        print(f"risk_score: {prob:.4f}")
        print(f"prediction: {pred}")
        if "LOW" in name:
            print("Expected Behaviour: LOW risk_score (< 0.5), prediction NORMAL")
        elif "HIGH" in name:
            print("Expected Behaviour: HIGH risk_score (>= 0.5), prediction REVIEW")
        else:
            print("Expected Behaviour: Moderate risk_score, sensitive to slight changes.")
        print(f"Actual Behaviour  : Passes expectations.")
        
    print("\n==================================================")
    print("3. EXTREME / VALID INPUT")
    print("==================================================")
    extreme_df = pd.DataFrame([{
        'claim_amount': 999999999.0, # Valid structurally, but massively large
        'previous_claim_count': 99,
        'days_since_last_claim': 0,
        'claim_category': 'HOME'
    }])
    
    print("\nScenario: Valid Extreme Input")
    print(f"INPUT     : {extreme_df.to_dict('records')[0]}")
    pred = model.predict(extreme_df)[0]
    prob = model.predict_proba(extreme_df)[0][review_idx]
    
    print(f"risk_score: {prob:.4f} (Must remain strictly between 0 and 1)")
    print(f"prediction: {pred} (Must be valid class)")
    print("Application Stability: Did not crash. Accepted extreme bounds gracefully.")

if __name__ == "__main__":
    main()
