from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import (
    train_test_split,
    KFold,
    cross_validate
)
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ==========================================================
# PROJECT PATH
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "f1_ml_features.csv"
)


# ==========================================================
# LOAD DATA
# ==========================================================

def load_data():

    if not DATA_FILE.exists():

        raise FileNotFoundError(
            f"Dataset not found:\n{DATA_FILE}"
        )

    return pd.read_csv(DATA_FILE)


# ==========================================================
# PREPARE FEATURES
# ==========================================================

def prepare_data(df):

    # Remove rows without target
    df = df.dropna(
        subset=["LapTime"]
    ).copy()

    # ------------------------------------------------------
    # IMPORTANT:
    # TelemetrySamples is removed because it can act as a
    # proxy for telemetry length rather than driving skill.
    # ------------------------------------------------------

    feature_columns = [

        "Sector1",
        "Sector2",
        "Sector3",

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

    X = df[
        feature_columns
    ].copy()

    y = df[
        "LapTime"
    ].copy()

    return X, y, feature_columns


# ==========================================================
# CREATE RANDOM FOREST PIPELINE
# ==========================================================

def create_model():

    pipeline = Pipeline([

        (
            "imputer",

            SimpleImputer(
                strategy="median"
            )
        ),

        (
            "model",

            RandomForestRegressor(

                n_estimators=200,

                max_depth=12,

                min_samples_split=2,

                min_samples_leaf=1,

                random_state=42,

                n_jobs=-1

            )
        )

    ])

    return pipeline


# ==========================================================
# TRAIN / TEST EVALUATION
# ==========================================================

def train_test_evaluation(
    X,
    y
):

    X_train, X_test, y_train, y_test = (
        train_test_split(

            X,
            y,

            test_size=0.20,

            random_state=42

        )
    )


    model = create_model()


    model.fit(
        X_train,
        y_train
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
        model,
        mae,
        rmse,
        r2
    )


# ==========================================================
# CROSS VALIDATION
# ==========================================================

def cross_validation(
    X,
    y
):

    model = create_model()


    kfold = KFold(

        n_splits=5,

        shuffle=True,

        random_state=42

    )


    scoring = {

        "MAE":
            "neg_mean_absolute_error",

        "RMSE":
            "neg_root_mean_squared_error",

        "R2":
            "r2"

    }


    results = cross_validate(

        model,

        X,

        y,

        cv=kfold,

        scoring=scoring,

        n_jobs=-1

    )


    mae_scores = (
        -results["test_MAE"]
    )

    rmse_scores = (
        -results["test_RMSE"]
    )

    r2_scores = (
        results["test_R2"]
    )


    return (
        mae_scores,
        rmse_scores,
        r2_scores
    )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    print("\n==========================================")
    print("        F1 TELEMETRY LAB")
    print("        PHASE 6.4")
    print("        MODEL EVALUATION")
    print("==========================================")


    # ======================================================
    # LOAD DATA
    # ======================================================

    print("\nLoading dataset...")

    df = load_data()

    print(
        f"Samples : {len(df)}"
    )


    # ======================================================
    # PREPARE DATA
    # ======================================================

    X, y, feature_columns = (
        prepare_data(df)
    )


    print("\n==========================================")
    print("          FEATURE CLEANUP")
    print("==========================================")


    print(
        "TelemetrySamples removed."
    )

    print(
        f"Features used : {len(feature_columns)}"
    )


    print("\nFeatures:")

    for number, feature in enumerate(
        feature_columns,
        start=1
    ):

        print(
            f"{number:2}. {feature}"
        )


    # ======================================================
    # TRAIN / TEST
    # ======================================================

    print("\n==========================================")
    print("          HOLDOUT EVALUATION")
    print("==========================================")


    (
        model,
        mae,
        rmse,
        r2
    ) = train_test_evaluation(
        X,
        y
    )


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
    # CROSS VALIDATION
    # ======================================================

    print("\n==========================================")
    print("          5-FOLD CROSS VALIDATION")
    print("==========================================")


    (
        mae_scores,
        rmse_scores,
        r2_scores
    ) = cross_validation(
        X,
        y
    )


    # ------------------------------------------------------
    # Fold results
    # ------------------------------------------------------

    for i in range(5):

        print(
            f"\nFold {i + 1}"
        )

        print(
            f"MAE  : "
            f"{mae_scores[i]:.4f} seconds"
        )

        print(
            f"RMSE : "
            f"{rmse_scores[i]:.4f} seconds"
        )

        print(
            f"R²   : "
            f"{r2_scores[i]:.4f}"
        )


    # ======================================================
    # AVERAGE RESULTS
    # ======================================================

    print("\n==========================================")
    print("          CROSS-VALIDATION RESULTS")
    print("==========================================")


    print(
        f"Average MAE  : "
        f"{mae_scores.mean():.4f} seconds"
    )

    print(
        f"Average RMSE : "
        f"{rmse_scores.mean():.4f} seconds"
    )

    print(
        f"Average R²   : "
        f"{r2_scores.mean():.4f}"
    )


    print(
        f"\nMAE Std      : "
        f"{mae_scores.std():.4f}"
    )

    print(
        f"RMSE Std     : "
        f"{rmse_scores.std():.4f}"
    )

    print(
        f"R² Std       : "
        f"{r2_scores.std():.4f}"
    )


    # ======================================================
    # INTERPRETATION
    # ======================================================

    print("\n==========================================")
    print("          EVALUATION SUMMARY")
    print("==========================================")


    print(
        "\nLower MAE and RMSE are better."
    )

    print(
        "Higher R² is better."
    )

    print(
        "\nCross-validation gives a more reliable "
        "estimate than a single train/test split."
    )


    print("\n==========================================")
    print("        PHASE 6.4 COMPLETE")
    print("==========================================")