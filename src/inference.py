import os
import joblib
import numpy as np
from src.feature_extraction import extract_features

# -------------------------
# Resolve project root
# -------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "models", "mos_predictor.pkl")

# Load model
model = joblib.load(MODEL_PATH)

def predict_mos(audio_path):
    features = extract_features(audio_path)
    features = features.reshape(1, -1)

    mos = model.predict(features)[0]
    mos = float(np.clip(mos, 1.0, 5.0))
    return mos
