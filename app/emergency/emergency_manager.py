from app.emergency.emergency_vehicle import EmergencyVehicle


class EmergencyManager:

    def __init__(self):

        self.active_vehicles = {}

        self.completed_vehicles = {}

        self.detection_history = []

    # ============================================================
    # REGISTER EMERGENCY VEHICLE
    # ============================================================

    def register_vehicle(
        self,
        vehicle_type="ambulance",
        source_junction=None,
        destination_junction=None
    ):

        vehicle = EmergencyVehicle(

            vehicle_type=vehicle_type,

            source_junction=source_junction,

            destination_junction=destination_junction
        )

        self.active_vehicles[
            vehicle.vehicle_id
        ] = vehicle

        self.detection_history.append({

            "vehicle_id":
                vehicle.vehicle_id,

            "vehicle_type":
                vehicle.vehicle_type,

            "source_junction":
                source_junction,

            "destination_junction":
                destination_junction,

            "event":
                "REGISTERED"
        })

        return vehicle

    # ============================================================
    # DETECT VEHICLE
    # ============================================================

    def detect_vehicle(
        self,
        vehicle_id,
        confidence=1.0
    ):

        vehicle = self.active_vehicles.get(
            vehicle_id
        )

        if vehicle is None:

            raise ValueError(
                f"Emergency vehicle "
                f"{vehicle_id} not found."
            )

        status = vehicle.detect(
            confidence
        )

        self.detection_history.append({

            "vehicle_id":
                vehicle_id,

            "vehicle_type":
                vehicle.vehicle_type,

            "source_junction":
                vehicle.source_junction,

            "destination_junction":
                vehicle.destination_junction,

            "confidence":
                confidence,

            "event":
                "DETECTED"
        })

        return status

    # ============================================================
    # UPDATE VEHICLE LOCATION
    # ============================================================

    def update_vehicle_location(
        self,
        vehicle_id,
        junction_id
    ):

        vehicle = self.active_vehicles.get(
            vehicle_id
        )

        if vehicle is None:

            raise ValueError(
                f"Emergency vehicle "
                f"{vehicle_id} not found."
            )

        status = vehicle.update_location(
            junction_id
        )

        self.detection_history.append({

            "vehicle_id":
                vehicle_id,

            "junction_id":
                junction_id,

            "event":
                "LOCATION_UPDATED"
        })

        return status

    # ============================================================
    # GET VEHICLE
    # ============================================================

    def get_vehicle(
        self,
        vehicle_id
    ):

        vehicle = self.active_vehicles.get(
            vehicle_id
        )

        if vehicle is None:
            return None

        return vehicle

    # ============================================================
    # GET ACTIVE VEHICLES
    # ============================================================

    def get_active_vehicles(self):

        return [

            vehicle.get_status()

            for vehicle
            in self.active_vehicles.values()
        ]

    # ============================================================
    # GET HIGH PRIORITY VEHICLES
    # ============================================================

    def get_high_priority_vehicles(self):

        return [

            vehicle.get_status()

            for vehicle
            in self.active_vehicles.values()

            if vehicle.is_high_priority()
        ]

    # ============================================================
    # COMPLETE JOURNEY
    # ============================================================

    def complete_vehicle(
        self,
        vehicle_id
    ):

        vehicle = self.active_vehicles.get(
            vehicle_id
        )

        if vehicle is None:

            raise ValueError(
                f"Emergency vehicle "
                f"{vehicle_id} not found."
            )

        vehicle.deactivate()

        self.completed_vehicles[
            vehicle_id
        ] = vehicle

        del self.active_vehicles[
            vehicle_id
        ]

        self.detection_history.append({

            "vehicle_id":
                vehicle_id,

            "event":
                "JOURNEY_COMPLETED"
        })

        return vehicle.get_status()

    # ============================================================
    # HISTORY
    # ============================================================

    def get_detection_history(self):

        return self.detection_history.copy()

    # ============================================================
    # SYSTEM STATUS
    # ============================================================

    def get_status(self):

        high_priority = len(
            self.get_high_priority_vehicles()
        )

        return {

            "active_vehicles":
                len(self.active_vehicles),

            "completed_vehicles":
                len(self.completed_vehicles),

            "high_priority_vehicles":
                high_priority,

            "total_events":
                len(self.detection_history)
        }