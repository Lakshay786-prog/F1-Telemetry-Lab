from pathlib import Path
import asyncio
import json
from datetime import datetime, timezone

import joblib
import pandas as pd

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.fastf1_connection import get_fastf1
from backend.live_tracking import load_session, get_live_data

from fastapi import FastAPI

app = FastAPI(
    title="F1 Telemetry Lab API",
    description="F1 Telemetry + Machine Learning API",
    version="1.0.0"
)


# ==========================================================
# NEXT F1 EVENT - TEST
# ==========================================================

@app.get("/api/next-event")
def get_next_event():

    return {
        "status": "success",

        "event": {

            "round": 1,

            "event_name":
                "TEST EVENT",

            "official_name":
                "F1 Test Event",

            "country":
                "Test",

            "location":
                "Test",

            "date":
                "2026-01-01",

            "event_date":
                "2026-01-01T00:00:00+00:00",

            "format":
                "conventional",

            "sessions": [],

            "session_details": []

        }
    }

# ==========================================================
# PROJECT PATH
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_DIR = PROJECT_ROOT / "model" / "saved_models"

MODEL_FILE = MODEL_DIR / "lap_time_prediction_model.pkl"

IMPUTER_FILE = MODEL_DIR / "lap_time_prediction_imputer.pkl"


# ==========================================================
# ML FEATURES
# ==========================================================

FEATURE_COLUMNS = [
    "MaxSpeed",
    "AvgSpeed",
    "MinSpeed",

    "MaxThrottle",
    "AvgThrottle",
    "MinThrottle",

    "MaxBrake",
    "AvgBrake",
    "BrakingSamples",

    "MinGear",
    "MaxGear",
    "MostUsedGear",
    "GearChanges",

    "MaxRPM",
    "AvgRPM",
    "MinRPM",

    "DRSUsage",
]


# ==========================================================
# FASTAPI APPLICATION
# ==========================================================

app = FastAPI(
    title="F1 Telemetry Lab API",
    description=(
        "F1 Telemetry + Machine Learning + Live Tracking API"
    ),
    version="1.0.0",
)


# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# REQUEST MODEL
# ==========================================================

class LapPredictionRequest(BaseModel):

    MaxSpeed: float
    AvgSpeed: float
    MinSpeed: float

    MaxThrottle: float
    AvgThrottle: float
    MinThrottle: float

    MaxBrake: float
    AvgBrake: float
    BrakingSamples: float

    MinGear: float
    MaxGear: float
    MostUsedGear: float
    GearChanges: float

    MaxRPM: float
    AvgRPM: float
    MinRPM: float

    DRSUsage: float


# ==========================================================
# ROOT
# ==========================================================

@app.get("/")
def root():

    return {
        "application": "F1 Telemetry Lab",
        "status": "online",
        "version": "1.0.0",
    }


# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.get("/api/health")
def health():

    return {
        "status": "healthy",
        "service": "F1 Telemetry Lab Backend",
    }


# ==========================================================
# FASTF1 STATUS
# ==========================================================

@app.get("/api/fastf1")
def fastf1_status():

    try:

        fastf1 = get_fastf1()

        return {
            "status": "connected",
            "fastf1_version": fastf1.__version__,
        }

    except Exception as error:

        return {
            "status": "error",
            "message": str(error),
        }


# ==========================================================
# ML MODEL STATUS
# ==========================================================

@app.get("/api/ml/status")
def ml_status():

    return {
        "model_available": MODEL_FILE.exists(),
        "imputer_available": IMPUTER_FILE.exists(),
        "model": str(MODEL_FILE),
        "features": len(FEATURE_COLUMNS),
    }


# ==========================================================
# LAP-TIME PREDICTION
# ==========================================================

@app.post("/api/predict/lap-time")
def predict_lap_time(
    request: LapPredictionRequest
):

    try:

        if not MODEL_FILE.exists():

            return {
                "status": "error",
                "message": "ML model not found",
                "model": str(MODEL_FILE),
            }


        if not IMPUTER_FILE.exists():

            return {
                "status": "error",
                "message": "ML imputer not found",
                "imputer": str(IMPUTER_FILE),
            }


        model = joblib.load(
            MODEL_FILE
        )

        imputer = joblib.load(
            IMPUTER_FILE
        )


        data = request.model_dump()


        input_data = pd.DataFrame(
            [
                [
                    data[column]
                    for column in FEATURE_COLUMNS
                ]
            ],
            columns=FEATURE_COLUMNS,
        )


        input_data = imputer.transform(
            input_data
        )


        prediction = model.predict(
            input_data
        )


        predicted_lap_time = float(
            prediction[0]
        )


        return {
            "status": "success",
            "predicted_lap_time": round(
                predicted_lap_time,
                3,
            ),
            "unit": "seconds",
        }


    except Exception as error:

        return {
            "status": "error",
            "message": str(error),
        }


# ==========================================================
# NEXT F1 EVENT
# ==========================================================

@app.get("/api/next-event")
def get_next_event():

    try:

        # --------------------------------------------------
        # FASTF1
        # --------------------------------------------------

        fastf1 = get_fastf1()


        # --------------------------------------------------
        # CURRENT UTC TIME
        # --------------------------------------------------

        now = pd.Timestamp.now(
            tz="UTC"
        )


        current_year = now.year


        # --------------------------------------------------
        # F1 SCHEDULE
        # --------------------------------------------------

        schedule = fastf1.get_event_schedule(
            current_year,
            include_testing=False
        )


        events = []


        # --------------------------------------------------
        # LOOP THROUGH EVENTS
        # --------------------------------------------------

        for _, event in schedule.iterrows():

            event_date = event.get(
                "EventDate"
            )


            if pd.isna(event_date):

                continue


            event_datetime = pd.Timestamp(
                event_date
            )


            # --------------------------------------------------
            # TIMEZONE
            # --------------------------------------------------

            if event_datetime.tzinfo is None:

                event_datetime = (
                    event_datetime
                    .tz_localize("UTC")
                )

            else:

                event_datetime = (
                    event_datetime
                    .tz_convert("UTC")
                )


            # --------------------------------------------------
            # ONLY FUTURE / CURRENT EVENTS
            # --------------------------------------------------

            event_day = (
                event_datetime.normalize()
            )


            if event_day < now.normalize():

                continue


            # --------------------------------------------------
            # SESSION NAMES
            # --------------------------------------------------

            sessions = []


            for column in [
                "Session1",
                "Session2",
                "Session3",
                "Session4",
                "Session5",
            ]:

                if column not in event.index:

                    continue


                value = event.get(
                    column
                )


                if (
                    pd.notna(value)
                    and str(value).strip()
                ):

                    sessions.append(
                        str(value).strip()
                    )


            # --------------------------------------------------
            # SESSION DETAILS
            # --------------------------------------------------

            session_details = []


            for index in range(1, 6):

                session_name = event.get(
                    f"Session{index}"
                )


                session_date = event.get(
                    f"Session{index}Date"
                )


                if (
                    pd.isna(session_name)
                    or not str(session_name).strip()
                ):

                    continue


                detail = {
                    "name": str(
                        session_name
                    ).strip()
                }


                if pd.notna(
                    session_date
                ):

                    session_datetime = (
                        pd.Timestamp(
                            session_date
                        )
                    )


                    if session_datetime.tzinfo is None:

                        session_datetime = (
                            session_datetime
                            .tz_localize("UTC")
                        )

                    else:

                        session_datetime = (
                            session_datetime
                            .tz_convert("UTC")
                        )


                    detail["date"] = (
                        session_datetime.strftime(
                            "%Y-%m-%d"
                        )
                    )


                    detail["datetime"] = (
                        session_datetime.isoformat()
                    )


                session_details.append(
                    detail
                )


            # --------------------------------------------------
            # ROUND
            # --------------------------------------------------

            round_number = event.get(
                "RoundNumber"
            )


            if pd.notna(
                round_number
            ):

                round_number = int(
                    round_number
                )

            else:

                round_number = None


            # --------------------------------------------------
            # EVENT INFORMATION
            # --------------------------------------------------

            event_name = event.get(
                "EventName",
                "Unknown"
            )


            official_name = event.get(
                "OfficialEventName",
                event_name
            )


            country = event.get(
                "Country",
                ""
            )


            location = event.get(
                "Location",
                ""
            )


            event_format = event.get(
                "EventFormat",
                "conventional"
            )


            # --------------------------------------------------
            # BUILD EVENT
            # --------------------------------------------------

            events.append(
                {

                    "round":
                        round_number,

                    "event_name":
                        str(event_name),

                    "official_name":
                        str(official_name),

                    "country":
                        str(country),

                    "location":
                        str(location),

                    "date":
                        event_datetime.strftime(
                            "%Y-%m-%d"
                        ),

                    "event_date":
                        event_datetime.isoformat(),

                    "format":
                        str(event_format),

                    "sessions":
                        sessions,

                    "session_details":
                        session_details,

                }
            )


        # --------------------------------------------------
        # NO UPCOMING EVENT
        # --------------------------------------------------

        if not events:

            return {

                "status":
                    "success",

                "message":
                    (
                        "No upcoming events found "
                        f"for {current_year}."
                    ),

                "event":
                    None,

            }


        # --------------------------------------------------
        # SORT EVENTS
        # --------------------------------------------------

        events.sort(
            key=lambda item:
                item["event_date"]
        )


        # --------------------------------------------------
        # NEXT EVENT
        # --------------------------------------------------

        next_event = events[0]


        return {

            "status":
                "success",

            "event":
                next_event,

        }


    except Exception as error:

        return {

            "status":
                "error",

            "message":
                str(error),

        }


# ==========================================================
# SESSION INFORMATION
# ==========================================================

@app.get(
    "/api/session/{year}/{event}/{session_type}"
)
def get_session_info(
    year: int,
    event: str,
    session_type: str,
):

    try:

        fastf1 = get_fastf1()


        session = fastf1.get_session(
            year,
            event,
            session_type,
        )


        session.load()


        return {

            "status":
                "success",

            "year":
                year,

            "event":
                event,

            "session":
                session_type,

            "event_name":
                session.event.get(
                    "EventName",
                    event,
                ),

            "country":
                session.event.get(
                    "Country",
                    "Unknown",
                ),

            "location":
                session.event.get(
                    "Location",
                    "Unknown",
                ),

        }


    except Exception as error:

        return {

            "status":
                "error",

            "message":
                str(error),

        }


# ==========================================================
# DRIVERS
# ==========================================================

@app.get(
    "/api/drivers/{year}/{event}/{session_type}"
)
def get_drivers(
    year: int,
    event: str,
    session_type: str,
):

    try:

        fastf1 = get_fastf1()


        session = fastf1.get_session(
            year,
            event,
            session_type,
        )


        session.load()


        drivers = []


        for driver_number in session.drivers:

            try:

                driver_info = (
                    session.get_driver(
                        driver_number
                    )
                )


                drivers.append(
                    {

                        "number":
                            driver_number,

                        "abbreviation":
                            driver_info.get(
                                "Abbreviation",
                                "",
                            ),

                        "name":
                            driver_info.get(
                                "FullName",
                                driver_number,
                            ),

                        "team":
                            driver_info.get(
                                "TeamName",
                                "",
                            ),

                    }
                )


            except Exception:

                continue


        return {

            "status":
                "success",

            "drivers":
                drivers,

        }


    except Exception as error:

        return {

            "status":
                "error",

            "message":
                str(error),

        }


# ==========================================================
# LIVE TELEMETRY WEBSOCKET
# ==========================================================

@app.websocket(
    "/ws/live/{year}/{event}/{session_type}"
)
async def live_telemetry(
    websocket: WebSocket,
    year: int,
    event: str,
    session_type: str,
):

    await websocket.accept()


    print(
        "\n=========================================="
    )

    print(
        "      WEBSOCKET CLIENT CONNECTED"
    )

    print(
        f"Session: {year} {event} {session_type}"
    )

    print(
        "=========================================="
    )


    try:

        session = load_session(
            year,
            event,
            session_type,
        )


        while True:

            try:

                live_data = get_live_data(
                    session
                )


                message = {

                    "status":
                        "success",

                    "timestamp":
                        pd.Timestamp.now().isoformat(),

                    "drivers":
                        live_data,

                }


                await websocket.send_text(
                    json.dumps(
                        message,
                        default=str,
                    )
                )


                print(
                    "Live update sent: "
                    f"{len(live_data)} drivers"
                )


                await asyncio.sleep(
                    2
                )


            except Exception as error:

                print(
                    f"Live update error: {error}"
                )


                error_message = {

                    "status":
                        "error",

                    "message":
                        str(error),

                }


                try:

                    await websocket.send_text(
                        json.dumps(
                            error_message
                        )
                    )

                except Exception:

                    break


                await asyncio.sleep(
                    2
                )


    except WebSocketDisconnect:

        print(
            "\nWebSocket client disconnected."
        )


    except Exception as error:

        print(
            f"\nWebSocket error: {error}"
        )


        try:

            await websocket.close()

        except Exception:

            pass


# ==========================================================
# START SERVER
# ==========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )