# scripts/train_autoencoder.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.callbacks import EarlyStopping
import joblib
import os

# Load data
print("📥 Loading preprocessed dataset...")
df = pd.read_csv("data/processed/portscan_clean.csv")

# Separate normal (label = 0) from anomalies (label = 1)
df_normal = df[df["Label"] == 0]
df_anomaly = df[df["Label"] == 1]

X_normal = df_normal.drop("Label", axis=1).values
X_all = df.drop("Label", axis=1).values
y_all = df["Label"].values

# Scale features
print("🧪 Scaling features...")
scaler = StandardScaler()
X_normal_scaled = scaler.fit_transform(X_normal)
X_all_scaled = scaler.transform(X_all)

# Train/test split (only train on normal traffic)
X_train, X_val = train_test_split(X_normal_scaled, test_size=0.2, random_state=42)

# Define Autoencoder model
print("🧠 Building Autoencoder model...")
input_dim = X_train.shape[1]
input_layer = Input(shape=(input_dim,))
encoded = Dense(32, activation="relu")(input_layer)
encoded = Dense(16, activation="relu")(encoded)
decoded = Dense(32, activation="relu")(encoded)
decoded = Dense(input_dim, activation="linear")(decoded)

autoencoder = Model(inputs=input_layer, outputs=decoded)
autoencoder.compile(optimizer='adam', loss='mse')

# Callbacks
early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

# Train Autoencoder
print("🚀 Training Autoencoder on normal traffic...")
history = autoencoder.fit(
    X_train, X_train,
    epochs=50,
    batch_size=128,
    validation_data=(X_val, X_val),
    callbacks=[early_stop],
    verbose=1
)

# Calculate reconstruction error on all data
print("🔍 Calculating reconstruction error...")
reconstructions = autoencoder.predict(X_all_scaled)
mse = np.mean(np.square(X_all_scaled - reconstructions), axis=1)

# Set threshold (e.g., 95th percentile of normal MSE)
threshold = np.percentile(mse[y_all == 0], 95)
print(f"🚨 Threshold for anomaly detection: {threshold:.6f}")

# Predict anomalies
y_pred = (mse > threshold).astype(int)

# Evaluate
print("✅ Evaluating Autoencoder anomaly detection...")
print("📊 Classification Report:")
print(classification_report(y_all, y_pred))

# Save model and scaler
os.makedirs("models", exist_ok=True)
autoencoder.save("models/portscan_autoencoder.h5")
joblib.dump(scaler, "models/autoencoder_scaler.pkl")
joblib.dump(threshold, "models/autoencoder_threshold.pkl")

print("✅ Autoencoder model, scaler, and threshold saved to 'models/'")
