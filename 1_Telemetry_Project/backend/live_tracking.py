from pathlib import Path
from datetime import datetime
import time

import pandas as pd

from fastf1_connection import get_fastf1


# ==========================================================
# CONFIGURATION
# ==========================================================

YEAR = 2026

# Change this to the current/desired event when needed
EVENT = "Monza"

SESSION_TYPE = "R"

UPDATE_INTERVAL = 2


# ==========================================================
# LOAD SESSION
# ==========================================================

def load_session(
    year,
    event,
    session_type
):

    fastf1 = get_fastf1()

    print(
        f"\nLoading {year} {event} - {session_type}"
    )

    session = fastf1.get_session(
        year,
        event,
        session_type
    )

    session.load()

    print(
        "Session loaded successfully!"
    )

    return session


# ==========================================================
# GET LATEST TELEMETRY
# ==========================================================

def get_latest_driver_data(
    session,
    driver
):

    driver_laps = (
        session.laps
        .pick_drivers(driver)
    )

    if driver_laps.empty:

        return None


    # Get latest available lap
    latest_lap = driver_laps.iloc[-1]


    try:

        telemetry = (
            latest_lap
            .get_telemetry()
        )

    except Exception:

        return None


    if telemetry.empty:

        return None


    latest = telemetry.iloc[-1]


    # ------------------------------------------------------
    # Safe value helper
    # ------------------------------------------------------

    def get_value(
        column,
        default=0
    ):

        if column not in telemetry.columns:

            return default


        value = latest[column]


        if pd.isna(value):

            return default


        return value


    # ------------------------------------------------------
    # Driver data
    # ------------------------------------------------------

    data = {

        "driver": driver,

        "lap": int(
            latest_lap["LapNumber"]
        ),

        "speed": float(
            get_value("Speed")
        ),

        "throttle": float(
            get_value("Throttle")
        ),

        "brake": float(
            get_value("Brake")
        ),

        "gear": int(
            get_value("nGear")
        ),

        "rpm": int(
            get_value("RPM")
        ),

        "drs": int(
            get_value("DRS")
        ),

        "x": float(
            get_value("X")
        ),

        "y": float(
            get_value("Y")
        )

    }


    return data


# ==========================================================
# GET ALL DRIVERS
# ==========================================================

def get_live_data(session):

    drivers = (
        session.drivers
    )


    live_data = []


    for driver in drivers:

        try:

            data = get_latest_driver_data(

                session,

                driver

            )


            if data is not None:

                live_data.append(
                    data
                )


        except Exception as error:

            print(
                f"Driver {driver} error: "
                f"{error}"
            )


    return live_data


# ==========================================================
# DISPLAY LIVE DATA
# ==========================================================

def display_live_data(
    live_data
):

    print("\n==========================================")
    print("             LIVE TELEMETRY")
    print("==========================================")


    if not live_data:

        print(
            "No live telemetry available."
        )

        return


    print(

        f"{'Driver':<8}"
        f"{'Lap':<6}"
        f"{'Speed':<10}"
        f"{'Throttle':<12}"
        f"{'Brake':<8}"
        f"{'Gear':<7}"
        f"{'RPM':<8}"
        f"{'DRS':<6}"

    )


    print(
        "-" * 65
    )


    for data in live_data:

        print(

            f"{data['driver']:<8}"
            f"{data['lap']:<6}"
            f"{data['speed']:<10.1f}"
            f"{data['throttle']:<12.1f}"
            f"{data['brake']:<8.1f}"
            f"{data['gear']:<7}"
            f"{data['rpm']:<8}"
            f"{data['drs']:<6}"

        )


# ==========================================================
# LIVE TRACKING LOOP
# ==========================================================

def start_live_tracking(
    session,
    iterations=5
):

    print("\n==========================================")
    print("          LIVE TRACKING STARTED")
    print("==========================================")


    for iteration in range(
        iterations
    ):

        print(
            f"\nUpdate "
            f"{iteration + 1}/{iterations}"
        )


        live_data = get_live_data(
            session
        )


        display_live_data(
            live_data
        )


        if iteration < iterations - 1:

            time.sleep(
                UPDATE_INTERVAL
            )


    print("\n==========================================")
    print("          LIVE TRACKING ENDED")
    print("==========================================")


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    print("\n==========================================")
    print("        F1 TELEMETRY LAB")
    print("        PHASE 7.3")
    print("        LIVE TRACKING")
    print("==========================================")


    print(
        f"\nCurrent system time: "
        f"{datetime.now()}"
    )


    # ------------------------------------------------------
    # LOAD SESSION
    # ------------------------------------------------------

    try:

        session = load_session(

            YEAR,

            EVENT,

            SESSION_TYPE

        )


    except Exception as error:

        print("\n==========================================")
        print("        SESSION ERROR")
        print("==========================================")

        print(error)

        print(
            "\nLive tracking cannot start "
            "without session data."
        )

        raise SystemExit(1)


    # ------------------------------------------------------
    # START LIVE TRACKING
    # ------------------------------------------------------

    start_live_tracking(

        session,

        iterations=5

    )


    print("\n==========================================")
    print("        PHASE 7.3 COMPLETE")
    print("==========================================")