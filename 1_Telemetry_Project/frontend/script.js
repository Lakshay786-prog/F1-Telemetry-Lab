const driverSelect = document.getElementById("driver");
const lapSelect = document.getElementById("lap");

const speed = document.getElementById("speed");
const throttle = document.getElementById("throttle");
const brake = document.getElementById("brake");
const gear = document.getElementById("gear");
const rpm = document.getElementById("rpm");

const currentLap = document.getElementById("current-lap");
const car = document.getElementById("car");


function updateTelemetry() {

    const selectedLap = lapSelect.value;

    if (selectedLap) {
        currentLap.textContent = selectedLap;
    }

    // Temporary demo values
    speed.textContent =
        Math.floor(250 + Math.random() * 70);

    throttle.textContent =
        Math.floor(60 + Math.random() * 40);

    brake.textContent =
        Math.floor(Math.random() * 30);

    gear.textContent =
        Math.floor(5 + Math.random() * 4);

    rpm.textContent =
        Math.floor(9000 + Math.random() * 3000)
        .toLocaleString();

    // Move the demo car
    const position =
        20 + Math.random() * 60;

    car.style.left = `${position}%`;
}


driverSelect.addEventListener(
    "change",
    updateTelemetry
);

lapSelect.addEventListener(
    "change",
    updateTelemetry
);