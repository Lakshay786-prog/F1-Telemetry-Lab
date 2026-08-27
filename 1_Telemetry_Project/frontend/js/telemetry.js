/*
=========================================================
UPDATE TELEMETRY
=========================================================
*/

function updateTelemetry(data) {


    const speed =
        Number(data.speed ?? 0);


    const throttle =
        Number(data.throttle ?? 0);


    const brake =
        Number(data.brake ?? 0);


    const gear =
        Number(data.gear ?? 0);


    const rpm =
        Number(data.rpm ?? 0);


    const drs =
        Number(data.drs ?? 0);



    /*
    SPEED
    */

    document.getElementById(
        "speed"
    ).textContent =
        Math.round(speed);


    /*
    THROTTLE
    */

    document.getElementById(
        "throttle"
    ).textContent =
        Math.round(throttle);


    /*
    BRAKE
    */

    document.getElementById(
        "brake"
    ).textContent =
        Math.round(brake);


    /*
    GEAR
    */

    document.getElementById(
        "gear"
    ).textContent =
        gear;


    /*
    RPM
    */

    document.getElementById(
        "rpm"
    ).textContent =
        Math.round(rpm);


    /*
    DRS
    */

    const drsElement =
        document.getElementById("drs");


    drsElement.textContent =
        drs > 0
            ? "ON"
            : "OFF";


    if (drs > 0) {

        drsElement.classList.add("red");

    }

    else {

        drsElement.classList.remove("red");

    }


    /*
    GRAPH VALUES
    */

    document.getElementById(
        "speedValue"
    ).textContent =
        `${Math.round(speed)} KM/H`;


    document.getElementById(
        "throttleValue"
    ).textContent =
        `${Math.round(throttle)}%`;


    document.getElementById(
        "brakeValue"
    ).textContent =
        `${Math.round(brake)}%`;

}