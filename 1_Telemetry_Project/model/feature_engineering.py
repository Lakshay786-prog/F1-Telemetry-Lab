import sys
from pathlib import Path

import pandas as pd


# ==========================================================
# PROJECT PATH
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


# ==========================================================
# BACKEND IMPORTS
# ==========================================================

from backend.fastf1_connection import get_fastf1


# ==========================================================
# FEATURE EXTRACTION FOR ONE LAP
# ==========================================================

def extract_lap_features(session, driver, lap_number):

    # ------------------------------------------------------
    # GET DRIVER LAPS
    # ------------------------------------------------------

    driver_laps = session.laps.pick_drivers(driver)

    lap_data = driver_laps[
        driver_laps["LapNumber"] == lap_number
    ]

    if lap_data.empty:

        raise ValueError(
            f"Lap {lap_number} not found for {driver}"
        )

    # First matching lap
    lap = lap_data.iloc[0]


    # ------------------------------------------------------
    # GET TELEMETRY
    # ------------------------------------------------------

    telemetry = lap.get_telemetry()


    if telemetry.empty:

        raise ValueError(
            f"No telemetry available for "
            f"{driver}, lap {lap_number}"
        )


    # ======================================================
    # SPEED
    # ======================================================

    speed = telemetry["Speed"].dropna()

    maximum_speed = speed.max()
    average_speed = speed.mean()
    minimum_speed = speed.min()


    # ======================================================
    # THROTTLE
    # ======================================================

    throttle = telemetry["Throttle"].dropna()

    maximum_throttle = throttle.max()
    average_throttle = throttle.mean()
    minimum_throttle = throttle.min()


    # ======================================================
    # BRAKE
    # ======================================================

    brake = telemetry["Brake"].fillna(0)

    maximum_brake = brake.max()
    average_brake = brake.mean()

    braking_samples = int(
        (brake > 0).sum()
    )


    # ======================================================
    # GEAR
    # ======================================================

    gear = telemetry["nGear"].dropna()

    gear = gear[gear > 0]

    minimum_gear = gear.min()
    maximum_gear = gear.max()

    most_used_gear = (
        gear.mode().iloc[0]
        if not gear.empty
        else 0
    )


    # Count gear changes
    if len(gear) > 1:

        gear_changes = int(
            (gear.diff() != 0).sum()
        )

    else:

        gear_changes = 0


    # ======================================================
    # RPM
    # ======================================================

    rpm = telemetry["RPM"].dropna()

    maximum_rpm = rpm.max()
    average_rpm = rpm.mean()
    minimum_rpm = rpm.min()


    # ======================================================
    # DRS
    # ======================================================

    if "DRS" in telemetry.columns:

        drs = telemetry["DRS"].fillna(0)

        drs_active_samples = int(
            (drs >= 10).sum()
        )

        total_drs_samples = len(drs)

        if total_drs_samples > 0:

            drs_usage = (
                drs_active_samples /
                total_drs_samples
            ) * 100

        else:

            drs_usage = 0

    else:

        drs_usage = 0


    # ======================================================
    # LAP TIME
    # ======================================================

    lap_time = lap["LapTime"]


    # Convert lap time to seconds
    if pd.notna(lap_time):

        lap_time_seconds = (
            lap_time.total_seconds()
        )

    else:

        lap_time_seconds = None


    # ======================================================
    # SECTOR TIMES
    # ======================================================

    sector_1 = lap["Sector1Time"]
    sector_2 = lap["Sector2Time"]
    sector_3 = lap["Sector3Time"]


    if pd.notna(sector_1):
        sector_1 = sector_1.total_seconds()
    else:
        sector_1 = None


    if pd.notna(sector_2):
        sector_2 = sector_2.total_seconds()
    else:
        sector_2 = None


    if pd.notna(sector_3):
        sector_3 = sector_3.total_seconds()
    else:
        sector_3 = None


    # ======================================================
    # CREATE FEATURE DICTIONARY
    # ======================================================

    features = {

        "Driver":
            driver,

        "Lap":
            int(lap["LapNumber"]),

        "LapTime":
            lap_time_seconds,

        "Sector1":
            sector_1,

        "Sector2":
            sector_2,

        "Sector3":
            sector_3,

        "MaxSpeed":
            maximum_speed,

        "AvgSpeed":
            average_speed,

        "MinSpeed":
            minimum_speed,

        "MaxThrottle":
            maximum_throttle,

        "AvgThrottle":
            average_throttle,

        "MinThrottle":
            minimum_throttle,

        "MaxBrake":
            maximum_brake,

        "AvgBrake":
            average_brake,

        "BrakingSamples":
            braking_samples,

        "MinGear":
            minimum_gear,

        "MaxGear":
            maximum_gear,

        "MostUsedGear":
            most_used_gear,

        "GearChanges":
            gear_changes,

        "MaxRPM":
            maximum_rpm,

        "AvgRPM":
            average_rpm,

        "MinRPM":
            minimum_rpm,

        "DRSUsage":
            drs_usage,

        "TelemetrySamples":
            len(telemetry)
    }


    return features


# ==========================================================
# CREATE DATASET FROM MULTIPLE LAPS
# ==========================================================

def create_feature_dataset(
    session,
    drivers,
    start_lap=1,
    end_lap=None
):

    rows = []


    for driver in drivers:

        print(
            f"\nProcessing driver: {driver}"
        )


        driver_laps = (
            session.laps
            .pick_drivers(driver)
        )


        if driver_laps.empty:

            print(
                f"No laps found for {driver}"
            )

            continue


        available_laps = sorted(
            driver_laps["LapNumber"]
            .dropna()
            .astype(int)
            .unique()
        )


        if end_lap is not None:

            available_laps = [

                lap
                for lap in available_laps

                if start_lap <= lap <= end_lap

            ]

        else:

            available_laps = [

                lap
                for lap in available_laps

                if lap >= start_lap

            ]


        for lap_number in available_laps:

            try:

                features = extract_lap_features(
                    session,
                    driver,
                    lap_number
                )

                rows.append(features)

                print(
                    f"  Lap {lap_number} ✓"
                )


            except Exception as error:

                print(
                    f"  Lap {lap_number} skipped: "
                    f"{error}"
                )


    return pd.DataFrame(rows)


# ==========================================================
# MAIN PROGRAM
# ==========================================================

if __name__ == "__main__":

    print("\n==========================================")
    print("        F1 TELEMETRY LAB")
    print("        PHASE 6 - ML")
    print("        FEATURE ENGINEERING")
    print("==========================================")


    # ======================================================
    # FASTF1
    # ======================================================

    fastf1 = get_fastf1()


    # ======================================================
    # SESSION
    # ======================================================

    YEAR = 2024

    RACE = "Monza"

    SESSION_TYPE = "R"


    print(
        f"\nLoading:"
        f" {YEAR} {RACE} - {SESSION_TYPE}"
    )


    session = fastf1.get_session(
        YEAR,
        RACE,
        SESSION_TYPE
    )


    session.load()


    print(
        "\nSession loaded successfully!"
    )


    # ======================================================
    # DRIVERS
    # ======================================================

    drivers = [

        "VER",
        "LEC",
        "NOR",
        "PIA",
        "HAM"

    ]


    # ======================================================
    # CREATE FEATURES
    # ======================================================

    dataset = create_feature_dataset(

        session,

        drivers,

        start_lap=1,

        end_lap=20

    )


    # ======================================================
    # DISPLAY DATASET
    # ======================================================

    print("\n==========================================")
    print("          FEATURE DATASET")
    print("==========================================")


    if dataset.empty:

        print(
            "No feature data was created."
        )

    else:

        print(
            dataset.to_string(
                index=False
            )
        )


        # ==================================================
        # SAVE DATASET
        # ==================================================

        output_directory = (
            PROJECT_ROOT / "data"
        )

        output_directory.mkdir(
            exist_ok=True
        )


        output_file = (
            output_directory /
            "f1_ml_features.csv"
        )


        dataset.to_csv(
            output_file,
            index=False
        )


        print(
            "\n=========================================="
        )

        print(
            f"Dataset saved to:\n{output_file}"
        )

        print(
            f"\nTotal samples: {len(dataset)}"
        )

        print(
            f"Total features: {len(dataset.columns)}"
        )