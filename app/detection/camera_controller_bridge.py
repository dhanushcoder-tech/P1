from app.detection.camera_optimizer import (
    CameraSignalOptimizer
)


class CameraControllerBridge:

    def __init__(
        self,
        video_path,
        confidence=0.40,
        frame_interval=10
    ):

        self.optimizer = CameraSignalOptimizer(
            video_path=video_path,
            confidence=confidence,
            frame_interval=frame_interval
        )

    # ============================================================
    # GET AI DECISION
    # ============================================================

    def get_signal_decision(self):

        result = self.optimizer.optimize()

        return {
            "vehicle_count":
                result["vehicle_count"],

            "queue_length":
                result["queue_length"],

            "waiting_time":
                result["waiting_time"],

            "traffic_density":
                result["traffic_density"],

            "green_time":
                result["recommended_green_time"],

            "traffic_condition":
                result["decision"]
        }

    # ============================================================
    # APPLY DECISION
    # ============================================================

    def apply_to_junction(
        self,
        junction_id,
        direction="NORTH_SOUTH"
    ):

        decision = self.get_signal_decision()

        return {
            "junction_id":
                junction_id,

            "direction":
                direction,

            "vehicle_count":
                decision["vehicle_count"],

            "queue_length":
                decision["queue_length"],

            "waiting_time":
                decision["waiting_time"],

            "traffic_density":
                decision["traffic_density"],

            "green_time":
                decision["green_time"],

            "traffic_condition":
                decision["traffic_condition"],

            "source":
                "REAL_CAMERA"
        }