from pathlib import Path

import pandas as pd


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
    / "driver_comparison.csv"
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
# GET DRIVER STATISTICS
# ==========================================================

def get_driver_stats(df, driver):

    driver_data = df[
        df["Driver"] == driver
    ].copy()

    if driver_data.empty:

        raise ValueError(
            f"Driver '{driver}' not found."
        )

    stats = {

        "Driver":
            driver,

        "Laps":
            len(driver_data),

        "Average Lap Time":
            driver_data["LapTime"].mean(),

        "Best Lap Time":
            driver_data["LapTime"].min(),

        "Lap Time Std":
            driver_data["LapTime"].std(),

        "Average Speed":
            driver_data["AvgSpeed"].mean(),

        "Maximum Speed":
            driver_data["MaxSpeed"].mean(),

        "Average Throttle":
            driver_data["AvgThrottle"].mean(),

        "Average Brake":
            driver_data["AvgBrake"].mean(),

        "Average Gear Changes":
            driver_data["GearChanges"].mean(),

        "Average RPM":
            driver_data["AvgRPM"].mean(),

        "DRS Usage":
            driver_data["DRSUsage"].mean()

    }

    return stats


# ==========================================================
# COMPARE DRIVERS
# ==========================================================

def compare_drivers(
    df,
    driver1,
    driver2
):

    stats1 = get_driver_stats(
        df,
        driver1
    )

    stats2 = get_driver_stats(
        df,
        driver2
    )

    comparison = pd.DataFrame({

        driver1: stats1,

        driver2: stats2

    })

    return comparison


# ==========================================================
# DETERMINE WINNER
# ==========================================================

def determine_winners(
    stats1,
    stats2
):

    results = {}


    # ------------------------------------------------------
    # Lower is better
    # ------------------------------------------------------

    if (
        stats1["Average Lap Time"]
        <
        stats2["Average Lap Time"]
    ):

        results["Average Lap Time"] = (
            stats1["Driver"]
        )

    else:

        results["Average Lap Time"] = (
            stats2["Driver"]
        )


    if (
        stats1["Best Lap Time"]
        <
        stats2["Best Lap Time"]
    ):

        results["Best Lap Time"] = (
            stats1["Driver"]
        )

    else:

        results["Best Lap Time"] = (
            stats2["Driver"]
        )


    # ------------------------------------------------------
    # Higher is better
    # ------------------------------------------------------

    if (
        stats1["Average Speed"]
        >
        stats2["Average Speed"]
    ):

        results["Average Speed"] = (
            stats1["Driver"]
        )

    else:

        results["Average Speed"] = (
            stats2["Driver"]
        )


    if (
        stats1["Maximum Speed"]
        >
        stats2["Maximum Speed"]
    ):

        results["Maximum Speed"] = (
            stats1["Driver"]
        )

    else:

        results["Maximum Speed"] = (
            stats2["Driver"]
        )


    if (
        stats1["Average Throttle"]
        >
        stats2["Average Throttle"]
    ):

        results["Average Throttle"] = (
            stats1["Driver"]
        )

    else:

        results["Average Throttle"] = (
            stats2["Driver"]
        )


    if (
        stats1["DRS Usage"]
        >
        stats2["DRS Usage"]
    ):

        results["DRS Usage"] = (
            stats1["Driver"]
        )

    else:

        results["DRS Usage"] = (
            stats2["Driver"]
        )


    # ------------------------------------------------------
    # Consistency
    # Lower standard deviation = more consistent
    # ------------------------------------------------------

    if (
        stats1["Lap Time Std"]
        <
        stats2["Lap Time Std"]
    ):

        results["Consistency"] = (
            stats1["Driver"]
        )

    else:

        results["Consistency"] = (
            stats2["Driver"]
        )


    return results


# ==========================================================
# ALL DRIVER SUMMARY
# ==========================================================

def create_driver_summary(df):

    rows = []

    drivers = sorted(
        df["Driver"]
        .dropna()
        .unique()
    )


    for driver in drivers:

        stats = get_driver_stats(
            df,
            driver
        )

        rows.append(stats)


    summary = pd.DataFrame(
        rows
    )


    # ------------------------------------------------------
    # Rank by average lap time
    # ------------------------------------------------------

    summary = summary.sort_values(

        by="Average Lap Time",

        ascending=True

    ).reset_index(
        drop=True
    )


    summary.insert(

        0,

        "Rank",

        range(
            1,
            len(summary) + 1
        )

    )


    return summary


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    print("\n==========================================")
    print("        F1 TELEMETRY LAB")
    print("        PHASE 6.7")
    print("        DRIVER COMPARISON")
    print("==========================================")


    # ======================================================
    # LOAD
    # ======================================================

    print("\nLoading dataset...")

    df = load_data()


    print(
        f"Total samples : {len(df)}"
    )


    drivers = sorted(
        df["Driver"]
        .dropna()
        .unique()
    )


    print(
        f"Drivers : {list(drivers)}"
    )


    # ======================================================
    # SELECT DRIVERS
    # ======================================================

    driver1 = "VER"
    driver2 = "LEC"


    print("\n==========================================")
    print("          SELECTED DRIVERS")
    print("==========================================")


    print(
        f"Driver 1 : {driver1}"
    )

    print(
        f"Driver 2 : {driver2}"
    )


    # ======================================================
    # GET STATISTICS
    # ======================================================

    stats1 = get_driver_stats(
        df,
        driver1
    )

    stats2 = get_driver_stats(
        df,
        driver2
    )


    # ======================================================
    # COMPARISON
    # ======================================================

    comparison = compare_drivers(

        df,

        driver1,

        driver2

    )


    print("\n==========================================")
    print("          DRIVER COMPARISON")
    print("==========================================")


    print(
        comparison.to_string()
    )


    # ======================================================
    # WINNERS
    # ======================================================

    winners = determine_winners(

        stats1,

        stats2

    )


    print("\n==========================================")
    print("          COMPARISON WINNERS")
    print("==========================================")


    for metric, winner in winners.items():

        print(
            f"{metric:<25} : {winner}"
        )


    # ======================================================
    # ALL DRIVER SUMMARY
    # ======================================================

    summary = create_driver_summary(
        df
    )


    print("\n==========================================")
    print("        ALL DRIVER SUMMARY")
    print("==========================================")


    display_columns = [

        "Rank",
        "Driver",
        "Laps",
        "Average Lap Time",
        "Best Lap Time",
        "Lap Time Std",
        "Average Speed",
        "Maximum Speed",
        "Average Throttle",
        "Average Brake",
        "Average Gear Changes",
        "Average RPM",
        "DRS Usage"

    ]


    print(

        summary[
            display_columns
        ].to_string(
            index=False
        )

    )


    # ======================================================
    # SAVE
    # ======================================================

    summary.to_csv(

        OUTPUT_FILE,

        index=False

    )


    print("\n==========================================")
    print("          DATA SAVED")
    print("==========================================")


    print(
        f"File:\n{OUTPUT_FILE}"
    )


    print("\n==========================================")
    print("        PHASE 6.7 COMPLETE")
    print("==========================================")