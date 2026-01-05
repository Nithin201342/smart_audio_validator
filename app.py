from flask import Flask, render_template, request
import os
import uuid

from src.inference import predict_mos
from src.feature_extraction import extract_features
from src.quality_mapper import map_quality
from src.recommendations import generate_recommendations
from flask import jsonify
from src.error_segments import detect_error_segments


# -------------------------
# Flask App Setup
# -------------------------
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------
# Home Page
# -------------------------
@app.route("/")
def index():
    return render_template("index.html")

# -------------------------
# Analyze Audio
# -------------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    # Get uploaded file
    file = request.files.get("audio")

    if not file:
        return "❌ Please upload a valid WAV file."

    # Save file with unique name
    filename = f"{uuid.uuid4()}.wav"
    audio_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(audio_path)

    # -------------------------
    # ML Pipeline (UNCHANGED)
    # -------------------------
    mos = predict_mos(audio_path)
    quality, confidence = map_quality(mos)
    features = extract_features(audio_path)
    recs = generate_recommendations(features)

    # -------------------------
    # Send results to UI
    # -------------------------
    return render_template(
        "result.html",
        mos=round(mos, 2),
        quality=quality,
        confidence=confidence,
        recommendations=recs
    )

@app.route("/analyze_ajax", methods=["POST"])
def analyze_ajax():
    try:
        file = request.files.get("audio")
        print("Received file:", file.filename if file else None)

        if not file:
            return jsonify({"error": "No audio file"}), 400

        filename = f"{uuid.uuid4()}.wav"
        audio_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(audio_path)

        mos = predict_mos(audio_path)
        quality, confidence = map_quality(mos)
        features = extract_features(audio_path)
        recs = generate_recommendations(features)
        error_segments = detect_error_segments(audio_path)

        return jsonify({
            "mos": round(mos, 2),
            "quality": quality,
            "confidence": confidence,
            "recommendations": recs,
            "loudness": float(features[4]),
            "pitch_std": float(features[1]),
            "error_segments": error_segments
        })

    except Exception as e:
        print("🔥 ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


# -------------------------
# Run App
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
