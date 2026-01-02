import librosa
import numpy as np

def detect_error_segments(audio_path, sr=22050):
    y, sr = librosa.load(audio_path, sr=sr)

    frame_len = 2048
    hop_len = 512

    rms = librosa.feature.rms(y=y, frame_length=frame_len, hop_length=hop_len)[0]
    times = librosa.frames_to_time(range(len(rms)), sr=sr, hop_length=hop_len)

    segments = []
    threshold = np.mean(rms) * 0.4  # silence / weak signal

    in_bad = False
    start = 0

    for i, val in enumerate(rms):
        if val < threshold and not in_bad:
            start = times[i]
            in_bad = True
        elif val >= threshold and in_bad:
            segments.append({
                "start": round(start, 2),
                "end": round(times[i], 2),
                "type": "low_energy"
            })
            in_bad = False

    return segments
