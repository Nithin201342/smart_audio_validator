import os
import json
import numpy as np
import librosa
import pandas as pd
from tqdm import tqdm

# =========================
# PATH CONFIGURATION
# =========================
DATA_DIR = "../data/SingMOS-Pro"
WAV_DIR = os.path.join(DATA_DIR, "wav")
METADATA_PATH = os.path.join(DATA_DIR, "metadata.json")
OUTPUT_FEATURES = "../features/audio_features.csv"

SAMPLE_RATE = 16000
N_MFCC = 13


# =========================
# LOAD METADATA
# =========================
def load_metadata(metadata_path):
    """
    Load metadata.json and convert to:
    {
      "sys0001-utt0001.wav": mos_value,
      ...
    }
    """
    with open(metadata_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    metadata = {}

    for item in records:
        wav_path = item["wav"]          # e.g. wav/sys0001-utt0001.wav
        filename = os.path.basename(wav_path)

        scores = item.get("judge_score", [])
        if len(scores) == 0:
            continue

        mos = float(np.mean(scores))
        metadata[filename] = mos

    return metadata



# =========================
# FEATURE EXTRACTION
# =========================
def extract_features(audio_path):
    """
    Extract audio features from a single WAV file
    Returns: numpy array of features
    """
    try:
        y, sr = librosa.load(audio_path, sr=SAMPLE_RATE)

        # MFCCs
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N_MFCC)
        mfcc_mean = np.mean(mfcc, axis=1)

        # RMS Energy
        rms = librosa.feature.rms(y=y)
        rms_mean = np.mean(rms)

        # Zero Crossing Rate
        zcr = librosa.feature.zero_crossing_rate(y)
        zcr_mean = np.mean(zcr)

        # Spectral Features
        centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
        rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))

        # Combine all features
        features = np.hstack([
            mfcc_mean,
            rms_mean,
            zcr_mean,
            centroid,
            bandwidth,
            rolloff
        ])

        return features

    except Exception as e:
        print(f"Error processing {audio_path}: {e}")
        return None


# =========================
# MAIN PIPELINE
# =========================
def build_feature_dataset():
    metadata = load_metadata(METADATA_PATH)

    feature_rows = []
    feature_names = (
        [f"mfcc_{i+1}" for i in range(N_MFCC)]
        + ["rms", "zcr", "spectral_centroid", "spectral_bandwidth", "spectral_rolloff"]
    )

    print("Extracting audio features...")

    for filename in tqdm(os.listdir(WAV_DIR)):
        if not filename.endswith(".wav"):
            continue

        if filename not in metadata:
            continue

        audio_path = os.path.join(WAV_DIR, filename)
        mos_score = metadata[filename]

        features = extract_features(audio_path)
        if features is None:
            continue

        row = dict(zip(feature_names, features))
        row["mos"] = mos_score
        row["audio_id"] = filename.replace(".wav", "")

        feature_rows.append(row)



    df = pd.DataFrame(feature_rows)
    df.to_csv(OUTPUT_FEATURES, index=False)

    print(f"\nFeature extraction completed!")
    print(f"Saved to: {OUTPUT_FEATURES}")
    print(df.head())


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    build_feature_dataset()
