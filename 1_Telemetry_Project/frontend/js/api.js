const API_BASE_URL = "http://127.0.0.1:8000";


// ==========================================================
// HEALTH CHECK
// ==========================================================

async function checkBackend() {

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/health`
        );

        if (!response.ok) {
            throw new Error(
                `Backend returned ${response.status}`
            );
        }

        const data = await response.json();

        console.log(
            "Backend:",
            data
        );

        return data;

    } catch (error) {

        console.error(
            "Backend connection failed:",
            error
        );

        return null;
    }
}


// ==========================================================
// FASTF1 STATUS
// ==========================================================

async function checkFastF1() {

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/fastf1`
        );

        if (!response.ok) {
            throw new Error(
                `FastF1 API returned ${response.status}`
            );
        }

        const data = await response.json();

        console.log(
            "FastF1:",
            data
        );

        return data;

    } catch (error) {

        console.error(
            "FastF1 connection failed:",
            error
        );

        return null;
    }
}


// ==========================================================
// GET REQUEST
// ==========================================================

async function apiGet(endpoint) {

    try {

        const response = await fetch(
            `${API_BASE_URL}${endpoint}`
        );

        if (!response.ok) {

            throw new Error(
                `API Error: ${response.status}`
            );

        }

        return await response.json();

    } catch (error) {

        console.error(
            "API request failed:",
            error
        );

        throw error;
    }
}


// ==========================================================
// SESSION
// ==========================================================

async function getSession(
    year,
    event,
    sessionType
) {

    try {

        const url =
            `${API_BASE_URL}/api/session/` +
            `${year}/${encodeURIComponent(event)}/${sessionType}`;


        const response = await fetch(
            url
        );


        if (!response.ok) {

            throw new Error(
                `Session API returned ${response.status}`
            );

        }


        const data =
            await response.json();


        console.log(
            "Session:",
            data
        );


        return data;


    } catch (error) {

        console.error(
            "Session request failed:",
            error
        );

        return null;
    }
}


// ==========================================================
// DRIVERS
// ==========================================================

async function getSession(
    year,
    event,
    sessionType
) {

    try {

        showLoading(
            "Loading session..."
        );

        const url =
            `${API_BASE_URL}/api/session/` +
            `${year}/${encodeURIComponent(event)}/${sessionType}`;

        const response =
            await fetch(url);

        if (!response.ok) {

            throw new Error(
                `Session API returned ${response.status}`
            );

        }

        const data =
            await response.json();

        console.log(
            "Session:",
            data
        );

        return data;

    } catch (error) {

        console.error(
            "Session request failed:",
            error
        );

        return null;

    } finally {

        hideLoading();

    }
}
// ==========================================================
// ML MODEL STATUS
// ==========================================================

async function checkMLModel() {

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/ml/status`
        );


        if (!response.ok) {

            throw new Error(
                `ML API returned ${response.status}`
            );

        }


        const data =
            await response.json();


        console.log(
            "ML Model:",
            data
        );


        return data;


    } catch (error) {

        console.error(
            "ML model connection failed:",
            error
        );

        return null;
    }
}


// ==========================================================
// ML LAP-TIME PREDICTION
// ==========================================================

async function predictLapTime(
    features
) {

    try {

        const response = await fetch(

            `${API_BASE_URL}/api/predict/lap-time`,

            {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body:
                    JSON.stringify(features)

            }

        );


        if (!response.ok) {

            throw new Error(
                `Prediction API returned ${response.status}`
            );

        }


        const data =
            await response.json();


        console.log(
            "Lap-time prediction:",
            data
        );


        return data;


    } catch (error) {

        console.error(
            "Lap prediction failed:",
            error
        );


        return {

            status:
                "error",

            message:
                error.message

        };

    }
}


// ==========================================================
// LIVE TELEMETRY WEBSOCKET
// ==========================================================

let liveSocket = null;


// ==========================================================
// CONNECT LIVE TELEMETRY
// ==========================================================

function connectLiveTelemetry(

    year,

    event,

    sessionType,

    onData,

    onError

) {

    // ------------------------------------------------------
    // Close existing connection
    // ------------------------------------------------------

    if (
        liveSocket !== null
    ) {

        liveSocket.close();

        liveSocket = null;

    }


    // ------------------------------------------------------
    // Create WebSocket URL
    // ------------------------------------------------------

    const websocketURL =

        `ws://127.0.0.1:8000/ws/live/` +

        `${year}/${encodeURIComponent(event)}/${sessionType}`;


    console.log(
        "Connecting to:",
        websocketURL
    );


    // ------------------------------------------------------
    // Create WebSocket
    // ------------------------------------------------------

    liveSocket =
        new WebSocket(
            websocketURL
        );


    // ------------------------------------------------------
    // CONNECTION OPEN
    // ------------------------------------------------------

    liveSocket.onopen =
        function () {

            console.log(
                "Live telemetry WebSocket connected."
            );

        };


    // ------------------------------------------------------
    // RECEIVE DATA
    // ------------------------------------------------------

    liveSocket.onmessage =
        function (event) {

            try {

                const data =
                    JSON.parse(
                        event.data
                    );


                console.log(
                    "Live telemetry:",
                    data
                );


                if (
                    typeof onData ===
                    "function"
                ) {

                    onData(
                        data
                    );

                }


            } catch (error) {

                console.error(

                    "Invalid WebSocket data:",

                    error

                );

            }

        };


    // ------------------------------------------------------
    // ERROR
    // ------------------------------------------------------

    liveSocket.onerror =
        function (error) {

            console.error(
                "WebSocket error:",
                error
            );


            if (
                typeof onError ===
                "function"
            ) {

                onError(
                    error
                );

            }

        };


    // ------------------------------------------------------
    // CONNECTION CLOSED
    // ------------------------------------------------------

    liveSocket.onclose =
        function (event) {

            console.log(
                "Live telemetry WebSocket closed.",
                event.code
            );

            liveSocket = null;

        };


    return liveSocket;
}


// ==========================================================
// DISCONNECT LIVE TELEMETRY
// ==========================================================

function disconnectLiveTelemetry() {

    if (
        liveSocket !== null
    ) {

        liveSocket.close();

        liveSocket = null;

        console.log(
            "Live telemetry disconnected."
        );

    }

}

// ==========================================================
// ERROR HANDLER
// ==========================================================

function handleAPIError(error, message = "Something went wrong.") {

    console.error(message, error);

    if (typeof showNotification === "function") {

        showNotification(
            message,
            "error"
        );

    }

    return {
        status: "error",
        message: message
    };
}
async function getDrivers(
    year,
    event,
    sessionType
) {

    try {

        showLoading(
            "Loading drivers..."
        );

        const url =
            `${API_BASE_URL}/api/drivers/` +
            `${year}/${encodeURIComponent(event)}/${sessionType}`;

        const response =
            await fetch(url);

        if (!response.ok) {

            throw new Error(
                `Driver API returned ${response.status}`
            );

        }

        const data =
            await response.json();

        console.log(
            "Drivers:",
            data
        );

        return data;

    } catch (error) {

        console.error(
            "Driver request failed:",
            error
        );

        return null;

    } finally {

        hideLoading();

    }
}