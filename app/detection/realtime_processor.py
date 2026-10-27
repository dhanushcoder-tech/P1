import cv2
import time

from app.detection.vehicle_detector import (
    VehicleDetector
)


class RealtimeTrafficProcessor:

    def __init__(
        self,
        video_path,
        confidence=0.40,
        process_every_n_frames=10
    ):

        self.video_path = video_path

        self.confidence = confidence

        self.process_every_n_frames = (
            process_every_n_frames
        )

        self.detector = VehicleDetector(
            confidence=confidence
        )

    # ============================================================
    # PROCESS REAL-TIME STREAM
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

        processed_frames = 0

        start_time = time.time()

        latest_data = None

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

            processed_frames += 1

            # ----------------------------------------------------
            # YOLO DETECTION
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

            # ----------------------------------------------------
            # TRAFFIC DATA
            # ----------------------------------------------------

            vehicle_count = (
                counts["total"]
            )

            elapsed = (
                time.time()
                - start_time
            )

            video_time = (
                frame_number / fps
            )

            latest_data = {

                "frame":
                    frame_number,

                "video_time":
                    round(
                        video_time,
                        2
                    ),

                "elapsed_time":
                    round(
                        elapsed,
                        2
                    ),

                "vehicle_count":
                    vehicle_count,

                "cars":
                    counts["car"],

                "motorcycles":
                    counts["motorcycle"],

                "buses":
                    counts["bus"],

                "trucks":
                    counts["truck"]
            }

            # ----------------------------------------------------
            # PRINT LIVE DATA
            # ----------------------------------------------------

            print(
                f"\n⏱️ Video Time : "
                f"{video_time:.1f}s"
            )

            print(
                f"🎞️ Frame      : "
                f"{frame_number}"
            )

            print(
                f"🚗 Vehicles   : "
                f"{vehicle_count}"
            )

            print(
                f"   Cars        : "
                f"{counts['car']}"
            )

            print(
                f"   Motorcycles : "
                f"{counts['motorcycle']}"
            )

            print(
                f"   Buses       : "
                f"{counts['bus']}"
            )

            print(
                f"   Trucks      : "
                f"{counts['truck']}"
            )

        cap.release()

        return {

            "total_frames":
                frame_number,

            "processed_frames":
                processed_frames,

            "last_data":
                latest_data
        }