from pathlib import Path

import pandas as pd
import numpy as np


# ==========================================================
# PROJECT PATH
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "f1_ml_features.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "driver_performance.csv"
)


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
# DRIVER PERFORMANCE
# ==========================================================

def calculate_driver_performance(df):

    # ------------------------------------------------------
    # Required columns
    # ------------------------------------------------------

    required_columns = [

        "Driver",
        "LapTime",
        "AvgSpeed",
        "MaxSpeed",
        "AvgThrottle",
        "AvgBrake",
        "GearChanges",
        "AvgRPM",
        "DRSUsage"

    ]


    missing = [

        column
        for column in required_columns
        if column not in df.columns

    ]


    if missing:

        raise ValueError(
            "Missing columns: "
            + str(missing)
        )


    # ------------------------------------------------------
    # Remove invalid lap times
    # ------------------------------------------------------

    df = df.dropna(
        subset=["LapTime"]
    ).copy()


    # ------------------------------------------------------
    # Group by driver
    # ------------------------------------------------------

    performance = (

        df.groupby("Driver")

        .agg(

            Laps=(
                "LapTime",
                "count"
            ),

            AverageLapTime=(
                "LapTime",
                "mean"
            ),

            BestLapTime=(
                "LapTime",
                "min"
            ),

            LapTimeStd=(
                "LapTime",
                "std"
            ),

            AverageSpeed=(
                "AvgSpeed",
                "mean"
            ),

            MaximumSpeed=(
                "MaxSpeed",
                "mean"
            ),

            AverageThrottle=(
                "AvgThrottle",
                "mean"
            ),

            AverageBrake=(
                "AvgBrake",
                "mean"
            ),

            AverageGearChanges=(
                "GearChanges",
                "mean"
            ),

            AverageRPM=(
                "AvgRPM",
                "mean"
            ),

            DRSUsage=(
                "DRSUsage",
                "mean"
            )

        )

        .reset_index()

    )


    # ------------------------------------------------------
    # Fill standard deviation
    # ------------------------------------------------------

    performance["LapTimeStd"] = (
        performance["LapTimeStd"]
        .fillna(0)
    )


    return performance


# ==========================================================
# NORMALIZE A METRIC
# ==========================================================

def normalize_series(
    series,
    higher_is_better=True
):

    minimum = series.min()

    maximum = series.max()


    if maximum == minimum:

        return pd.Series(
            100.0,
            index=series.index
        )


    if higher_is_better:

        normalized = (

            (series - minimum)
            /
            (maximum - minimum)

        ) * 100

    else:

        normalized = (

            (maximum - series)
            /
            (maximum - minimum)

        ) * 100


    return normalized


# ==========================================================
# CALCULATE PERFORMANCE SCORE
# ==========================================================

def calculate_score(performance):

    # ------------------------------------------------------
    # Normalize individual metrics
    # ------------------------------------------------------

    performance["LapTimeScore"] = (
        normalize_series(
            performance["AverageLapTime"],
            higher_is_better=False
        )
    )


    performance["SpeedScore"] = (
        normalize_series(
            performance["AverageSpeed"],
            higher_is_better=True
        )
    )


    performance["MaxSpeedScore"] = (
        normalize_series(
            performance["MaximumSpeed"],
            higher_is_better=True
        )
    )


    performance["ThrottleScore"] = (
        normalize_series(
            performance["AverageThrottle"],
            higher_is_better=True
        )
    )


    performance["ConsistencyScore"] = (
        normalize_series(
            performance["LapTimeStd"],
            higher_is_better=False
        )
    )


    # ------------------------------------------------------
    # Weighted performance score
    # ------------------------------------------------------

    performance["PerformanceScore"] = (

        performance["LapTimeScore"] * 0.40

        +

        performance["SpeedScore"] * 0.25

        +

        performance["MaxSpeedScore"] * 0.10

        +

        performance["ThrottleScore"] * 0.10

        +

        performance["ConsistencyScore"] * 0.15

    )


    # ------------------------------------------------------
    # Round score
    # ------------------------------------------------------

    performance["PerformanceScore"] = (
        performance["PerformanceScore"]
        .round(2)
    )


    # ------------------------------------------------------
    # Ranking
    # ------------------------------------------------------

    performance = performance.sort_values(

        by="PerformanceScore",

        ascending=False

    ).reset_index(
        drop=True
    )


    performance.insert(

        0,

        "Rank",

        range(
            1,
            len(performance) + 1
        )

    )


    return performance


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    print("\n==========================================")
    print("        F1 TELEMETRY LAB")
    print("        PHASE 6.6")
    print("        DRIVER PERFORMANCE")
    print("==========================================")


    # ======================================================
    # LOAD
    # ======================================================

    print("\nLoading feature dataset...")

    df = load_data()


    print(
        f"Total samples : {len(df)}"
    )


    print(
        f"Drivers       : "
        f"{df['Driver'].nunique()}"
    )


    # ======================================================
    # CALCULATE PERFORMANCE
    # ======================================================

    performance = (
        calculate_driver_performance(
            df
        )
    )


    # ======================================================
    # CALCULATE SCORE
    # ======================================================

    performance = (
        calculate_score(
            performance
        )
    )


    # ======================================================
    # DISPLAY
    # ======================================================

    print("\n==========================================")
    print("          DRIVER PERFORMANCE")
    print("==========================================")


    display_columns = [

        "Rank",
        "Driver",
        "Laps",
        "AverageLapTime",
        "BestLapTime",
        "LapTimeStd",
        "AverageSpeed",
        "MaximumSpeed",
        "AverageThrottle",
        "PerformanceScore"

    ]


    print(

        performance[
            display_columns
        ].to_string(
            index=False
        )

    )


    # ======================================================
    # SAVE
    # ======================================================

    performance.to_csv(

        OUTPUT_FILE,

        index=False

    )


    print("\n==========================================")
    print("          PERFORMANCE SAVED")
    print("==========================================")


    print(
        f"File:\n{OUTPUT_FILE}"
    )


    print("\n==========================================")
    print("        PHASE 6.6 COMPLETE")
    print("==========================================")