# src/genre_predictor.py
import os
import joblib
import numpy as np

from src.genre_features import extract_genre_features

MODEL_DIR = "models"

# Load model and encoder ONCE
genre_model = joblib.load(os.path.join(MODEL_DIR, "genre_model.pkl"))
genre_encoder = joblib.load(os.path.join(MODEL_DIR, "genre_encoder.pkl"))


def predict_genre(audio_path):
    """
    Predict genre of given audio file
    """
    try:
        features = extract_genre_features(audio_path)

        if features is None:
            return "Unknown"

        features = np.array(features).reshape(1, -1)

        pred_index = genre_model.predict(features)[0]
        genre = genre_encoder.inverse_transform([pred_index])[0]

        return genre

    except Exception as e:
        print("🔥 Genre prediction error:", e)
        return "Unknown"
