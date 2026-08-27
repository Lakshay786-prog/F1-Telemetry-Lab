from fastf1_connection import get_fastf1


fastf1 = get_fastf1()


def load_race(year, race, session_type):
    """
    Load an F1 session.

    Parameters:
        year: F1 season year
        race: Grand Prix name
        session_type: R, Q, FP1, FP2, FP3, S, SQ
    """

    session = fastf1.get_session(
        year,
        race,
        session_type
    )

    print(f"Loading {year} {race} - {session_type}")

    session.load()

    print("Session loaded successfully!")

    return session


if __name__ == "__main__":

    session = load_race(
        2024,
        "Monza",
        "R"
    )

    print("\nSession:")
    print(session.event)

    print("\nResults:")
    print(session.results)