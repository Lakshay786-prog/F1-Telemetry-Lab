from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

import joblib


# ==========================================================
# PROJECT PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "f1_ml_features.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "model"
    / "saved_models"
)

MODEL_FILE = (
    MODEL_DIR
    / "lap_time_prediction_model.pkl"
)

IMPUTER_FILE = (
    MODEL_DIR
    / "lap_time_prediction_imputer.pkl"
)


# ==========================================================
# FEATURES
# ==========================================================

FEATURE_COLUMNS = [

    "MaxSpeed",
    "AvgSpeed",
    "MinSpeed",

    "MaxThrottle",
    "AvgThrottle",
    "MinThrottle",

    "MaxBrake",
    "AvgBrake",
    "BrakingSamples",

    "MinGear",
    "MaxGear",
    "MostUsedGear",
    "GearChanges",

    "MaxRPM",
    "AvgRPM",
    "MinRPM",

    "DRSUsage"

]


# ==========================================================
# LOAD DATA
# ==========================================================

def load_data():

    if not DATA_FILE.exists():

        raise FileNotFoundError(
            f"Dataset not found:\n{DATA_FILE}"
        )

    return pd.read_csv(
        DATA_FILE
    )


# ==========================================================
# PREPARE DATA
# ==========================================================

def prepare_data(df):

    # Remove rows without lap time

    df = df.dropna(
        subset=["LapTime"]
    ).copy()


    X = df[
        FEATURE_COLUMNS
    ].copy()


    y = df[
        "LapTime"
    ].copy()


    return X, y


# ==========================================================
# TRAIN MODEL
# ==========================================================

def train_prediction_model(
    X_train,
    y_train
):

    imputer = SimpleImputer(
        strategy="median"
    )


    X_train = imputer.fit_transform(
        X_train
    )


    model = RandomForestRegressor(

        n_estimators=300,

        max_depth=12,

        min_samples_split=2,

        min_samples_leaf=1,

        random_state=42,

        n_jobs=-1

    )


    model.fit(
        X_train,
        y_train
    )


    return model, imputer


# ==========================================================
# EVALUATE
# ==========================================================

def evaluate_model(
    model,
    imputer,
    X_test,
    y_test
):

    X_test = imputer.transform(
        X_test
    )


    predictions = model.predict(
        X_test
    )


    mae = mean_absolute_error(
        y_test,
        predictions
    )


    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )


    r2 = r2_score(
        y_test,
        predictions
    )


    return (
        predictions,
        mae,
        rmse,
        r2
    )


# ==========================================================
# SAVE MODEL
# ==========================================================

def save_model(
    model,
    imputer
):

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    joblib.dump(
        model,
        MODEL_FILE
    )


    joblib.dump(
        imputer,
        IMPUTER_FILE
    )


# ==========================================================
# PREDICT SINGLE LAP
# ==========================================================

def predict_lap_time(
    model,
    imputer,
    features
):

    input_data = pd.DataFrame(
        [features],
        columns=FEATURE_COLUMNS
    )


    input_data = imputer.transform(
        input_data
    )


    prediction = model.predict(
        input_data
    )


    return prediction[0]


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    print("\n==========================================")
    print("        F1 TELEMETRY LAB")
    print("        PHASE 6.5")
    print("        LAP-TIME PREDICTION")
    print("==========================================")


    # ======================================================
    # LOAD
    # ======================================================

    print("\nLoading dataset...")


    df = load_data()


    print(
        f"Samples : {len(df)}"
    )


    # ======================================================
    # PREPARE
    # ======================================================

    X, y = prepare_data(
        df
    )


    print("\n==========================================")
    print("          PREDICTION FEATURES")
    print("==========================================")


    print(
        f"Features used : {len(FEATURE_COLUMNS)}"
    )


    for number, feature in enumerate(
        FEATURE_COLUMNS,
        start=1
    ):

        print(
            f"{number:2}. {feature}"
        )


    print(
        "\nSector times are excluded "
        "to avoid target leakage."
    )


    # ======================================================
    # TRAIN TEST SPLIT
    # ======================================================

    (
        X_train,
        X_test,
        y_train,
        y_test
    ) = train_test_split(

        X,
        y,

        test_size=0.20,

        random_state=42

    )


    print("\n==========================================")
    print("          TRAIN / TEST")
    print("==========================================")


    print(
        f"Training samples : {len(X_train)}"
    )

    print(
        f"Testing samples  : {len(X_test)}"
    )


    # ======================================================
    # TRAIN
    # ======================================================

    print("\n==========================================")
    print("          TRAINING MODEL")
    print("==========================================")


    model, imputer = (
        train_prediction_model(
            X_train,
            y_train
        )
    )


    print(
        "Random Forest prediction model trained."
    )


    # ======================================================
    # EVALUATION
    # ======================================================

    (
        predictions,
        mae,
        rmse,
        r2
    ) = evaluate_model(

        model,

        imputer,

        X_test,

        y_test

    )


    print("\n==========================================")
    print("          MODEL RESULTS")
    print("==========================================")


    print(
        f"MAE  : {mae:.4f} seconds"
    )

    print(
        f"RMSE : {rmse:.4f} seconds"
    )

    print(
        f"R²   : {r2:.4f}"
    )


    # ======================================================
    # PREDICTION TABLE
    # ======================================================

    results = pd.DataFrame({

        "Actual_LapTime":
            y_test.values,

        "Predicted_LapTime":
            predictions

    })


    results["Error"] = (
        results["Actual_LapTime"]
        -
        results["Predicted_LapTime"]
    )


    print("\n==========================================")
    print("          PREDICTION RESULTS")
    print("==========================================")


    print(
        results.head(10).to_string(
            index=False
        )
    )


    # ======================================================
    # EXAMPLE PREDICTION
    # ======================================================

    example_features = {

        "MaxSpeed": 330.0,

        "AvgSpeed": 220.0,

        "MinSpeed": 75.0,

        "MaxThrottle": 100.0,

        "AvgThrottle": 72.0,

        "MinThrottle": 0.0,

        "MaxBrake": 100.0,

        "AvgBrake": 20.0,

        "BrakingSamples": 120,

        "MinGear": 1,

        "MaxGear": 8,

        "MostUsedGear": 7,

        "GearChanges": 45,

        "MaxRPM": 12000,

        "AvgRPM": 9800,

        "MinRPM": 4500,

        "DRSUsage": 10.0

    }


    predicted_time = predict_lap_time(

        model,

        imputer,

        example_features

    )


    print("\n==========================================")
    print("        EXAMPLE LAP PREDICTION")
    print("==========================================")


    print(
        f"Predicted Lap Time : "
        f"{predicted_time:.3f} seconds"
    )


    # ======================================================
    # SAVE
    # ======================================================

    save_model(
        model,
        imputer
    )


    print("\n==========================================")
    print("          MODEL SAVED")
    print("==========================================")


    print(
        f"Model:\n{MODEL_FILE}"
    )


    print(
        f"\nImputer:\n{IMPUTER_FILE}"
    )


    print("\n==========================================")
    print("        PHASE 6.5 COMPLETE")
    print("==========================================")