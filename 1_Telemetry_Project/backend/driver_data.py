import pandas as pd

from fastf1_connection import get_fastf1


def get_driver_data(session):
    """
    Extract basic driver information from an F1 session.

    Parameters
    ----------
    session : FastF1 session
        Loaded FastF1 session.

    Returns
    -------
    pandas.DataFrame
        Clean driver information.
    """

    results = session.results

    driver_data = results[
        [
            "DriverNumber",
            "Abbreviation",
            "FullName",
            "TeamName",
            "Position",
            "GridPosition",
            "Status",
            "Points",
            "Laps"
        ]
    ].copy()

    return driver_data


if __name__ == "__main__":

    fastf1 = get_fastf1()

    # Load 2024 Italian GP
    session = fastf1.get_session(
        2024,
        "Monza",
        "R"
    )

    session.load()

    # Get driver data
    drivers = get_driver_data(session)

    print("\n================================")
    print("        DRIVER DATA")
    print("================================\n")

    print(drivers.to_string(index=False))