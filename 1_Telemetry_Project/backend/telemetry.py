from fastf1_connection import get_fastf1


def get_lap_telemetry(session, driver, lap_number):
    """
    Extract telemetry for a specific driver's lap.
    """

    # Get driver's laps
    driver_laps = session.laps.pick_drivers(driver)

    # Get requested lap
    lap_data = driver_laps.pick_laps(lap_number)

    if lap_data.empty:
        raise ValueError(
            f"Lap {lap_number} not found for driver {driver}"
        )

    # Get first matching lap
    lap = lap_data.iloc[0]

    # Extract telemetry
    telemetry = lap.get_telemetry()

    return lap, telemetry


if __name__ == "__main__":

    fastf1 = get_fastf1()

    # ==========================================
    # SESSION
    # ==========================================

    session = fastf1.get_session(
        2024,
        "Monza",
        "R"
    )

    session.load()

    # ==========================================
    # DRIVER + LAP
    # ==========================================

    driver = "VER"
    lap_number = 20

    lap, telemetry = get_lap_telemetry(
        session,
        driver,
        lap_number
    )

    # ==========================================
    # LAP INFORMATION
    # ==========================================

    print("\n================================")
    print("        LAP INFORMATION")
    print("================================")

    print("Driver:", driver)
    print("Lap:", lap["LapNumber"])
    print("Lap Time:", lap["LapTime"])

    # ==========================================
    # TELEMETRY COLUMNS
    # ==========================================

    print("\n================================")
    print("       TELEMETRY COLUMNS")
    print("================================")

    print(telemetry.columns.tolist())

    # ==========================================
    # TELEMETRY DATA
    # ==========================================

    print("\n================================")
    print("       TELEMETRY SAMPLE")
    print("================================")

    print(telemetry.head(10).to_string(index=False))