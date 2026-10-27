import cv2
import time

from app.detection.vehicle_detector import (
    VehicleDetector
)


class RealtimeSignalController:

    def __init__(
        self,
        video_path,
        confidence=0.40,
        process_every_n_frames=10,
        min_green=20,
        max_green=90
    ):

        self.video_path = video_path

        self.confidence = confidence

        self.process_every_n_frames = (
            process_every_n_frames
        )

        self.min_green = min_green

        self.max_green = max_green

        self.detector = VehicleDetector(
            confidence=confidence
        )

    # ============================================================
    # SIGNAL OPTIMIZATION
    # ============================================================

    def calculate_green_time(
        self,
        vehicle_count
    ):

        if vehicle_count >= 15:

            green_time = 75

        elif vehicle_count >= 12:

            green_time = 65

        elif vehicle_count >= 10:

            green_time = 55

        elif vehicle_count >= 7:

            green_time = 45

        elif vehicle_count >= 4:

            green_time = 35

        else:

            green_time = 25

        return max(
            self.min_green,
            min(
                green_time,
                self.max_green
            )
        )

    # ============================================================
    # TRAFFIC LEVEL
    # ============================================================

    def traffic_level(
        self,
        vehicle_count
    ):

        if vehicle_count >= 15:

            return "SEVERE"

        elif vehicle_count >= 12:

            return "HIGH"

        elif vehicle_count >= 8:

            return "MODERATE"

        elif vehicle_count >= 4:

            return "LOW"

        return "VERY LOW"

    # ============================================================
    # PROCESS CAMERA
    # ============================================================

    def run(self):

        cap = cv2.VideoCapture(
            self.video_path
        )

        if not cap.isOpened():

            raise RuntimeError(
                f"Could not open video: "
                f"{self.video_path}"
            )

        fps = cap.get(
            cv2.CAP_PROP_FPS
        )

        if fps <= 0:

            fps = 30.0

        frame_number = 0

        decisions = []

        start_time = time.time()

        while True:

            ret, frame = cap.read()

            if not ret:

                break

            frame_number += 1

            if (
                frame_number %
                self.process_every_n_frames
                != 0
            ):

                continue

            # ----------------------------------------------------
            # YOLO
            # ----------------------------------------------------

            detections = (
                self.detector.detect(
                    frame
                )
            )

            counts = (
                self.detector.count(
                    detections
                )
            )

            vehicle_count = (
                counts["total"]
            )

            # ----------------------------------------------------
            # AI SIGNAL DECISION
            # ----------------------------------------------------

            green_time = (
                self.calculate_green_time(
                    vehicle_count
                )
            )

            level = (
                self.traffic_level(
                    vehicle_count
                )
            )

            video_time = (
                frame_number / fps
            )

            decision = {

                "frame":
                    frame_number,

                "timestamp":
                    round(
                        video_time,
                        2
                    ),

                "vehicle_count":
                    vehicle_count,

                "green_time":
                    green_time,

                "traffic_level":
                    level,

                "direction":
                    "NORTH_SOUTH"
            }

            decisions.append(
                decision
            )

            # ----------------------------------------------------
            # DISPLAY DECISION IN TERMINAL
            # ----------------------------------------------------

            print(
                "\n" + "-" * 65
            )

            print(
                f"⏱️ Time          : "
                f"{video_time:.1f}s"
            )

            print(
                f"🚗 Vehicles      : "
                f"{vehicle_count}"
            )

            print(
                f"📊 Traffic Level : "
                f"{level}"
            )

            print(
                f"🧠 AI Decision   : "
                f"GREEN {green_time}s"
            )

            print(
                f"🚦 Direction     : "
                f"NORTH → SOUTH"
            )

            print(
                "🔴 Conflicting directions → RED"
            )

        cap.release()

        elapsed = (
            time.time()
            - start_time
        )

        return {

            "total_frames":
                frame_number,

            "decisions":
                decisions,

            "processing_time":
                round(
                    elapsed,
                    2
                )
        }