from ultralytics import YOLO
import cv2


class VehicleDetector:

    VEHICLE_CLASSES = {
        2: "car",
        3: "motorcycle",
        5: "bus",
        7: "truck"
    }

    def __init__(
        self,
        model_path="yolo11n.pt",
        confidence=0.40
    ):
        self.model = YOLO(model_path)
        self.confidence = confidence

    # ============================================================
    # DETECT VEHICLES
    # ============================================================

    def detect(self, frame):

        results = self.model.predict(
            source=frame,
            conf=self.confidence,
            verbose=False
        )

        detections = []

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                class_id = int(
                    box.cls[0].item()
                )

                confidence = float(
                    box.conf[0].item()
                )

                if class_id not in self.VEHICLE_CLASSES:
                    continue

                x1, y1, x2, y2 = (
                    box.xyxy[0]
                    .cpu()
                    .numpy()
                    .tolist()
                )

                detections.append({
                    "class_id": class_id,
                    "class_name":
                        self.VEHICLE_CLASSES[class_id],
                    "confidence":
                        round(confidence, 3),
                    "bbox": [
                        int(x1),
                        int(y1),
                        int(x2),
                        int(y2)
                    ]
                })

        return detections

    # ============================================================
    # COUNT VEHICLES
    # ============================================================

    def count(self, detections):

        counts = {
            "car": 0,
            "motorcycle": 0,
            "bus": 0,
            "truck": 0
        }

        for detection in detections:

            vehicle_type = (
                detection["class_name"]
            )

            if vehicle_type in counts:

                counts[vehicle_type] += 1

        counts["total"] = sum(
            counts.values()
        )

        return counts

    # ============================================================
    # ROI CHECK
    # ============================================================

    def is_inside_roi(
        self,
        detection,
        roi
    ):

        x1, y1, x2, y2 = (
            detection["bbox"]
        )

        rx1, ry1, rx2, ry2 = roi

        center_x = (
            x1 + x2
        ) // 2

        center_y = (
            y1 + y2
        ) // 2

        return (
            rx1 <= center_x <= rx2
            and
            ry1 <= center_y <= ry2
        )

    # ============================================================
    # FILTER ROI
    # ============================================================

    def filter_roi(
        self,
        detections,
        roi
    ):

        return [
            detection
            for detection in detections
            if self.is_inside_roi(
                detection,
                roi
            )
        ]

    # ============================================================
    # ROI DENSITY
    # ============================================================

    def calculate_roi_density(
        self,
        frame,
        detections,
        roi
    ):

        rx1, ry1, rx2, ry2 = roi

        roi_width = max(
            0,
            rx2 - rx1
        )

        roi_height = max(
            0,
            ry2 - ry1
        )

        roi_area = (
            roi_width *
            roi_height
        )

        if roi_area <= 0:
            return 0.0

        occupied_area = 0

        for detection in detections:

            x1, y1, x2, y2 = (
                detection["bbox"]
            )

            vehicle_area = (
                max(0, x2 - x1)
                *
                max(0, y2 - y1)
            )

            occupied_area += vehicle_area

        density = (
            occupied_area /
            roi_area
        ) * 100

        return round(
            min(density, 100.0),
            2
        )

    # ============================================================
    # DENSITY LEVEL
    # ============================================================

    def density_level(
        self,
        density
    ):

        if density < 5:
            return "LOW"

        elif density < 15:
            return "MODERATE"

        return "HIGH"

    # ============================================================
    # ESTIMATE WAITING TIME
    # ============================================================

    def estimate_waiting_time(
        self,
        queue_history,
        current_time
    ):

        if not queue_history:

            return 0.0

        waiting_times = []

        for vehicle in queue_history:

            entered_at = (
                vehicle["entered_at"]
            )

            waiting_time = (
                current_time -
                entered_at
            )

            waiting_times.append(
                max(0.0, waiting_time)
            )

        if not waiting_times:

            return 0.0

        return round(
            sum(waiting_times) /
            len(waiting_times),
            2
        )

    # ============================================================
    # DRAW DETECTIONS
    # ============================================================

    def draw_detections(
        self,
        frame,
        detections
    ):

        output = frame.copy()

        for detection in detections:

            x1, y1, x2, y2 = (
                detection["bbox"]
            )

            vehicle_type = (
                detection["class_name"]
            )

            confidence = (
                detection["confidence"]
            )

            label = (
                f"{vehicle_type} "
                f"{confidence:.2f}"
            )

            cv2.rectangle(
                output,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            cv2.putText(
                output,
                label,
                (
                    x1,
                    max(y1 - 10, 20)
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        return output