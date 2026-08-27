from fastf1_connection import get_fastf1
import matplotlib.pyplot as plt


# ==========================================================
# GET TRACK DATA
# ==========================================================

def get_track_data(session, driver, lap_number):
    """
    Extract X and Y position data for a specific
    driver's specific lap.
    """

    # Get all laps for the selected driver
    driver_laps = session.laps.pick_drivers(driver)

    # Select the requested lap
    lap_data = driver_laps[
        driver_laps["LapNumber"] == lap_number
    ]

    # Check if lap exists
    if lap_data.empty:
        raise ValueError(
            f"Lap {lap_number} not found for driver {driver}"
        )

    # Get first matching lap
    lap = lap_data.iloc[0]

    # Extract telemetry
    telemetry = lap.get_telemetry()

    # Required position columns
    required_columns = ["X", "Y"]

    for column in required_columns:

        if column not in telemetry.columns:
            raise ValueError(
                f"{column} position data is not available."
            )

    # Remove missing position values
    telemetry = telemetry.dropna(
        subset=["X", "Y"]
    )

    if telemetry.empty:
        raise ValueError(
            "No valid X/Y position data found."
        )

    return lap, telemetry


# ==========================================================
# PLOT TRACK
# ==========================================================

def plot_track(telemetry, driver, lap_number):
    """
    Plot an F1-style circuit map.
    """

    # Create figure
    fig, ax = plt.subplots(
        figsize=(12, 8)
    )

    # ------------------------------------------------------
    # BACKGROUND
    # ------------------------------------------------------

    fig.patch.set_facecolor("#080808")
    ax.set_facecolor("#080808")


    # ------------------------------------------------------
    # TRACK BASE
    # ------------------------------------------------------

    ax.plot(
        telemetry["X"],
        telemetry["Y"],
        linewidth=9,
        color="#2b2b2b",
        solid_capstyle="round",
        zorder=1
    )


    # ------------------------------------------------------
    # RACING LINE
    # ------------------------------------------------------

    ax.plot(
        telemetry["X"],
        telemetry["Y"],
        linewidth=2,
        color="#e10600",
        solid_capstyle="round",
        zorder=2
    )


    # ------------------------------------------------------
    # START POSITION
    # ------------------------------------------------------

    start_x = telemetry["X"].iloc[0]
    start_y = telemetry["Y"].iloc[0]

    ax.scatter(
        start_x,
        start_y,
        s=120,
        color="white",
        edgecolors="#e10600",
        linewidths=2,
        zorder=5
    )

    ax.annotate(
        "START",
        xy=(start_x, start_y),
        xytext=(20, 20),
        textcoords="offset points",
        color="white",
        fontsize=10,
        fontweight="bold",
        arrowprops=dict(
            arrowstyle="->",
            color="white",
            linewidth=1
        )
    )


    # ------------------------------------------------------
    # FINISH POSITION
    # ------------------------------------------------------

    finish_x = telemetry["X"].iloc[-1]
    finish_y = telemetry["Y"].iloc[-1]

    ax.scatter(
        finish_x,
        finish_y,
        s=80,
        color="#e10600",
        edgecolors="white",
        linewidths=2,
        zorder=5
    )

    ax.annotate(
        "FINISH",
        xy=(finish_x, finish_y),
        xytext=(20, -25),
        textcoords="offset points",
        color="#e10600",
        fontsize=10,
        fontweight="bold",
        arrowprops=dict(
            arrowstyle="->",
            color="#e10600",
            linewidth=1
        )
    )


    # ------------------------------------------------------
    # TITLE
    # ------------------------------------------------------

    ax.set_title(
        f"MONZA CIRCUIT  |  {driver}  |  LAP {lap_number}",
        color="white",
        fontsize=20,
        fontweight="bold",
        pad=20
    )


    # ------------------------------------------------------
    # INFORMATION
    # ------------------------------------------------------

    fig.text(
        0.05,
        0.035,
        f"DRIVER: {driver}",
        color="#aaaaaa",
        fontsize=10
    )

    fig.text(
        0.50,
        0.035,
        f"LAP: {lap_number}",
        color="#aaaaaa",
        fontsize=10,
        horizontalalignment="center"
    )

    fig.text(
        0.95,
        0.035,
        f"TELEMETRY SAMPLES: {len(telemetry)}",
        color="#aaaaaa",
        fontsize=10,
        horizontalalignment="right"
    )


    # ------------------------------------------------------
    # REMOVE AXES
    # ------------------------------------------------------

    ax.set_xticks([])
    ax.set_yticks([])

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_aspect("equal")


    # ------------------------------------------------------
    # DISPLAY
    # ------------------------------------------------------

    plt.tight_layout(
        rect=[0, 0.07, 1, 0.95]
    )

    plt.show()


# ==========================================================
# MAIN PROGRAM
# ==========================================================

if __name__ == "__main__":

    # ------------------------------------------------------
    # FASTF1 CONNECTION
    # ------------------------------------------------------

    fastf1 = get_fastf1()


    # ------------------------------------------------------
    # RACE SETTINGS
    # ------------------------------------------------------

    YEAR = 2024
    RACE = "Monza"
    SESSION_TYPE = "R"

    DRIVER = "VER"
    LAP_NUMBER = 20


    # ------------------------------------------------------
    # HEADER
    # ------------------------------------------------------

    print("\n================================")
    print("       F1 TELEMETRY LAB")
    print("================================")


    # ------------------------------------------------------
    # LOAD SESSION
    # ------------------------------------------------------

    print(
        f"\nLoading {YEAR} {RACE} - {SESSION_TYPE}"
    )

    session = fastf1.get_session(
        YEAR,
        RACE,
        SESSION_TYPE
    )

    session.load()

    print(
        "Session loaded successfully!"
    )


    # ------------------------------------------------------
    # GET LAP TELEMETRY
    # ------------------------------------------------------

    print(
        f"\nGetting track data..."
    )

    print(
        f"Driver : {DRIVER}"
    )

    print(
        f"Lap    : {LAP_NUMBER}"
    )

    lap, telemetry = get_track_data(
        session,
        DRIVER,
        LAP_NUMBER
    )


    # ------------------------------------------------------
    # DISPLAY INFORMATION
    # ------------------------------------------------------

    print(
        f"\nTelemetry samples: "
        f"{len(telemetry)}"
    )

    print(
        f"Lap time: "
        f"{lap['LapTime']}"
    )

    print(
        "\nTrack data successfully extracted!"
    )


    # ------------------------------------------------------
    # PLOT
    # ------------------------------------------------------

    plot_track(
        telemetry,
        DRIVER,
        LAP_NUMBER
    )