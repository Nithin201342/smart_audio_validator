import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
sys.path.append(PROJECT_ROOT)

import numpy as np
from src.genre_features import extract_genre_features
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from joblib import dump

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
DATASET_PATH = os.path.join(PROJECT_ROOT, "GTZAN", "Data", "genres_original")

X, y = [], []

print("Extracting features...")

for genre in os.listdir(DATASET_PATH):
    genre_path = os.path.join(DATASET_PATH, genre)
    if not os.path.isdir(genre_path):
        continue

    print(f"Processing genre: {genre}")

    for file in os.listdir(genre_path):
        if file.endswith(".wav"):
            file_path = os.path.join(genre_path, file)
            try:
                features = extract_genre_features(file_path)
                if features is not None:
                    X.append(features)
                    y.append(genre)
            except Exception as e:
                print("Skipping:", file_path, e)

X = np.array(X)

print("Feature extraction complete.")

# ✅ SINGLE, CORRECT ENCODER
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded
)

print("Training genre classifier...")

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)

print(f"Genre Model Accuracy: {acc * 100:.2f}%")
print("🎵 Genre Classes:", list(label_encoder.classes_))

# Save model + encoder
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

dump(model, os.path.join(MODEL_DIR, "genre_model.pkl"))
dump(label_encoder, os.path.join(MODEL_DIR, "genre_encoder.pkl"))

print("✅ Genre model & encoder saved successfully")
