import joblib
from feature_extraction import extract_features
import numpy as np

model = joblib.load("models/quality_model.pkl")
encoder = joblib.load("models/label_encoder.pkl")

def evaluate_audio(audio_path):
    features = extract_features(audio_path)
    features = np.array(features).reshape(1, -1)

    prediction = model.predict(features)
    label = encoder.inverse_transform(prediction)

    return label[0]
