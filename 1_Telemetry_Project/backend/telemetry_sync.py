import pandas as pd


# ==========================================================
# TELEMETRY SYNCHRONIZER
# ==========================================================

class TelemetrySynchronizer:
    """
    Synchronizes playback with the actual FastF1
    telemetry timestamps.
    """

    def __init__(self, telemetry):

        self.telemetry = (
            telemetry
            .copy()
            .reset_index(drop=True)
        )

        # --------------------------------------------------
        # CHECK TIME COLUMN
        # --------------------------------------------------

        if "SessionTime" not in self.telemetry.columns:
            raise ValueError(
                "SessionTime column is missing."
            )

        # --------------------------------------------------
        # CONVERT TIME TO SECONDS
        # --------------------------------------------------

        self.time_seconds = (
            self.telemetry["SessionTime"]
            .apply(
                lambda x: x.total_seconds()
                if pd.notna(x)
                else None
            )
        )

        # Remove invalid timestamps
        valid = self.time_seconds.notna()

        self.telemetry = (
            self.telemetry.loc[valid]
            .reset_index(drop=True)
        )

        self.time_seconds = (
            self.time_seconds.loc[valid]
            .reset_index(drop=True)
        )

        # --------------------------------------------------
        # MAKE TIME RELATIVE TO START
        # --------------------------------------------------

        self.time_seconds = (
            self.time_seconds
            - self.time_seconds.iloc[0]
        )

        # --------------------------------------------------
        # TOTAL LAP TIME
        # --------------------------------------------------

        self.total_time = (
            self.time_seconds.iloc[-1]
        )


    # ======================================================
    # GET TELEMETRY AT PLAYBACK TIME
    # ======================================================

    def get_sample(self, playback_time):

        # Keep playback inside the lap
        playback_time = max(
            0,
            min(
                playback_time,
                self.total_time
            )
        )

        # Find closest telemetry sample
        index = (
            (self.time_seconds - playback_time)
            .abs()
            .idxmin()
        )

        return (
            self.telemetry.iloc[index],
            index
        )


    # ======================================================
    # GET POSITION
    # ======================================================

    def get_position(self, playback_time):

        sample, index = (
            self.get_sample(
                playback_time
            )
        )

        return (
            sample["X"],
            sample["Y"],
            index
        )


    # ======================================================
    # GET TELEMETRY VALUES
    # ======================================================

    def get_values(self, playback_time):

        sample, index = (
            self.get_sample(
                playback_time
            )
        )

        return {
            "index": index,
            "time": playback_time,
            "speed": sample["Speed"],
            "throttle": sample["Throttle"],
            "brake": sample["Brake"],
            "gear": sample["nGear"],
            "rpm": sample["RPM"],
            "drs": sample["DRS"],
            "x": sample["X"],
            "y": sample["Y"]
        }


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    import fastf1

    from pathlib import Path

    # ------------------------------------------------------
    # CACHE
    # ------------------------------------------------------

    BASE_DIR = (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )

    CACHE_DIR = (
        BASE_DIR
        / "data"
        / "fastf1_cache"
    )

    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    fastf1.Cache.enable_cache(
        str(CACHE_DIR)
    )

    # ------------------------------------------------------
    # LOAD SESSION
    # ------------------------------------------------------

    print("\n================================")
    print("   TELEMETRY SYNCHRONIZATION")
    print("================================")

    session = fastf1.get_session(
        2024,
        "Monza",
        "R"
    )

    session.load()

    # ------------------------------------------------------
    # GET LAP
    # ------------------------------------------------------

    laps = session.laps.pick_drivers(
        "VER"
    )

    lap_data = laps[
        laps["LapNumber"] == 20
    ]

    if lap_data.empty:

        raise ValueError(
            "Lap 20 not found."
        )

    lap = lap_data.iloc[0]

    telemetry = (
        lap
        .get_telemetry()
        .dropna(
            subset=["X", "Y"]
        )
        .reset_index(drop=True)
    )

    print(
        f"\nTelemetry samples: "
        f"{len(telemetry)}"
    )

    # ------------------------------------------------------
    # CREATE SYNCHRONIZER
    # ------------------------------------------------------

    synchronizer = (
        TelemetrySynchronizer(
            telemetry
        )
    )

    print(
        f"Lap telemetry duration: "
        f"{synchronizer.total_time:.3f} seconds"
    )

    # ------------------------------------------------------
    # TEST DIFFERENT TIMES
    # ------------------------------------------------------

    test_times = [
        0,
        1,
        5,
        10,
        20,
        synchronizer.total_time
    ]

    print(
        "\n================================"
    )

    print(
        "       SYNCHRONIZATION TEST"
    )

    print(
        "================================"
    )

    for time in test_times:

        values = (
            synchronizer
            .get_values(time)
        )

        print(
            f"\nTime: {time:.2f}s"
        )

        print(
            f"Sample: "
            f"{values['index']}"
        )

        print(
            f"Position: "
            f"({values['x']:.2f}, "
            f"{values['y']:.2f})"
        )

        print(
            f"Speed: "
            f"{values['speed']:.0f} km/h"
        )

        print(
            f"Throttle: "
            f"{values['throttle']:.0f}%"
        )

        print(
            f"Brake: "
            f"{values['brake']:.0f}"
        )

        print(
            f"Gear: "
            f"{values['gear']:.0f}"
        )

        print(
            f"RPM: "
            f"{values['rpm']:.0f}"
        )

        print(
            f"DRS: "
            f"{values['drs']:.0f}"
        )