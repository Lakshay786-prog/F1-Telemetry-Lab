from pathlib import Path

out = Path("/mnt/data/F1TelemetryLab_corrected_phase3_5")
out.mkdir(parents=True, exist_ok=True)

sync_code = r'''import pandas as pd
import numpy as np


class TelemetrySynchronizer:
    """
    Synchronizes Arcade playback time with FastF1 telemetry.

    The telemetry is converted to relative seconds starting at 0.
    A telemetry sample is selected using searchsorted, which is much
    faster than calculating the distance to every sample on every frame.
    """

    def __init__(self, telemetry):
        self.telemetry = telemetry.copy().reset_index(drop=True)

        required = [
            "SessionTime",
            "X",
            "Y",
            "Speed",
            "Throttle",
            "Brake",
            "nGear",
            "RPM",
            "DRS",
        ]

        missing = [
            column for column in required
            if column not in self.telemetry.columns
        ]

        if missing:
            raise ValueError(
                "Missing telemetry columns: "
                + ", ".join(missing)
            )

        self.telemetry = (
            self.telemetry
            .dropna(subset=["SessionTime", "X", "Y"])
            .reset_index(drop=True)
        )

        if self.telemetry.empty:
            raise ValueError("Telemetry contains no valid samples.")

        # FastF1 SessionTime is normally a pandas Timedelta.
        self.time_seconds = (
            pd.to_timedelta(self.telemetry["SessionTime"])
            .dt.total_seconds()
            .to_numpy(dtype=float)
        )

        # Make time relative to the first telemetry sample.
        self.time_seconds -= self.time_seconds[0]

        # Remove duplicate/non-increasing timestamps.
        keep = np.r_[True, np.diff(self.time_seconds) > 0]

        self.time_seconds = self.time_seconds[keep]
        self.telemetry = (
            self.telemetry.loc[keep]
            .reset_index(drop=True)
        )

        if len(self.telemetry) < 2:
            raise ValueError(
                "At least two telemetry samples are required."
            )

        self.total_time = float(self.time_seconds[-1])

    def get_index(self, playback_time):
        """
        Return the telemetry index closest to playback_time.
        """
        t = float(
            np.clip(
                playback_time,
                0.0,
                self.total_time
            )
        )

        right = np.searchsorted(
            self.time_seconds,
            t,
            side="left"
        )

        if right <= 0:
            return 0

        if right >= len(self.time_seconds):
            return len(self.time_seconds) - 1

        left = right - 1

        if (
            t - self.time_seconds[left]
            <=
            self.time_seconds[right] - t
        ):
            return left

        return right

    @staticmethod
    def _number(value, default=0.0):
        if pd.isna(value):
            return default
        return float(value)

    def get_values(self, playback_time):
        """
        Return all telemetry values synchronized to playback_time.
        """
        index = self.get_index(playback_time)
        row = self.telemetry.iloc[index]

        return {
            "index": index,
            "time": float(self.time_seconds[index]),
            "x": self._number(row["X"]),
            "y": self._number(row["Y"]),
            "speed": self._number(row["Speed"]),
            "throttle": self._number(row["Throttle"]),
            "brake": self._number(row["Brake"]),
            "gear": int(self._number(row["nGear"])),
            "rpm": self._number(row["RPM"]),
            "drs": int(self._number(row["DRS"])),
        }


if __name__ == "__main__":
    import fastf1
    from pathlib import Path

    BASE_DIR = Path(__file__).resolve().parent.parent
    CACHE_DIR = BASE_DIR / "data" / "fastf1_cache"

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(CACHE_DIR))

    print("\n================================")
    print("   TELEMETRY SYNCHRONIZATION")
    print("================================")

    session = fastf1.get_session(2024, "Monza", "R")
    session.load()

    laps = session.laps.pick_drivers("VER")
    lap_data = laps[laps["LapNumber"] == 20]

    if lap_data.empty:
        raise ValueError("Lap 20 not found for VER.")

    lap = lap_data.iloc[0]

    telemetry = (
        lap.get_telemetry()
        .dropna(subset=["SessionTime", "X", "Y"])
        .reset_index(drop=True)
    )

    sync = TelemetrySynchronizer(telemetry)

    print(f"Telemetry samples : {len(sync.telemetry)}")
    print(f"Lap duration      : {sync.total_time:.3f} seconds")

    print("\n--------------------------------")
    print("Synchronization test")
    print("--------------------------------")

    for t in np.linspace(
        0,
        sync.total_time,
        6
    ):
        values = sync.get_values(t)

        print(
            f"Time {values['time']:7.2f}s | "
            f"Sample {values['index']:4d} | "
            f"Speed {values['speed']:6.1f} | "
            f"Throttle {values['throttle']:5.1f}% | "
            f"Brake {values['brake']:5.1f} | "
            f"Gear {values['gear']} | "
            f"RPM {values['rpm']:6.0f} | "
            f"DRS {values['drs']}"
        )
'''

animation_code = r'''import arcade
import fastf1
from pathlib import Path
import math

from telemetry_sync import TelemetrySynchronizer


# ==========================================================
# PROJECT SETTINGS
# ==========================================================

YEAR = 2024
RACE = "Monza"
SESSION_TYPE = "R"

DRIVER = "VER"
LAP_NUMBER = 20


# ==========================================================
# CACHE
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = BASE_DIR / "data" / "fastf1_cache"

CACHE_DIR.mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))


# ==========================================================
# LOAD TELEMETRY
# ==========================================================

def load_lap_telemetry():

    print("\n================================")
    print("       F1 TELEMETRY LAB")
    print("================================")

    print(
        f"\nLoading {YEAR} {RACE} - {SESSION_TYPE}"
    )

    session = fastf1.get_session(
        YEAR,
        RACE,
        SESSION_TYPE
    )

    session.load()

    print("Session loaded successfully!")

    laps = session.laps.pick_drivers(DRIVER)

    lap_data = laps[
        laps["LapNumber"] == LAP_NUMBER
    ]

    if lap_data.empty:
        raise ValueError(
            f"Lap {LAP_NUMBER} not found for {DRIVER}"
        )

    lap = lap_data.iloc[0]

    telemetry = lap.get_telemetry()

    required = [
        "SessionTime",
        "X",
        "Y",
        "Speed",
        "Throttle",
        "Brake",
        "nGear",
        "RPM",
        "DRS",
    ]

    missing = [
        column
        for column in required
        if column not in telemetry.columns
    ]

    if missing:
        raise ValueError(
            "Missing telemetry columns: "
            + ", ".join(missing)
        )

    telemetry = (
        telemetry
        .dropna(
            subset=[
                "SessionTime",
                "X",
                "Y"
            ]
        )
        .reset_index(drop=True)
    )

    print(
        f"Telemetry samples: {len(telemetry)}"
    )

    return telemetry, lap


# ==========================================================
# ARCADE WINDOW
# ==========================================================

class F1TelemetryWindow(arcade.Window):

    def __init__(
        self,
        telemetry,
        lap
    ):

        super().__init__(
            width=1280,
            height=800,
            title="F1 Telemetry Lab"
        )

        self.telemetry = telemetry
        self.lap = lap

        # --------------------------------------------------
        # SYNCHRONIZER
        # --------------------------------------------------

        self.synchronizer = TelemetrySynchronizer(
            telemetry
        )

        # --------------------------------------------------
        # PLAYBACK
        # --------------------------------------------------

        self.playback_time = 0.0
        self.playback_speed = 1.0
        self.paused = False

        # --------------------------------------------------
        # TRACK
        # --------------------------------------------------

        self.x_data = telemetry["X"].to_numpy(dtype=float)
        self.y_data = telemetry["Y"].to_numpy(dtype=float)

        min_x = self.x_data.min()
        max_x = self.x_data.max()
        min_y = self.y_data.min()
        max_y = self.y_data.max()

        track_width = max_x - min_x
        track_height = max_y - min_y

        if track_width <= 0 or track_height <= 0:
            raise ValueError("Invalid track dimensions.")

        margin_x = 80
        margin_y = 90

        scale_x = (
            (self.width - 2 * margin_x)
            / track_width
        )

        scale_y = (
            (self.height - 2 * margin_y)
            / track_height
        )

        self.track_scale = min(
            scale_x,
            scale_y
        )

        self.track_center_x = (
            min_x + max_x
        ) / 2

        self.track_center_y = (
            min_y + max_y
        ) / 2

        self.track_points = [
            self.convert_position(x, y)
            for x, y in zip(
                self.x_data,
                self.y_data
            )
        ]

        # --------------------------------------------------
        # COLORS
        # --------------------------------------------------

        self.bg = (7, 7, 7)
        self.track = (48, 48, 48)
        self.track_inner = (105, 105, 105)
        self.red = (225, 6, 0)
        self.white = (245, 245, 245)
        self.gray = (165, 165, 165)
        self.panel = (18, 18, 18)

    # ======================================================
    # POSITION CONVERSION
    # ======================================================

    def convert_position(self, x, y):

        screen_x = (
            (x - self.track_center_x)
            * self.track_scale
            + self.width / 2
        )

        screen_y = (
            (y - self.track_center_y)
            * self.track_scale
            + self.height / 2
        )

        return screen_x, screen_y

    # ======================================================
    # UPDATE
    # ======================================================

    def on_update(self, delta_time):

        if self.paused:
            return

        # Actual elapsed time × playback speed.
        self.playback_time += (
            float(delta_time)
            * self.playback_speed
        )

        if (
            self.playback_time
            >= self.synchronizer.total_time
        ):
            self.playback_time = 0.0

    # ======================================================
    # DRAW TRACK
    # ======================================================

    def draw_track(self):

        points = self.track_points

        # Wide track
        for i in range(len(points) - 1):

            arcade.draw_line(
                points[i][0],
                points[i][1],
                points[i + 1][0],
                points[i + 1][1],
                self.track,
                12
            )

        # Thin center/racing line
        for i in range(len(points) - 1):

            arcade.draw_line(
                points[i][0],
                points[i][1],
                points[i + 1][0],
                points[i + 1][1],
                self.red,
                2
            )

    # ======================================================
    # DRAW CAR
    # ======================================================

    def draw_car(
        self,
        x,
        y,
        angle
    ):

        # Convert degrees to radians.
        radians = math.radians(angle)

        # Direction vector.
        dx = math.cos(radians)
        dy = math.sin(radians)

        # Perpendicular vector.
        px = -dy
        py = dx

        # Small F1-style arrow/body.
        nose = (
            x + dx * 18,
            y + dy * 18
        )

        rear = (
            x - dx * 13,
            y - dy * 13
        )

        left = (
            rear[0] + px * 7,
            rear[1] + py * 7
        )

        right = (
            rear[0] - px * 7,
            rear[1] - py * 7
        )

        arcade.draw_triangle_filled(
            nose[0],
            nose[1],
            left[0],
            left[1],
            right[0],
            right[1],
            self.red
        )

        arcade.draw_circle_filled(
            x,
            y,
            5,
            self.white
        )

        # Rear wing
        wing_left = (
            rear[0] + px * 8,
            rear[1] + py * 8
        )

        wing_right = (
            rear[0] - px * 8,
            rear[1] - py * 8
        )

        arcade.draw_line(
            wing_left[0],
            wing_left[1],
            wing_right[0],
            wing_right[1],
            self.white,
            3
        )

    # ======================================================
    # GET CAR ANGLE
    # ======================================================

    def get_car_angle(self, index):

        if index >= len(self.track_points) - 1:
            index = len(self.track_points) - 2

        x1, y1 = self.track_points[index]
        x2, y2 = self.track_points[index + 1]

        angle = math.degrees(
            math.atan2(
                y2 - y1,
                x2 - x1
            )
        )

        return angle

    # ======================================================
    # DRAW TELEMETRY PANEL
    # ======================================================

    def draw_panel(self, values):

        panel_x = 930
        panel_y = 600

        arcade.draw_lrwh_rectangle_filled(
            panel_x - 25,
            175,
            310,
            450,
            self.panel
        )

        arcade.draw_text(
            "LIVE TELEMETRY",
            panel_x,
            panel_y,
            self.red,
            20,
            bold=True
        )

        data = [
            ("SPEED", f"{values['speed']:.0f} km/h"),
            ("THROTTLE", f"{values['throttle']:.0f} %"),
            ("BRAKE", f"{values['brake']:.0f}"),
            ("GEAR", f"{values['gear']}"),
            ("RPM", f"{values['rpm']:.0f}"),
            ("DRS", f"{values['drs']}"),
        ]

        y = panel_y - 55

        for name, value in data:

            arcade.draw_text(
                name,
                panel_x,
                y,
                self.gray,
                12
            )

            arcade.draw_text(
                value,
                panel_x + 125,
                y,
                self.white,
                14,
                bold=True
            )

            y -= 45

    # ======================================================
    # DRAW
    # ======================================================

    def on_draw(self):

        self.clear(self.bg)

        self.draw_track()

        # --------------------------------------------------
        # SYNCHRONIZED DATA
        # --------------------------------------------------

        values = self.synchronizer.get_values(
            self.playback_time
        )

        car_x, car_y = self.convert_position(
            values["x"],
            values["y"]
        )

        angle = self.get_car_angle(
            values["index"]
        )

        self.draw_car(
            car_x,
            car_y,
            angle
        )

        # --------------------------------------------------
        # HEADER
        # --------------------------------------------------

        arcade.draw_text(
            "F1 TELEMETRY LAB",
            35,
            self.height - 50,
            self.white,
            24,
            bold=True
        )

        arcade.draw_text(
            f"{RACE.upper()}  |  "
            f"{DRIVER}  |  "
            f"LAP {LAP_NUMBER}",
            35,
            self.height - 82,
            self.gray,
            13
        )

        # --------------------------------------------------
        # TELEMETRY PANEL
        # --------------------------------------------------

        self.draw_panel(values)

        # --------------------------------------------------
        # PLAYBACK
        # --------------------------------------------------

        status = (
            "PAUSED"
            if self.paused
            else "PLAYING"
        )

        arcade.draw_text(
            f"{status}   |   "
            f"TIME {values['time']:.2f}s / "
            f"{self.synchronizer.total_time:.2f}s   |   "
            f"SPEED x{self.playback_speed:.1f}",
            35,
            55,
            self.gray,
            12
        )

        arcade.draw_text(
            "SPACE: Pause/Play     "
            "R: Restart     "
            "+/-: Playback Speed",
            35,
            25,
            self.gray,
            10
        )

    # ======================================================
    # KEYBOARD
    # ======================================================

    def on_key_press(
        self,
        key,
        modifiers
    ):

        if key == arcade.key.SPACE:

            self.paused = not self.paused

        elif key == arcade.key.R:

            self.playback_time = 0.0

        elif (
            key == arcade.key.PLUS
            or key == arcade.key.NUM_ADD
        ):

            self.playback_speed = min(
                10.0,
                self.playback_speed + 0.5
            )

        elif (
            key == arcade.key.MINUS
            or key == arcade.key.NUM_SUBTRACT
        ):

            self.playback_speed = max(
                0.5,
                self.playback_speed - 0.5
            )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    telemetry, lap = load_lap_telemetry()

    window = F1TelemetryWindow(
        telemetry,
        lap
    )

    arcade.run()
'''

(out / "telemetry_sync.py").write_text(sync_code, encoding="utf-8")
(out / "car_animation.py").write_text(animation_code, encoding="utf-8")

print("Files created:")
print(out / "telemetry_sync.py")
print(out / "car_animation.py")
