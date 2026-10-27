from app.detection.camera_traffic import (
    CameraTrafficProcessor
)


class CameraSignalOptimizer:

    def __init__(
        self,
        video_path,
        confidence=0.40,
        frame_interval=10
    ):

        self.processor = CameraTrafficProcessor(
            video_path=video_path,
            confidence=confidence,
            frame_interval=frame_interval
        )

    # ============================================================
    # GET CAMERA TRAFFIC
    # ============================================================

    def get_traffic_data(self):

        samples = self.processor.process()

        if not samples:
            raise RuntimeError(
                "No traffic data received from camera."
            )

        return (
            self.processor.create_controller_input(
                samples
            )
        )

    # ============================================================
    # CALCULATE GREEN TIME
    # ============================================================

    def calculate_green_time(
        self,
        traffic_data
    ):

        vehicle_count = (
            traffic_data["vehicle_count"]
        )

        queue_length = (
            traffic_data["queue_length"]
        )

        density = (
            traffic_data["traffic_density"]
        )

        # --------------------------------------------------------
        # BASE GREEN TIME
        # --------------------------------------------------------

        green_time = 30.0

        # --------------------------------------------------------
        # VEHICLE PRESSURE
        # --------------------------------------------------------

        if vehicle_count >= 15:

            green_time += 20

        elif vehicle_count >= 10:

            green_time += 12

        elif vehicle_count >= 5:

            green_time += 6

        # --------------------------------------------------------
        # QUEUE PRESSURE
        # --------------------------------------------------------

        if queue_length >= 15:

            green_time += 15

        elif queue_length >= 10:

            green_time += 10

        elif queue_length >= 5:

            green_time += 5

        # --------------------------------------------------------
        # DENSITY PRESSURE
        # --------------------------------------------------------

        if density >= 20:

            green_time += 15

        elif density >= 10:

            green_time += 8

        elif density >= 5:

            green_time += 4

        # --------------------------------------------------------
        # SAFETY LIMIT
        # --------------------------------------------------------

        green_time = max(
            20.0,
            min(
                green_time,
                90.0
            )
        )

        return round(
            green_time,
            2
        )

    # ============================================================
    # COMPLETE DECISION
    # ============================================================

    def optimize(self):

        traffic_data = (
            self.get_traffic_data()
        )

        green_time = (
            self.calculate_green_time(
                traffic_data
            )
        )

        if green_time >= 70:

            decision = "HIGH CONGESTION"

        elif green_time >= 50:

            decision = "MODERATE CONGESTION"

        else:

            decision = "NORMAL TRAFFIC"

        return {

            "vehicle_count":
                traffic_data["vehicle_count"],

            "queue_length":
                traffic_data["queue_length"],

            "waiting_time":
                traffic_data["waiting_time"],

            "traffic_density":
                traffic_data["traffic_density"],

            "recommended_green_time":
                green_time,

            "decision":
                decision
        }