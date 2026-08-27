/*
=========================================================
UPDATE CAR POSITION
=========================================================
*/

function updateCarPosition(
    x,
    y
) {

    const car =
        document.getElementById("car");


    if (!car) {

        return;

    }


    /*
    Normalize coordinates
    between 0 and 1.
    */

    const normalizedX =
        Math.max(
            0,
            Math.min(
                1,
                Number(x) || 0
            )
        );


    const normalizedY =
        Math.max(
            0,
            Math.min(
                1,
                Number(y) || 0
            )
        );


    car.style.left =
        `${10 + normalizedX * 80}%`;


    car.style.top =
        `${10 + normalizedY * 80}%`;

}