import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


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
# LOAD DATASET
# ==========================================================

def load_dataset():

    if not DATA_FILE.exists():

        raise FileNotFoundError(
            f"Dataset not found:\n{DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE)

    return df


# ==========================================================
# CLEAN DATASET
# ==========================================================

def clean_dataset(df):

    # Remove rows where target is missing
    df = df.dropna(
        subset=["LapTime"]
    ).copy()

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Reset index
    df = df.reset_index(
        drop=True
    )

    return df


# ==========================================================
# PREPARE FEATURES
# ==========================================================

def prepare_features(df):

    # ------------------------------------------------------
    # TARGET
    # ------------------------------------------------------

    y = df["LapTime"]


    # ------------------------------------------------------
    # FEATURES
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

        "DRSUsage",

        "TelemetrySamples"

    ]


    # Check missing columns
    missing_columns = [

        column
        for column in feature_columns
        if column not in df.columns

    ]


    if missing_columns:

        raise ValueError(
            "Missing feature columns: "
            + str(missing_columns)
        )


    X = df[
        feature_columns
    ].copy()


    return X, y, feature_columns


# ==========================================================
# HANDLE MISSING VALUES
# ==========================================================

def handle_missing_values(X):

    imputer = SimpleImputer(
        strategy="median"
    )

    X_imputed = imputer.fit_transform(
        X
    )

    X_imputed = pd.DataFrame(
        X_imputed,
        columns=X.columns
    )

    return X_imputed, imputer


# ==========================================================
# TRAIN / TEST SPLIT
# ==========================================================

def split_dataset(
    X,
    y,
    test_size=0.20,
    random_state=42
):

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state
        )
    )

    return (
        X_train,
        X_test,
        y_train,
        y_test
    )


# ==========================================================
# STANDARDIZATION
# ==========================================================

def scale_features(
    X_train,
    X_test
):

    scaler = StandardScaler()


    X_train_scaled = scaler.fit_transform(
        X_train
    )


    X_test_scaled = scaler.transform(
        X_test
    )


    X_train_scaled = pd.DataFrame(
        X_train_scaled,
        columns=X_train.columns
    )


    X_test_scaled = pd.DataFrame(
        X_test_scaled,
        columns=X_test.columns
    )


    return (
        X_train_scaled,
        X_test_scaled,
        scaler
    )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    print("\n==========================================")
    print("        F1 TELEMETRY LAB")
    print("        PHASE 6.2")
    print("        DATASET PREPARATION")
    print("==========================================")


    # ------------------------------------------------------
    # LOAD
    # ------------------------------------------------------

    print("\nLoading dataset...")

    df = load_dataset()

    print(
        f"Original samples : {len(df)}"
    )

    print(
        f"Original columns : {len(df.columns)}"
    )


    # ------------------------------------------------------
    # CLEAN
    # ------------------------------------------------------

    df = clean_dataset(df)

    print("\nAfter cleaning:")

    print(
        f"Samples : {len(df)}"
    )


    # ------------------------------------------------------
    # FEATURES
    # ------------------------------------------------------

    X, y, feature_columns = (
        prepare_features(df)
    )


    print("\n==========================================")
    print("             FEATURES")
    print("==========================================")


    for number, column in enumerate(
        feature_columns,
        start=1
    ):

        print(
            f"{number:2}. {column}"
        )


    print(
        f"\nTotal input features : "
        f"{len(feature_columns)}"
    )


    # ------------------------------------------------------
    # MISSING VALUES
    # ------------------------------------------------------

    print("\n==========================================")
    print("          MISSING VALUES")
    print("==========================================")


    print(
        X.isna().sum()
    )


    X, imputer = (
        handle_missing_values(X)
    )


    print(
        "\nMissing values handled."
    )


    # ------------------------------------------------------
    # TARGET
    # ------------------------------------------------------

    print("\n==========================================")
    print("              TARGET")
    print("==========================================")


    print(
        "Target : LapTime"
    )

    print(
        f"Target samples : {len(y)}"
    )


    # ------------------------------------------------------
    # TRAIN TEST SPLIT
    # ------------------------------------------------------

    (
        X_train,
        X_test,
        y_train,
        y_test
    ) = split_dataset(
        X,
        y
    )


    print("\n==========================================")
    print("          TRAIN / TEST SPLIT")
    print("==========================================")


    print(
        f"Training samples : "
        f"{len(X_train)}"
    )

    print(
        f"Testing samples  : "
        f"{len(X_test)}"
    )


    # ------------------------------------------------------
    # STANDARDIZATION
    # ------------------------------------------------------

    (
        X_train_scaled,
        X_test_scaled,
        scaler
    ) = scale_features(
        X_train,
        X_test
    )


    print("\n==========================================")
    print("          STANDARDIZATION")
    print("==========================================")


    print(
        "Feature standardization completed."
    )


    # ------------------------------------------------------
    # FINAL SHAPES
    # ------------------------------------------------------

    print("\n==========================================")
    print("             FINAL DATA")
    print("==========================================")


    print(
        "X_train shape :",
        X_train_scaled.shape
    )

    print(
        "X_test shape  :",
        X_test_scaled.shape
    )

    print(
        "y_train shape :",
        y_train.shape
    )

    print(
        "y_test shape  :",
        y_test.shape
    )


    # ------------------------------------------------------
    # SAMPLE
    # ------------------------------------------------------

    print("\n==========================================")
    print("        TRAINING DATA SAMPLE")
    print("==========================================")


    print(
        X_train_scaled.head()
    )


    print("\n==========================================")
    print("        PHASE 6.2 COMPLETE")
    print("==========================================")