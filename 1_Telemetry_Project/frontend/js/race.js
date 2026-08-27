const yearSelect =
    document.getElementById("yearSelect");

const raceSelect =
    document.getElementById("raceSelect");

const sessionSelect =
    document.getElementById("sessionSelect");

const driverSelect =
    document.getElementById("driverSelect");

const lapSelect =
    document.getElementById("lapSelect");


/*
=========================================================
UPDATE DASHBOARD
=========================================================
*/

function updateRaceInformation() {

    const race =
        raceSelect.value;

    const session =
        sessionSelect.value;

    const driver =
        driverSelect.value;

    const lap =
        lapSelect.value;


    document.getElementById(
        "circuitName"
    ).textContent =
        race.toUpperCase();


    document.getElementById(
        "lapNumber"
    ).textContent =
        lap;


    document.getElementById(
        "trackDriver"
    ).textContent =
        driver;


    document.getElementById(
        "trackSession"
    ).textContent =
        session === "R"
            ? "RACE"
            : session;

}


/*
=========================================================
LOAD RACE
=========================================================
*/

async function loadRace() {

    updateRaceInformation();


    const request = {

        year:
            yearSelect.value,

        race:
            raceSelect.value,

        session:
            sessionSelect.value,

        driver:
            driverSelect.value,

        lap:
            lapSelect.value

    };


    console.log(
        "Selected F1 session:",
        request
    );


    /*
    =====================================================
    IMPORTANT

    We will connect this to your exact FastAPI
    endpoint after checking your Phase 4 backend.
    =====================================================
    */

}