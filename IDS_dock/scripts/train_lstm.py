# scripts/train_lstm.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import joblib
import os

# Load data
print("📥 Loading preprocessed dataset...")
df = pd.read_csv("data/processed/portscan_clean.csv")

# Separate features and labels
X = df.drop("Label", axis=1).values
y = df["Label"].values

# Scale features
print("🧪 Scaling features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Reshape for LSTM input: (samples, timesteps, features)
X_scaled = X_scaled.reshape((X_scaled.shape[0], 1, X_scaled.shape[1]))

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# Build LSTM model
print("🧠 Building LSTM model...")
model = Sequential([
    LSTM(64, input_shape=(X_train.shape[1], X_train.shape[2]), return_sequences=True),
    Dropout(0.3),
    LSTM(32),
    Dropout(0.3),
    Dense(1, activation='sigmoid')
])

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# Callbacks
early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

# Train
print("🚀 Training LSTM model...")
history = model.fit(
    X_train, y_train,
    epochs=10,
    batch_size=64,
    validation_split=0.2,
    callbacks=[early_stop],
    verbose=1
)

# Evaluate
print("✅ Evaluating LSTM model...")
y_pred = (model.predict(X_test) > 0.5).astype("int32")
print("📊 Classification Report:")
print(classification_report(y_test, y_pred))

# Save model and scaler
os.makedirs("models", exist_ok=True)
model.save("models/portscan_lstm.h5")
joblib.dump(scaler, "models/lstm_scaler.pkl")

print("✅ LSTM model and scaler saved to 'models/'")
