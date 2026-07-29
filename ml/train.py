import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score

def main():
    # 1. Load the dataset
    data_path = 'data/riskguard_synthetic_claims.csv'
    df = pd.read_csv(data_path)
    print(f"Loaded dataset: {df.shape}")

    # 2. Separate features (X) and target (y)
    X = df[['claim_amount', 'previous_claim_count', 'days_since_last_claim', 'claim_category']]
    y = df['risk_label']

    # 3. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Training set: {X_train.shape}, Test set: {X_test.shape}")

    # 4. Define Preprocessing
    # We use ColumnTransformer to apply specific transformations to specific columns
    numeric_features = ['claim_amount', 'previous_claim_count', 'days_since_last_claim']
    numeric_transformer = StandardScaler() # Standardize numeric features for Logistic Regression

    categorical_features = ['claim_category']
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    # 5. Create the Pipeline
    # Pipeline bundles preprocessing and modeling steps
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', LogisticRegression(random_state=42))
    ])

    # 6. Train the Model
    print("Training Logistic Regression model...")
    pipeline.fit(X_train, y_train)

    # 7. Evaluate Basic Performance
    print("\n--- Training Performance ---")
    y_train_pred = pipeline.predict(X_train)
    print(f"Accuracy: {accuracy_score(y_train, y_train_pred):.4f}")
    
    print("\n--- Test Performance ---")
    y_test_pred = pipeline.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_test_pred):.4f}")
    print("\nClassification Report (Test):")
    print(classification_report(y_test, y_test_pred))

    # 8. Save the Trained Pipeline
    os.makedirs('models', exist_ok=True)
    model_path = 'models/risk_model.joblib'
    joblib.dump(pipeline, model_path)
    print(f"\nModel successfully saved to {model_path}")

    # 9. Verify the Saved Model (Load and Predict)
    print("\nVerifying saved model...")
    loaded_model = joblib.load(model_path)
    
    # Create a single test record
    test_record = pd.DataFrame([{
        'claim_amount': 85000.0,
        'previous_claim_count': 5,
        'days_since_last_claim': 30,
        'claim_category': 'AUTO'
    }])
    
    # Predict using the loaded model
    pred_label = loaded_model.predict(test_record)[0]
    pred_prob = loaded_model.predict_proba(test_record)[0]
    
    print(f"Test Record: {test_record.to_dict(orient='records')[0]}")
    print(f"Prediction: {pred_label}")
    print(f"Probabilities: {loaded_model.classes_} -> {pred_prob}")
    print("Verification complete.")

if __name__ == '__main__':
    main()
