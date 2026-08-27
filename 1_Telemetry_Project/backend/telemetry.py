from fastf1_connection import get_fastf1


# ==========================================================
# GET LAP TELEMETRY
# ==========================================================

def get_lap_telemetry(session, driver, lap_number):
    """
    Extract telemetry for a specific driver's lap.

    Parameters
    ----------
    session : FastF1 session
        Loaded FastF1 session.

    driver : str
        Driver abbreviation, e.g. 'VER'.

    lap_number : int
        Requested lap number.

    Returns
    -------
    lap : pandas Series
        Information about the selected lap.

    telemetry : pandas DataFrame
        Telemetry data for the selected lap.
    """

    # Get driver's laps
    driver_laps = session.laps.pick_drivers(driver)

    # Get requested lap
    lap_data = driver_laps.pick_laps(lap_number)

    # Check whether lap exists
    if lap_data.empty:
        raise ValueError(
            f"Lap {lap_number} not found for driver {driver}"
        )

    # Get first matching lap
    lap = lap_data.iloc[0]

    # Extract telemetry
    telemetry = lap.get_telemetry()

    return lap, telemetry


# ==========================================================
# SPEED ANALYSIS
# ==========================================================

def analyze_speed(telemetry):
    """
    Analyze speed telemetry.

    Returns
    -------
    dict
        Maximum, average and minimum speed.
    """

    # Check that Speed exists
    if "Speed" not in telemetry.columns:
        raise ValueError(
            "Speed data is not available in telemetry."
        )

    speed = telemetry["Speed"]

    analysis = {
        "maximum_speed": speed.max(),
        "average_speed": speed.mean(),
        "minimum_speed": speed.min()
    }

    return analysis

# ==========================================================
# THROTTLE ANALYSIS
# ==========================================================

def analyze_throttle(telemetry):
    """
    Analyze throttle telemetry.

    Returns
    -------
    dict
        Maximum, average and minimum throttle.
    """

    if "Throttle" not in telemetry.columns:
        raise ValueError(
            "Throttle data is not available in telemetry."
        )

    throttle = telemetry["Throttle"]

    analysis = {
        "maximum_throttle": throttle.max(),
        "average_throttle": throttle.mean(),
        "minimum_throttle": throttle.min()
    }

    return analysis

# ==========================================================
# BRAKE ANALYSIS
# ==========================================================

def analyze_brake(telemetry):
    """
    Analyze brake telemetry.

    Returns
    -------
    dict
        Brake statistics and braking events.
    """

    if "Brake" not in telemetry.columns:
        raise ValueError(
            "Brake data is not available in telemetry."
        )

    brake = telemetry["Brake"].fillna(0)

    # Number of telemetry samples where braking occurred
    braking_samples = (brake > 0).sum()

    analysis = {
        "maximum_brake": brake.max(),
        "average_brake": brake.mean(),
        "braking_samples": braking_samples
    }

    return analysis

# ==========================================================
# GEAR ANALYSIS
# ==========================================================

def analyze_gear(telemetry):
    """
    Analyze gear telemetry.

    Returns
    -------
    dict
        Gear statistics and gear changes.
    """

    if "nGear" not in telemetry.columns:
        raise ValueError(
            "Gear data is not available in telemetry."
        )

    gear = telemetry["nGear"].fillna(0)

    # Remove invalid gear values
    gear = gear[gear > 0]

    if gear.empty:
        raise ValueError(
            "No valid gear data available."
        )

    # Count gear changes
    gear_changes = (gear.diff() != 0).sum() - 1

    # Most frequently used gear
    most_used_gear = gear.mode().iloc[0]

    analysis = {
        "minimum_gear": gear.min(),
        "maximum_gear": gear.max(),
        "most_used_gear": most_used_gear,
        "gear_changes": gear_changes
    }

    return analysis

# ==========================================================
# RPM ANALYSIS
# ==========================================================

def analyze_rpm(telemetry):
    """
    Analyze RPM telemetry.

    Returns
    -------
    dict
        Maximum, average and minimum RPM.
    """

    if "RPM" not in telemetry.columns:
        raise ValueError(
            "RPM data is not available in telemetry."
        )

    rpm = telemetry["RPM"].dropna()

    if rpm.empty:
        raise ValueError(
            "No valid RPM data available."
        )

    analysis = {
        "maximum_rpm": rpm.max(),
        "average_rpm": rpm.mean(),
        "minimum_rpm": rpm.min()
    }

    return analysis

# ==========================================================
# DRS ANALYSIS
# ==========================================================

def analyze_drs(telemetry):
    """
    Analyze DRS telemetry.
    """

    if "DRS" not in telemetry.columns:
        return {
            "available": False,
            "message": "DRS data is not available."
        }

    drs = telemetry["DRS"].fillna(0)

    total_samples = len(drs)

    # Get unique DRS states
    drs_states = sorted(drs.unique())

    # DRS active states
    drs_active = drs >= 10

    active_samples = int(drs_active.sum())

    if total_samples > 0:
        usage_percentage = (
            active_samples / total_samples
        ) * 100
    else:
        usage_percentage = 0

    return {
        "available": True,
        "total_samples": total_samples,
        "drs_active_samples": active_samples,
        "drs_usage_percentage": usage_percentage,
        "drs_states": drs_states
    }
    
# ==========================================================
# LAP & SECTOR ANALYSIS
# ==========================================================

def analyze_lap(lap):
    """
    Analyze lap and sector performance.
    """

    analysis = {
        "lap_number": lap["LapNumber"],
        "lap_time": lap["LapTime"],
        "sector_1": lap["Sector1Time"],
        "sector_2": lap["Sector2Time"],
        "sector_3": lap["Sector3Time"]
    }

    return analysis

# ==========================================================
# MAIN PROGRAM
# ==========================================================

if __name__ == "__main__":

    # ------------------------------------------------------
    # FASTF1 CONNECTION
    # ------------------------------------------------------

    fastf1 = get_fastf1()


    # ------------------------------------------------------
    # LOAD SESSION
    # ------------------------------------------------------

    YEAR = 2024
    RACE = "Monza"
    SESSION_TYPE = "R"

    print("\n================================")
    print("       F1 TELEMETRY LAB")
    print("================================")

    print(
        f"\nLoading {YEAR} {RACE} - {SESSION_TYPE}"
    )

    session = fastf1.get_session(
        YEAR,
        RACE,
        SESSION_TYPE
    )

    session.load()

    print("\nSession loaded successfully!")


    # ------------------------------------------------------
    # DRIVER + LAP
    # ------------------------------------------------------

    driver = "VER"
    lap_number = 20

    lap, telemetry = get_lap_telemetry(
        session,
        driver,
        lap_number
    )


    # ------------------------------------------------------
    # LAP INFORMATION
    # ------------------------------------------------------

    print("\n================================")
    print("        LAP INFORMATION")
    print("================================")

    print("Driver   :", driver)
    print("Lap      :", lap["LapNumber"])
    print("Lap Time :", lap["LapTime"])


    # ------------------------------------------------------
    # TELEMETRY COLUMNS
    # ------------------------------------------------------

    print("\n================================")
    print("       TELEMETRY COLUMNS")
    print("================================")

    print(
        telemetry.columns.tolist()
    )


    # ------------------------------------------------------
    # TELEMETRY SAMPLE
    # ------------------------------------------------------

    print("\n================================")
    print("       TELEMETRY SAMPLE")
    print("================================")

    print(
        telemetry.head(10).to_string(
            index=False
        )
    )


    # ------------------------------------------------------
    # SPEED ANALYSIS
    # ------------------------------------------------------

    speed_analysis = analyze_speed(
        telemetry
    )

    print("\n================================")
    print("         SPEED ANALYSIS")
    print("================================")

    print(
        f"Maximum Speed : "
        f"{speed_analysis['maximum_speed']:.2f} km/h"
    )

    print(
        f"Average Speed : "
        f"{speed_analysis['average_speed']:.2f} km/h"
    )

    print(
        f"Minimum Speed : "
        f"{speed_analysis['minimum_speed']:.2f} km/h"
    )
    
    
 # ------------------------------------------------------
# THROTTLE ANALYSIS
# ------------------------------------------------------

throttle_analysis = analyze_throttle(
    telemetry
)

print("\n================================")
print("        THROTTLE ANALYSIS")
print("================================")

print(
    f"Maximum Throttle : "
    f"{throttle_analysis['maximum_throttle']:.2f}%"
)

print(
    f"Average Throttle : "
    f"{throttle_analysis['average_throttle']:.2f}%"
)

print(
    f"Minimum Throttle : "
    f"{throttle_analysis['minimum_throttle']:.2f}%"
)

# ------------------------------------------------------
# BRAKE ANALYSIS
# ------------------------------------------------------

brake_analysis = analyze_brake(
    telemetry
)

print("\n================================")
print("          BRAKE ANALYSIS")
print("================================")

print(
    f"Maximum Brake : "
    f"{brake_analysis['maximum_brake']:.2f}"
)

print(
    f"Average Brake : "
    f"{brake_analysis['average_brake']:.2f}"
)

print(
    f"Braking Samples : "
    f"{brake_analysis['braking_samples']}"
)

# ------------------------------------------------------
# GEAR ANALYSIS
# ------------------------------------------------------

gear_analysis = analyze_gear(
    telemetry
)

print("\n================================")
print("          GEAR ANALYSIS")
print("================================")

print(
    f"Minimum Gear : "
    f"{gear_analysis['minimum_gear']}"
)

print(
    f"Maximum Gear : "
    f"{gear_analysis['maximum_gear']}"
)

print(
    f"Most Used Gear : "
    f"{gear_analysis['most_used_gear']}"
)

print(
    f"Gear Changes : "
    f"{gear_analysis['gear_changes']}"
)
# ------------------------------------------------------
# RPM ANALYSIS
# ------------------------------------------------------

rpm_analysis = analyze_rpm(
    telemetry
)

print("\n================================")
print("           RPM ANALYSIS")
print("================================")

print(
    f"Maximum RPM : "
    f"{rpm_analysis['maximum_rpm']:.0f}"
)

print(
    f"Average RPM : "
    f"{rpm_analysis['average_rpm']:.0f}"
)

print(
    f"Minimum RPM : "
    f"{rpm_analysis['minimum_rpm']:.0f}"
)

# ------------------------------------------------------
# DRS ANALYSIS
# ------------------------------------------------------

drs_analysis = analyze_drs(
    telemetry
)

print("\n================================")
print("           DRS ANALYSIS")
print("================================")

if drs_analysis["available"]:

    print(
        f"Total Telemetry Samples : "
        f"{drs_analysis['total_samples']}"
    )

    print(
        f"DRS Active Samples : "
        f"{drs_analysis['drs_active_samples']}"
    )

    print(
        f"DRS Usage : "
        f"{drs_analysis['drs_usage_percentage']:.2f}%"
    )

    print(
        f"DRS States : "
        f"{drs_analysis['drs_states']}"
    )

else:

    print(
        drs_analysis["message"]
    )
    
# ------------------------------------------------------
# LAP & SECTOR ANALYSIS
# ------------------------------------------------------

lap_analysis = analyze_lap(
    lap
)

print("\n================================")
print("      LAP & SECTOR ANALYSIS")
print("================================")

print(
    f"Lap Number : "
    f"{lap_analysis['lap_number']}"
)

print(
    f"Lap Time   : "
    f"{lap_analysis['lap_time']}"
)

print(
    f"Sector 1   : "
    f"{lap_analysis['sector_1']}"
)

print(
    f"Sector 2   : "
    f"{lap_analysis['sector_2']}"
)

print(
    f"Sector 3   : "
    f"{lap_analysis['sector_3']}"
)