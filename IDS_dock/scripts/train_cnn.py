# IDS_dock/scripts/train_cnn.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv1D, MaxPooling1D, Flatten, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping
import joblib
import os

# 📦 Load preprocessed dataset
print("📥 Loading preprocessed dataset...")
df = pd.read_csv("data/processed/portscan_clean.csv")

# 🔁 Shuffle dataset (helps training)
df = df.sample(frac=1).reset_index(drop=True)

# 🧪 Split features and labels
X = df.drop("Label", axis=1)
y = df["Label"]

# 🔍 Normalize the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Save the scaler for inference
joblib.dump(scaler, "models/cnn_scaler.pkl")

# 🧱 Reshape input for Conv1D: (samples, time_steps, features=1)
X_scaled = X_scaled.reshape((X_scaled.shape[0], X_scaled.shape[1], 1))

# 🎓 Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# 🧠 Build CNN model
model = Sequential([
    Conv1D(64, kernel_size=3, activation='relu', input_shape=(X_train.shape[1], 1)),
    BatchNormalization(),
    MaxPooling1D(pool_size=2),
    Dropout(0.3),

    Conv1D(128, kernel_size=3, activation='relu'),
    BatchNormalization(),
    MaxPooling1D(pool_size=2),
    Dropout(0.3),

    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.3),
    Dense(1, activation='sigmoid')  # Binary classification
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# 🏁 Train model with early stopping
print("🚀 Training CNN model...")
early_stop = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
history = model.fit(
    X_train, y_train,
    epochs=20,
    batch_size=256,
    validation_split=0.2,
    callbacks=[early_stop],
    verbose=1
)

# 🧪 Evaluate model
print("\n✅ Evaluating CNN model...")
y_pred = model.predict(X_test)
y_pred_classes = (y_pred > 0.5).astype(int)

print("📊 Classification Report:\n", classification_report(y_test, y_pred_classes))
print("🎯 Accuracy:", accuracy_score(y_test, y_pred_classes))

# 💾 Save model
model.save("models/cnn_model.h5")
print("✅ Model and scaler saved to 'models/'")
