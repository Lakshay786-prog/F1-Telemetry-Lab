/*
=========================================================
F1 TELEMETRY LAB
APPLICATION CONTROLLER
PHASE 8.7
FINAL DASHBOARD INTEGRATION
=========================================================
*/


// ==========================================================
// API URL
// ==========================================================

const APP_API_BASE_URL =
    "http://127.0.0.1:8000";


// ==========================================================
// GLOBAL DASHBOARD STATE
// ==========================================================

window.dashboardState = {

    year: 2026,

    event: "Monza",

    session: "R",

    driver: null,

    liveConnected: false,

    lastTelemetry: null,

    prediction: null,

    nextEvent: null

};


// ==========================================================
// NEXT EVENT VARIABLES
// ==========================================================

let nextEventDateTime = null;

window.nextEventTimer = null;


// ==========================================================
// LOADING STATE
// ==========================================================

window.showLoading = function (
    message = "Loading..."
) {

    let loader =
        document.getElementById(
            "global-loader"
        );


    if (!loader) {

        loader =
            document.createElement(
                "div"
            );

        loader.id =
            "global-loader";


        loader.innerHTML = `

            <div class="loader-box">

                <div class="loader-spinner"></div>

                <div id="loader-message">
                    ${message}
                </div>

            </div>

        `;


        document.body.appendChild(
            loader
        );

    }


    const messageElement =
        document.getElementById(
            "loader-message"
        );


    if (messageElement) {

        messageElement.textContent =
            message;

    }


    loader.style.display =
        "flex";

};


// ==========================================================
// UPDATE LOADING
// ==========================================================

window.updateLoading = function (
    message
) {

    const messageElement =
        document.getElementById(
            "loader-message"
        );


    if (messageElement) {

        messageElement.textContent =
            message;

    }

};


// ==========================================================
// HIDE LOADING
// ==========================================================

window.hideLoading = function () {

    const loader =
        document.getElementById(
            "global-loader"
        );


    if (loader) {

        loader.style.display =
            "none";

    }

};


// ==========================================================
// NOTIFICATION SYSTEM
// ==========================================================

window.showNotification = function (
    message,
    type = "info"
) {

    let notification =
        document.getElementById(
            "api-notification"
        );


    if (!notification) {

        notification =
            document.createElement(
                "div"
            );


        notification.id =
            "api-notification";


        document.body.appendChild(
            notification
        );

    }


    notification.textContent =
        message;


    notification.className =
        `api-notification ${type}`;


    notification.style.display =
        "block";


    setTimeout(
        function () {

            notification.style.display =
                "none";

        },
        4000
    );

};


// ==========================================================
// NEXT F1 EVENT
// ==========================================================

window.loadNextEvent =
async function () {

    try {

        console.log(
            "Loading next F1 event..."
        );


        const response =
            await fetch(
                `${APP_API_BASE_URL}/api/next-event`
            );


        if (!response.ok) {

            throw new Error(
                `Next event API returned ${response.status}`
            );

        }


        const data =
            await response.json();


        console.log(
            "Next F1 event:",
            data
        );


        if (
            data.status !== "success"
            ||
            !data.event
        ) {

            throw new Error(
                data.message ||
                "No upcoming F1 event found."
            );

        }


        const event =
            data.event;


        // --------------------------------------------------
        // SAVE EVENT
        // --------------------------------------------------

        window.dashboardState.nextEvent =
            event;


        // --------------------------------------------------
        // EVENT DATE
        // --------------------------------------------------

        nextEventDateTime =
            new Date(
                event.event_date
            );


        // --------------------------------------------------
        // ROUND
        // --------------------------------------------------

        setElementText(
            "nextEventRound",
            event.round !== null
                ? `ROUND ${event.round}`
                : "--"
        );


        // --------------------------------------------------
        // EVENT NAME
        // --------------------------------------------------

        setElementText(
            "nextEventName",
            event.event_name ||
            "--"
        );


        // --------------------------------------------------
        // OFFICIAL NAME
        // --------------------------------------------------

        setElementText(
            "nextEventOfficialName",
            event.official_name ||
            "--"
        );


        // --------------------------------------------------
        // LOCATION
        // --------------------------------------------------

        setElementText(
            "nextEventLocation",
            event.location ||
            "--"
        );


        // --------------------------------------------------
        // COUNTRY
        // --------------------------------------------------

        setElementText(
            "nextEventCountry",
            event.country ||
            "--"
        );


        // --------------------------------------------------
        // DATE
        // --------------------------------------------------

        setElementText(
            "nextEventDate",
            formatEventDate(
                event.event_date
            )
        );


        // --------------------------------------------------
        // FORMAT
        // --------------------------------------------------

        setElementText(
            "nextEventFormat",
            formatEventFormat(
                event.format
            )
        );


        // --------------------------------------------------
        // SESSIONS
        // --------------------------------------------------

        renderNextEventSessions(
            event
        );


        // --------------------------------------------------
        // COUNTDOWN
        // --------------------------------------------------

        updateNextEventCountdown();


        if (
            window.nextEventTimer
        ) {

            clearInterval(
                window.nextEventTimer
            );

        }


        window.nextEventTimer =
            setInterval(
                updateNextEventCountdown,
                1000
            );


        console.log(
            "Next event loaded successfully:",
            event.event_name
        );


        return event;

    }
    catch (error) {

        console.error(
            "Next event loading failed:",
            error
        );


        setElementText(
            "nextEventName",
            "Unable to load event"
        );


        setElementText(
            "nextEventRound",
            "--"
        );


        setElementText(
            "nextEventLocation",
            "--"
        );


        setElementText(
            "nextEventCountry",
            "--"
        );


        setElementText(
            "nextEventDate",
            "--"
        );


        setElementText(
            "nextEventFormat",
            "--"
        );


        setElementText(
            "nextEventCountdown",
            "--"
        );


        return null;

    }

};


// ==========================================================
// SET ELEMENT TEXT
// ==========================================================

function setElementText(
    id,
    value
) {

    const element =
        document.getElementById(
            id
        );


    if (element) {

        element.textContent =
            value;

    }

};


// ==========================================================
// FORMAT EVENT DATE
// ==========================================================

window.formatEventDate =
function (
    dateString
) {

    const date =
        new Date(
            dateString
        );


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return "--";

    }


    return date.toLocaleDateString(
        "en-IN",
        {

            day: "2-digit",

            month: "short",

            year: "numeric"

        }
    );

};


// ==========================================================
// FORMAT SESSION DATE
// ==========================================================

function formatSessionDate(
    dateString
) {

    const date =
        new Date(
            dateString
        );


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return "";

    }


    return date.toLocaleString(
        "en-IN",
        {

            day: "2-digit",

            month: "short",

            hour: "2-digit",

            minute: "2-digit"

        }
    );

};


// ==========================================================
// FORMAT EVENT FORMAT
// ==========================================================

window.formatEventFormat =
function (
    format
) {

    if (!format) {

        return "--";

    }


    const value =
        String(format)
            .toLowerCase()
            .replace(
                /_/g,
                " "
            );


    return value.replace(
        /\b\w/g,
        function (
            character
        ) {

            return character.toUpperCase();

        }
    );

};


// ==========================================================
// RENDER NEXT EVENT SESSIONS
// ==========================================================

function renderNextEventSessions(
    event
) {

    const container =
        document.getElementById(
            "nextEventSessions"
        );


    if (!container) {

        console.warn(
            "nextEventSessions element not found."
        );

        return;

    }


    container.innerHTML =
        "";


    const sessionDetails =
        Array.isArray(
            event.session_details
        )
            ? event.session_details
            : [];


    const sessions =
        Array.isArray(
            event.sessions
        )
            ? event.sessions
            : [];


    // ------------------------------------------------------
    // SESSION DETAILS AVAILABLE
    // ------------------------------------------------------

    if (
        sessionDetails.length > 0
    ) {

        sessionDetails.forEach(
            function (
                session
            ) {

                const element =
                    document.createElement(
                        "span"
                    );


                const name =
                    session.name ||
                    "Session";


                if (
                    session.datetime
                ) {

                    element.textContent =
                        `${name} — ${formatSessionDate(
                            session.datetime
                        )}`;

                }
                else {

                    element.textContent =
                        name;

                }


                container.appendChild(
                    element
                );

            }
        );


        return;

    }


    // ------------------------------------------------------
    // BASIC SESSION NAMES
    // ------------------------------------------------------

    if (
        sessions.length > 0
    ) {

        sessions.forEach(
            function (
                session
            ) {

                const element =
                    document.createElement(
                        "span"
                    );


                element.textContent =
                    session;


                container.appendChild(
                    element
                );

            }
        );


        return;

    }


    // ------------------------------------------------------
    // NO SCHEDULE
    // ------------------------------------------------------

    const element =
        document.createElement(
            "span"
        );


    element.textContent =
        "Schedule unavailable";


    container.appendChild(
        element
    );

};


// ==========================================================
// NEXT EVENT COUNTDOWN
// ==========================================================

window.updateNextEventCountdown =
function () {

    const countdown =
        document.getElementById(
            "nextEventCountdown"
        );


    if (!countdown) {

        return;

    }


    if (
        !nextEventDateTime
        ||
        Number.isNaN(
            nextEventDateTime.getTime()
        )
    ) {

        countdown.textContent =
            "--";

        return;

    }


    const now =
        new Date();


    const difference =
        nextEventDateTime.getTime()
        -
        now.getTime();


    if (
        difference <= 0
    ) {

        countdown.textContent =
            "EVENT STARTED";

        return;

    }


    const totalSeconds =
        Math.floor(
            difference / 1000
        );


    const days =
        Math.floor(
            totalSeconds / 86400
        );


    const hours =
        Math.floor(
            (
                totalSeconds % 86400
            ) / 3600
        );


    const minutes =
        Math.floor(
            (
                totalSeconds % 3600
            ) / 60
        );


    const seconds =
        totalSeconds % 60;


    countdown.textContent =
        `${days}D ` +
        `${String(hours).padStart(2, "0")}H ` +
        `${String(minutes).padStart(2, "0")}M ` +
        `${String(seconds).padStart(2, "0")}S`;

};


// ==========================================================
// DASHBOARD INITIALIZATION
// ==========================================================

window.initializeDashboard =
async function () {

    console.log(
        "================================="
    );


    console.log(
        "F1 TELEMETRY LAB"
    );


    console.log(
        "PHASE 8.7 DASHBOARD"
    );


    console.log(
        "================================="
    );


    try {

        showLoading(
            "Initializing dashboard..."
        );


        // --------------------------------------------------
        // BACKEND
        // --------------------------------------------------

        if (
            typeof checkBackend !==
            "function"
        ) {

            throw new Error(
                "checkBackend() is not available. Check api.js."
            );

        }


        const backend =
            await checkBackend();


        if (!backend) {

            throw new Error(
                "Backend is unavailable."
            );

        }


        console.log(
            "FastAPI backend connected."
        );


        // --------------------------------------------------
        // FASTF1
        // --------------------------------------------------

        if (
            typeof checkFastF1 !==
            "function"
        ) {

            throw new Error(
                "checkFastF1() is not available. Check api.js."
            );

        }


        const fastf1 =
            await checkFastF1();


        if (
            !fastf1
            ||
            fastf1.status !==
            "connected"
        ) {

            throw new Error(
                "FastF1 is unavailable."
            );

        }


        console.log(
            "FastF1 connected:",
            fastf1.fastf1_version
        );


        // --------------------------------------------------
        // ML MODEL
        // --------------------------------------------------

        if (
            typeof checkMLModel ===
            "function"
        ) {

            const ml =
                await checkMLModel();


            if (
                ml
                &&
                ml.model_available
            ) {

                console.log(
                    "ML model connected."
                );

            }
            else {

                console.warn(
                    "ML model is unavailable."
                );

            }

        }


        // --------------------------------------------------
        // NEXT EVENT
        // --------------------------------------------------

        await loadNextEvent();


        hideLoading();


        showNotification(
            "Dashboard connected.",
            "success"
        );


        console.log(
            "Dashboard initialization complete."
        );


        return true;

    }
    catch (error) {

        hideLoading();


        console.error(
            "Dashboard initialization failed:",
            error
        );


        showNotification(
            error.message ||
            "Dashboard initialization failed.",
            "error"
        );


        return false;

    }

};


// ==========================================================
// LOAD DASHBOARD SESSION
// ==========================================================

window.loadDashboardSession =
async function (
    year,
    event,
    sessionType
) {

    dashboardState.year =
        year;


    dashboardState.event =
        event;


    dashboardState.session =
        sessionType;


    try {

        showLoading(
            "Loading session..."
        );


        console.log(
            `Loading ${year} ${event} ${sessionType}`
        );


        if (
            typeof getSession !==
            "function"
        ) {

            throw new Error(
                "getSession() is not available."
            );

        }


        const data =
            await getSession(
                year,
                event,
                sessionType
            );


        if (
            !data
            ||
            data.status !==
            "success"
        ) {

            throw new Error(
                data?.message ||
                "Session could not be loaded."
            );

        }


        updateSessionUI(
            data
        );


        // --------------------------------------------------
        // DRIVERS
        // --------------------------------------------------

        if (
            typeof getDrivers ===
            "function"
        ) {

            const drivers =
                await getDrivers(
                    year,
                    event,
                    sessionType
                );


            if (
                drivers
                &&
                drivers.status ===
                "success"
            ) {

                updateDriverUI(
                    drivers.drivers ||
                    []
                );

            }

        }


        showNotification(
            "Session loaded successfully.",
            "success"
        );


        return data;

    }
    catch (error) {

        console.error(
            "Session loading failed:",
            error
        );


        showNotification(
            error.message ||
            "Unable to load session.",
            "error"
        );


        return null;

    }
    finally {

        hideLoading();

    }

};


// ==========================================================
// UPDATE SESSION UI
// ==========================================================

window.updateSessionUI =
function (
    data
) {

    setElementText(
        "dashboard-event",
        data.event_name ||
        data.event ||
        "--"
    );


    setElementText(
        "dashboard-location",
        data.location ||
        "--"
    );


    setElementText(
        "dashboard-country",
        data.country ||
        "--"
    );


    setElementText(
        "dashboard-session",
        data.session ||
        data.session_type ||
        "--"
    );

};


// ==========================================================
// UPDATE DRIVER SELECTOR
// ==========================================================

window.updateDriverUI =
function (
    drivers
) {

    const driverSelect =
        document.getElementById(
            "driver-select"
        );


    if (!driverSelect) {

        console.warn(
            "driver-select element not found."
        );

        return;

    }


    driverSelect.innerHTML =
        "";


    const defaultOption =
        document.createElement(
            "option"
        );


    defaultOption.value =
        "";


    defaultOption.textContent =
        "Select Driver";


    driverSelect.appendChild(
        defaultOption
    );


    if (
        !Array.isArray(
            drivers
        )
    ) {

        return;

    }


    drivers.forEach(
        function (
            driver
        ) {

            const option =
                document.createElement(
                    "option"
                );


            option.value =
                driver.number ||
                driver.driver_number ||
                driver.abbreviation ||
                "";


            option.textContent =
                driver.abbreviation ||
                driver.name ||
                driver.driver_name ||
                option.value;


            driverSelect.appendChild(
                option
            );

        }
    );


    driverSelect.onchange =
    function () {

        dashboardState.driver =
            this.value ||
            null;


        console.log(
            "Selected driver:",
            dashboardState.driver
        );

    };

};


// ==========================================================
// START LIVE TELEMETRY
// ==========================================================

window.startDashboardLiveTelemetry =
function () {

    console.log(
        "Starting live telemetry..."
    );


    showLoading(
        "Connecting to live telemetry..."
    );


    if (
        typeof connectLiveTelemetry !==
        "function"
    ) {

        hideLoading();


        console.error(
            "connectLiveTelemetry() is not available."
        );


        showNotification(
            "WebSocket function is unavailable.",
            "error"
        );


        return null;

    }


    const socket =
        connectLiveTelemetry(

            dashboardState.year,

            dashboardState.event,

            dashboardState.session,


            // DATA
            function (
                data
            ) {

                hideLoading();


                console.log(
                    "Dashboard live data:",
                    data
                );


                dashboardState.lastTelemetry =
                    data;


                dashboardState.liveConnected =
                    data &&
                    data.status ===
                    "success";


                updateLiveStatus(
                    dashboardState.liveConnected
                );


                updateTelemetryUI(
                    data
                );

            },


            // ERROR
            function (
                error
            ) {

                hideLoading();


                dashboardState.liveConnected =
                    false;


                console.error(
                    "Live telemetry connection failed:",
                    error
                );


                updateLiveStatus(
                    false
                );


                showNotification(
                    "Live telemetry connection failed.",
                    "error"
                );

            }

        );


    return socket;

};


// ==========================================================
// UPDATE LIVE STATUS
// ==========================================================

window.updateLiveStatus =
function (
    connected
) {

    const statusElement =
        document.getElementById(
            "live-status"
        );


    if (!statusElement) {

        return;

    }


    if (
        connected
    ) {

        statusElement.textContent =
            "LIVE";


        statusElement.classList.add(
            "connected"
        );


        statusElement.classList.remove(
            "disconnected"
        );

    }
    else {

        statusElement.textContent =
            "OFFLINE";


        statusElement.classList.add(
            "disconnected"
        );


        statusElement.classList.remove(
            "connected"
        );

    }

};


// ==========================================================
// UPDATE TELEMETRY UI
// ==========================================================

window.updateTelemetryUI =
function (
    data
) {

    if (!data) {

        return;

    }


    console.log(
        "Updating telemetry UI:",
        data
    );


    if (
        data.drivers
    ) {

        if (
            typeof updateTelemetry ===
            "function"
        ) {

            updateTelemetry(
                data.drivers
            );

        }

    }


    if (
        data.speed !== undefined
        ||
        data.throttle !== undefined
        ||
        data.brake !== undefined
        ||
        data.gear !== undefined
        ||
        data.rpm !== undefined
        ||
        data.drs !== undefined
    ) {

        if (
            typeof updateTelemetry ===
            "function"
        ) {

            updateTelemetry(
                data
            );

        }

    }

};


// ==========================================================
// LAP-TIME PREDICTION
// ==========================================================

window.runDashboardPrediction =
async function (
    features
) {

    try {

        showLoading(
            "Predicting lap time..."
        );


        if (
            typeof predictLapTime !==
            "function"
        ) {

            throw new Error(
                "predictLapTime() is not available."
            );

        }


        const result =
            await predictLapTime(
                features
            );


        if (
            !result
            ||
            result.status !==
            "success"
        ) {

            throw new Error(
                result?.message ||
                "Prediction failed."
            );

        }


        dashboardState.prediction =
            result;


        updatePredictionUI(
            result
        );


        showNotification(
            "Lap prediction completed.",
            "success"
        );


        console.log(
            "Prediction:",
            result
        );


        return result;

    }
    catch (error) {

        console.error(
            "Prediction error:",
            error
        );


        showNotification(
            error.message ||
            "Lap prediction failed.",
            "error"
        );


        return null;

    }
    finally {

        hideLoading();

    }

};


// ==========================================================
// UPDATE PREDICTION UI
// ==========================================================

window.updatePredictionUI =
function (
    result
) {

    const predictionElement =
        document.getElementById(
            "predicted-lap-time"
        );


    if (!predictionElement) {

        console.warn(
            "predicted-lap-time element not found."
        );

        return;

    }


    if (
        result
        &&
        result.status ===
        "success"
    ) {

        predictionElement.textContent =
            `${Number(
                result.predicted_lap_time
            ).toFixed(3)} s`;

    }
    else {

        predictionElement.textContent =
            "--";

    }

};


// ==========================================================
// STOP LIVE TELEMETRY
// ==========================================================

window.stopDashboardLiveTelemetry =
function () {

    if (
        typeof disconnectLiveTelemetry ===
        "function"
    ) {

        disconnectLiveTelemetry();

    }


    dashboardState.liveConnected =
        false;


    updateLiveStatus(
        false
    );


    showNotification(
        "Live telemetry disconnected.",
        "info"
    );


    console.log(
        "Live telemetry stopped."
    );

};


// ==========================================================
// DOM READY
// ==========================================================

document.addEventListener(
    "DOMContentLoaded",
    async function () {

        console.log(
            "F1 Telemetry Lab frontend loaded."
        );


        // --------------------------------------------------
        // LOAD BUTTON
        // --------------------------------------------------

        const loadButton =
            document.getElementById(
                "loadButton"
            );


        if (loadButton) {

            loadButton.addEventListener(
                "click",
                async function () {

                    loadButton.textContent =
                        "LOADING...";


                    loadButton.disabled =
                        true;


                    try {

                        if (
                            typeof loadRace ===
                            "function"
                        ) {

                            await loadRace();

                        }
                        else {

                            // Fallback if race.js
                            // does not expose loadRace().
                            await loadDashboardSession(
                                dashboardState.year,
                                dashboardState.event,
                                dashboardState.session
                            );

                        }

                    }
                    catch (error) {

                        console.error(
                            "Load session error:",
                            error
                        );


                        showNotification(
                            "Unable to load session.",
                            "error"
                        );

                    }
                    finally {

                        loadButton.textContent =
                            "LOAD SESSION";


                        loadButton.disabled =
                            false;

                    }

                }
            );

        }


        // --------------------------------------------------
        // INITIAL TELEMETRY DISPLAY
        // --------------------------------------------------

        if (
            typeof updateTelemetry ===
            "function"
        ) {

            updateTelemetry({

                speed: 312,

                throttle: 98,

                brake: 0,

                gear: 8,

                rpm: 11000,

                drs: 0

            });

        }


        // --------------------------------------------------
        // INITIAL NEXT EVENT
        // --------------------------------------------------

        await loadNextEvent();


        // --------------------------------------------------
        // BACKEND INITIALIZATION
        // --------------------------------------------------

        await initializeDashboard();

    }
);


// ==========================================================
// APP.JS LOADED
// ==========================================================

console.log(
    "================================="
);


console.log(
    "F1 Telemetry Lab app.js loaded successfully."
);


console.log(
    "Next Event system loaded."
);


console.log(
    "Phase 8.7 ready."
);


console.log(
    "================================="
);