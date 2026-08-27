import fastf1

# Load a race session
session = fastf1.get_session(2024, "Monza", "R")

# Load the session data
session.load()

# Display race results
print(session.results)