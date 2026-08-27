from fastf1_connection import get_fastf1


# ==========================================================
# GET F1 RACE CALENDAR
# ==========================================================

def get_race_calendar(year):
    """
    Get the complete F1 event calendar for a season.
    """

    fastf1 = get_fastf1()

    schedule = fastf1.get_event_schedule(
        year
    )

    return schedule


# ==========================================================
# DISPLAY CALENDAR
# ==========================================================

def display_calendar(schedule):

    print("\n==========================================")
    print("             F1 RACE CALENDAR")
    print("==========================================")


    for _, event in schedule.iterrows():

        round_number = event.get(
            "RoundNumber",
            "N/A"
        )

        country = event.get(
            "Country",
            "N/A"
        )

        location = event.get(
            "Location",
            "N/A"
        )

        event_name = event.get(
            "EventName",
            "N/A"
        )

        event_date = event.get(
            "EventDate",
            "N/A"
        )


        print(
            f"\nRound {round_number}"
        )

        print(
            f"Event    : {event_name}"
        )

        print(
            f"Country  : {country}"
        )

        print(
            f"Location : {location}"
        )

        print(
            f"Date     : {event_date}"
        )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    print("\n==========================================")
    print("        F1 TELEMETRY LAB")
    print("        PHASE 7.1")
    print("        RACE CALENDAR")
    print("==========================================")


    YEAR = 2026


    print(
        f"\nLoading {YEAR} F1 calendar..."
    )


    schedule = get_race_calendar(
        YEAR
    )


    print(
        "\nCalendar loaded successfully!"
    )


    print(
        f"Total events : {len(schedule)}"
    )


    display_calendar(
        schedule
    )


    print("\n==========================================")
    print("        PHASE 7.1 COMPLETE")
    print("==========================================")