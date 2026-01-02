def generate_recommendations(features):
    """
    features example order:
    [duration, pitch_std, spectral_centroid, zcr, rms_mean, rms_std]
    """

    duration, pitch_std, centroid, zcr, rms_mean, rms_std = features

    recs = []

    # 🔉 Low loudness
    if rms_mean < 0.03:
        recs.append({
            "issue": "Low Loudness",
            "message": "The audio is too quiet and lacks presence.",
            "fix": "Apply normalization and gentle compression.",
            "youtube": "https://www.youtube.com/watch?v=1Yf9J7U3S6Q"
        })

    # 🔊 Clipping / Too loud
    if rms_mean > 0.25:
        recs.append({
            "issue": "Clipping / Distortion",
            "message": "Audio levels are too high and may cause distortion.",
            "fix": "Reduce gain and apply a limiter.",
            "youtube": "https://www.youtube.com/watch?v=Jt8FqM1pK0g"
        })

    # 🌊 High noise / hiss
    if zcr > 0.12:
        recs.append({
            "issue": "Background Noise",
            "message": "High background noise detected.",
            "fix": "Use noise reduction or noise gate.",
            "youtube": "https://www.youtube.com/watch?v=UPpYYHmpc3k"
        })

    # 🎤 Pitch instability
    if pitch_std > 80:
        recs.append({
            "issue": "Pitch Instability",
            "message": "Pitch variation is high, vocals/instruments may sound unstable.",
            "fix": "Use pitch correction or re-record with monitoring.",
            "youtube": "https://www.youtube.com/watch?v=KXb4g4Eo5wU"
        })

    # 🎚️ Harsh / dull tone
    if centroid < 1200:
        recs.append({
            "issue": "Dull Sound",
            "message": "Audio lacks high-frequency clarity.",
            "fix": "Apply high-shelf EQ boost.",
            "youtube": "https://www.youtube.com/watch?v=H5uN9fQhX2M"
        })

    if centroid > 3500:
        recs.append({
            "issue": "Harsh Sound",
            "message": "Audio is overly bright or harsh.",
            "fix": "Reduce high frequencies using EQ.",
            "youtube": "https://www.youtube.com/watch?v=KzP6XzZkFqM"
        })

    # 🎵 Short audio warning
    if duration < 15:
        recs.append({
            "issue": "Short Duration",
            "message": "Audio is too short for reliable quality analysis.",
            "fix": "Upload a longer clip (minimum 20–30 seconds).",
            "youtube": "https://www.youtube.com/watch?v=2xYH8d9Zz7Y"
        })

    if not recs:
        recs.append({
            "issue": "Good Quality",
            "message": "No major issues detected.",
            "fix": "Minor mastering enhancements can be applied.",
            "youtube": "https://www.youtube.com/watch?v=TEjOdqZFvhY"
        })

    return recs
