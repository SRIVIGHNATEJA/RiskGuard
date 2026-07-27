import pandas as pd
import sys

def main():
    try:
        df = pd.read_csv('data/riskguard_synthetic_claims.csv')
    except Exception as e:
        print(f"Error loading dataset: {e}")
        sys.exit(1)
        
    print("=== Shape ===")
    print(df.shape)
    
    print("\n=== Columns and Data Types ===")
    print(df.dtypes)
    
    print("\n=== Missing Values ===")
    print(df.isnull().sum())
    
    print("\n=== Class Distribution (Target Variable) ===")
    print(df['risk_label'].value_counts())
    
    print("\n=== Basic Feature Ranges ===")
    print(df.describe())

if __name__ == '__main__':
    main()
