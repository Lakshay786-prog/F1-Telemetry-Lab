/*
=========================================================
F1 TELEMETRY LAB
APPLICATION CONTROLLER
=========================================================
*/


document.addEventListener(
    "DOMContentLoaded",
    () => {


        const loadButton =
            document.getElementById(
                "loadButton"
            );


        /*
        =================================================
        LOAD BUTTON
        =================================================
        */

        loadButton.addEventListener(
            "click",
            async () => {


                loadButton.textContent =
                    "LOADING...";


                loadButton.disabled =
                    true;


                try {

                    await loadRace();

                }

                catch (error) {

                    console.error(
                        error
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


        /*
        =================================================
        INITIAL DASHBOARD
        =================================================
        */

        updateRaceInformation();


        /*
        =================================================
        TEMPORARY TELEMETRY

        These values will later be replaced
        with FastAPI telemetry.
        =================================================
        */

        updateTelemetry({

            speed: 312,

            throttle: 98,

            brake: 0,

            gear: 8,

            rpm: 11000,

            drs: 0

        });


        /*
        =================================================
        BACKEND STATUS
        =================================================
        */

        checkBackend()
            .then(
                connected => {

                    if (connected) {

                        console.log(
                            "FastAPI backend connected."
                        );

                    }

                    else {

                        console.log(
                            "FastAPI backend not connected yet."
                        );

                    }

                }
            );

    }
);