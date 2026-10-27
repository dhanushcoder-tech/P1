import cv2

from app.detection.vehicle_detector import VehicleDetector


class CameraTrafficProcessor:

    def __init__(
        self,
        video_path,
        confidence=0.40,
        frame_interval=10
    ):

        self.video_path = video_path
        self.confidence = confidence
        self.frame_interval = frame_interval

        self.detector = VehicleDetector(
            confidence=confidence
        )

    # ============================================================
    # PROCESS VIDEO
    # ============================================================

    def process(self):

        cap = cv2.VideoCapture(
            self.video_path
        )

        if not cap.isOpened():

            raise RuntimeError(
                f"Could not open video: "
                f"{self.video_path}"
            )

        width = int(
            cap.get(
                cv2.CAP_PROP_FRAME_WIDTH
            )
        )

        height = int(
            cap.get(
                cv2.CAP_PROP_FRAME_HEIGHT
            )
        )

        fps = cap.get(
            cv2.CAP_PROP_FPS
        )

        roi = (
            int(width * 0.10),
            int(height * 0.30),
            int(width * 0.90),
            int(height * 0.90)
        )

        frame_number = 0

        samples = []

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            frame_number += 1

            if (
                frame_number %
                self.frame_interval
                != 0
            ):
                continue

            current_time = (
                frame_number / fps
                if fps > 0
                else 0
            )

            detections = (
                self.detector.detect(
                    frame
                )
            )

            roi_detections = (
                self.detector.filter_roi(
                    detections,
                    roi
                )
            )

            counts = (
                self.detector.count(
                    roi_detections
                )
            )

            density = (
                self.detector.calculate_roi_density(
                    frame,
                    roi_detections,
                    roi
                )
            )

            level = (
                self.detector.density_level(
                    density
                )
            )

            samples.append({

                "timestamp":
                    round(current_time, 2),

                "vehicle_count":
                    counts["total"],

                "car_count":
                    counts["car"],

                "motorcycle_count":
                    counts["motorcycle"],

                "bus_count":
                    counts["bus"],

                "truck_count":
                    counts["truck"],

                "density":
                    density,

                "traffic_level":
                    level

            })

        cap.release()

        return samples

    # ============================================================
    # CREATE TRAFFIC INPUT
    # ============================================================

    def create_controller_input(
        self,
        samples
    ):

        if not samples:

            return {

                "vehicle_count": 0,

                "queue_length": 0,

                "waiting_time": 0.0,

                "traffic_density": 0.0
            }

        vehicle_counts = [
            sample["vehicle_count"]
            for sample in samples
        ]

        densities = [
            sample["density"]
            for sample in samples
        ]

        average_vehicle_count = (
            sum(vehicle_counts)
            /
            len(vehicle_counts)
        )

        average_density = (
            sum(densities)
            /
            len(densities)
        )

        maximum_queue = max(
            vehicle_counts
        )

        return {

            "vehicle_count":
                round(
                    average_vehicle_count,
                    2
                ),

            "queue_length":
                maximum_queue,

            "waiting_time":
                0.0,

            "traffic_density":
                round(
                    average_density,
                    2
                )
        }