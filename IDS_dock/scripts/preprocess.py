# scripts/preprocess.py

import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import os

# Paths
RAW_FILE = "data/raw/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv"
SAVE_PATH = "data/processed/portscan_clean.csv"

def preprocess():
    print("🔄 Loading dataset...")
    df = pd.read_csv(RAW_FILE)
    
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    print("✅ Dropping null or infinite values...")
    df = df.replace([float('inf'), float('-inf')], pd.NA)
    df = df.dropna()

    print("🧼 Dropping non-numeric and irrelevant columns...")
    drop_cols = ['Flow ID', 'Source IP', 'Destination IP', 'Timestamp']
    df = df.drop(columns=[col for col in drop_cols if col in df.columns])

    print("🔍 Encoding label...")
    df['Label'] = df['Label'].apply(lambda x: 'BENIGN' if 'BENIGN' in x else 'ATTACK')
    encoder = LabelEncoder()
    df['Label'] = encoder.fit_transform(df['Label'])  # BENIGN=0, ATTACK=1

    print("📊 Scaling features...")
    features = df.drop('Label', axis=1)
    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(features)
    
    print("💾 Saving cleaned data...")
    processed_df = pd.DataFrame(scaled_features, columns=features.columns)
    processed_df['Label'] = df['Label'].values
    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
    processed_df.to_csv(SAVE_PATH, index=False)
    print(f"✅ Done! Saved to: {SAVE_PATH}")

if __name__ == "__main__":
    preprocess()
