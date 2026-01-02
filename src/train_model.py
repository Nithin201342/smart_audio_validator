import os
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# Try XGBoost first (best accuracy)
try:
    from xgboost import XGBRegressor
    MODEL_TYPE = "xgboost"
except ImportError:
    from sklearn.ensemble import RandomForestRegressor
    MODEL_TYPE = "random_forest"


# =========================
# PATH CONFIGURATION
# =========================
FEATURES_PATH = "../features/audio_features.csv"
MODEL_DIR = "../models"
MODEL_PATH = os.path.join(MODEL_DIR, "mos_predictor.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)


# =========================
# LOAD DATA
# =========================
def load_data():
    df = pd.read_csv(FEATURES_PATH)

    X = df.drop(columns=["mos", "audio_id"])
    y = df["mos"]

    return X, y


# =========================
# BUILD MODEL
# =========================
def build_model():
    if MODEL_TYPE == "xgboost":
        print("Using XGBoost Regressor (High Accuracy)")

        model = XGBRegressor(
            n_estimators=400,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            random_state=42,
            n_jobs=-1
        )
    else:
        print("XGBoost not found. Using Random Forest Regressor")

        model = RandomForestRegressor(
            n_estimators=300,
            max_depth=20,
            random_state=42,
            n_jobs=-1
        )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", model)
    ])

    return pipeline


# =========================
# TRAIN & EVALUATE
# =========================
def train():
    X, y = load_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = build_model()

    print("\nTraining model...")
    model.fit(X_train, y_train)

    # Predictions
    y_pred = model.predict(X_test)

    # Metrics
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print("\n📊 Model Performance:")
    print(f"MAE  : {mae:.3f}")
    print(f"RMSE : {rmse:.3f}")
    print(f"R²   : {r2:.3f}")

    # Save model
    joblib.dump(model, MODEL_PATH)
    print(f"\n✅ Model saved at: {MODEL_PATH}")


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    train()
