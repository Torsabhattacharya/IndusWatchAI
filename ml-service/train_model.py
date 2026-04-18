
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

print("🤖 IndusWatchAI - ML Model Training")
print("=" * 50)

# Generate synthetic training data (based on sensor patterns)
np.random.seed(42)
n_samples = 10000

# Features: temperature, vibration, pressure, rpm, temp_trend, vib_trend
X = []
y = []

for _ in range(n_samples):
    temp = np.random.normal(75, 15)
    vib = np.random.normal(0.4, 0.3)
    pressure = np.random.normal(100, 12)
    rpm = np.random.normal(1500, 250)
    
    # Calculate failure probability based on thresholds
    failure_prob = 0
    if temp > 90:
        failure_prob += 0.3
    if vib > 0.8:
        failure_prob += 0.3
    if pressure > 115:
        failure_prob += 0.2
    if rpm > 1800 or rpm < 1200:
        failure_prob += 0.2
    
    # Random noise
    failure_prob += np.random.random() * 0.2
    
    # Label: 1 if failure probability > 0.5
    label = 1 if failure_prob > 0.5 else 0
    
    X.append([temp, vib, pressure, rpm])
    y.append(label)

X = np.array(X)
y = np.array(y)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest
print(f"📊 Training data: {len(X_train)} samples")
model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Model accuracy: {accuracy:.2%}")

# Save model
os.makedirs("C:/IndusWatchAI/ml-service/models", exist_ok=True)
joblib.dump(model, "C:/IndusWatchAI/ml-service/models/failure_model.pkl")
print("💾 Model saved: C:/IndusWatchAI/ml-service/models/failure_model.pkl")

# Feature importance
feature_names = ['Temperature', 'Vibration', 'Pressure', 'RPM']
importances = model.feature_importances_
print("\n📈 Feature Importance:")
for name, imp in zip(feature_names, importances):
    print(f"   {name}: {imp:.2%}")
