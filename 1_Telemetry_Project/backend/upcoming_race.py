from datetime import datetime

import pandas as pd

from fastf1_connection import get_fastf1


# ==========================================================
# GET SEASON SCHEDULE
# ==========================================================

def get_schedule(year):

    fastf1 = get_fastf1()

    schedule = fastf1.get_event_schedule(
        year
    )

    return schedule


# ==========================================================
# PREPARE DATES
# ==========================================================

def prepare_schedule(schedule):

    schedule = schedule.copy()

    schedule["EventDate"] = pd.to_datetime(
        schedule["EventDate"],
        errors="coerce"
    )

    return schedule


# ==========================================================
# GET UPCOMING RACES
# ==========================================================

def get_upcoming_races(
    schedule,
    today=None
):

    if today is None:

        today = pd.Timestamp(
            datetime.now()
        )

    else:

        today = pd.Timestamp(
            today
        )


    upcoming = schedule[
        schedule["EventDate"] >= today
    ].copy()


    upcoming = upcoming.sort_values(
        "EventDate"
    )


    return upcoming


# ==========================================================
# GET COMPLETED RACES
# ==========================================================

def get_completed_races(
    schedule,
    today=None
):

    if today is None:

        today = pd.Timestamp(
            datetime.now()
        )

    else:

        today = pd.Timestamp(
            today
        )


    completed = schedule[
        schedule["EventDate"] < today
    ].copy()


    completed = completed.sort_values(
        "EventDate",
        ascending=False
    )


    return completed


# ==========================================================
# GET NEXT RACE
# ==========================================================

def get_next_race(
    schedule,
    today=None
):

    upcoming = get_upcoming_races(
        schedule,
        today
    )


    if upcoming.empty:

        return None


    return upcoming.iloc[0]


# ==========================================================
# DISPLAY RACE
# ==========================================================

def display_race(
    race,
    title
):

    print("\n==========================================")
    print(
        f"          {title}"
    )
    print("==========================================")


    if race is None:

        print(
            "No race available."
        )

        return


    print(
        f"Round    : "
        f"{race.get('RoundNumber', 'N/A')}"
    )

    print(
        f"Event    : "
        f"{race.get('EventName', 'N/A')}"
    )

    print(
        f"Country  : "
        f"{race.get('Country', 'N/A')}"
    )

    print(
        f"Location : "
        f"{race.get('Location', 'N/A')}"
    )

    print(
        f"Date     : "
        f"{race.get('EventDate', 'N/A')}"
    )


# ==========================================================
# DISPLAY UPCOMING RACES
# ==========================================================

def display_upcoming_races(
    upcoming
):

    print("\n==========================================")
    print("          UPCOMING RACES")
    print("==========================================")


    if upcoming.empty:

        print(
            "No upcoming races found."
        )

        return


    columns = [

        "RoundNumber",
        "EventName",
        "Country",
        "Location",
        "EventDate"

    ]


    available_columns = [

        column
        for column in columns
        if column in upcoming.columns

    ]


    print(

        upcoming[
            available_columns
        ].to_string(
            index=False
        )

    )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    print("\n==========================================")
    print("        F1 TELEMETRY LAB")
    print("        PHASE 7.2")
    print("        UPCOMING RACES")
    print("==========================================")


    YEAR = 2026


    print(
        f"\nLoading {YEAR} F1 calendar..."
    )


    # ------------------------------------------------------
    # LOAD
    # ------------------------------------------------------

    schedule = get_schedule(
        YEAR
    )


    # ------------------------------------------------------
    # PREPARE
    # ------------------------------------------------------

    schedule = prepare_schedule(
        schedule
    )


    # ------------------------------------------------------
    # CURRENT DATE
    # ------------------------------------------------------

    today = pd.Timestamp(
        datetime.now()
    )


    print(
        f"\nToday: "
        f"{today.strftime('%Y-%m-%d')}"
    )


    # ------------------------------------------------------
    # UPCOMING
    # ------------------------------------------------------

    upcoming = get_upcoming_races(
        schedule,
        today
    )


    # ------------------------------------------------------
    # COMPLETED
    # ------------------------------------------------------

    completed = get_completed_races(
        schedule,
        today
    )


    # ------------------------------------------------------
    # NEXT RACE
    # ------------------------------------------------------

    next_race = get_next_race(
        schedule,
        today
    )


    # ------------------------------------------------------
    # DISPLAY NEXT
    # ------------------------------------------------------

    display_race(
        next_race,
        "NEXT RACE"
    )


    # ------------------------------------------------------
    # DISPLAY UPCOMING
    # ------------------------------------------------------

    display_upcoming_races(
        upcoming
    )


    # ------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------

    print("\n==========================================")
    print("              SUMMARY")
    print("==========================================")


    print(
        f"Completed races : "
        f"{len(completed)}"
    )

    print(
        f"Upcoming races  : "
        f"{len(upcoming)}"
    )


    print("\n==========================================")
    print("        PHASE 7.2 COMPLETE")
    print("==========================================")