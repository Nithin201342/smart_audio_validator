def generate_recommendations(features):
    """
    Uses selected features only.
    Extra features are ignored safely.
    """

    duration = features[0]
    pitch_std = features[2]
    centroid = features[3]
    zcr = features[4]
    rms_mean = features[5]
    rms_std = features[6]

    recs = []

    if rms_mean < 0.03:
        recs.append({
            "issue": "Low Loudness",
            "message": "Audio level is too low.",
            "fix": "Normalize and compress the audio.",
            "youtube": "https://www.youtube.com/watch?v=1Yf9J7U3S6Q"
        })

    if rms_mean > 0.25:
        recs.append({
            "issue": "Clipping / Distortion",
            "message": "Audio is too loud and may be distorted.",
            "fix": "Reduce gain and apply a limiter.",
            "youtube": "https://www.youtube.com/watch?v=Jt8FqM1pK0g"
        })

    if zcr > 0.12:
        recs.append({
            "issue": "Background Noise",
            "message": "High noise level detected.",
            "fix": "Apply noise reduction or noise gate.",
            "youtube": "https://www.youtube.com/watch?v=UPpYYHmpc3k"
        })

    if pitch_std > 80:
        recs.append({
            "issue": "Pitch Instability",
            "message": "Pitch variations are high.",
            "fix": "Use pitch correction or re-record.",
            "youtube": "https://www.youtube.com/watch?v=KXb4g4Eo5wU"
        })

    if not recs:
        recs.append({
            "issue": "Good Quality",
            "message": "No major audio issues detected.",
            "fix": "Minor mastering enhancements can improve quality.",
            "youtube": "https://www.youtube.com/watch?v=TEjOdqZFvhY"
        })

    return recs
