from app.emergency.emergency_vehicle import (
    EmergencyVehicle
)


class AmbulanceDetector:

    def __init__(self):

        self.detected_ambulances = {}

        self.next_id = 1

    # ============================================
    # DETECT AMBULANCE
    # ============================================

    def detect_ambulance(
        self,
        junction_id,
        direction
    ):

        ambulance_id = (
            f"AMB-{self.next_id:04d}"
        )

        self.next_id += 1

        ambulance = EmergencyVehicle(
            vehicle_id=ambulance_id,
            vehicle_type="ambulance",
            source_junction=junction_id,
            direction=direction
        )

        ambulance.detect()

        ambulance.start_tracking()

        self.detected_ambulances[
            ambulance_id
        ] = ambulance

        print("\n🚨 EMERGENCY EVENT")

        print(
            f"   Ambulance: "
            f"{ambulance_id}"
        )

        print(
            f"   Junction: "
            f"{junction_id}"
        )

        print(
            f"   Direction: "
            f"{direction}"
        )

        return ambulance

    # ============================================
    # GET AMBULANCE
    # ============================================

    def get_ambulance(
        self,
        ambulance_id
    ):

        return self.detected_ambulances.get(
            ambulance_id
        )

    # ============================================
    # UPDATE TRACKING
    # ============================================

    def update_tracking(
        self,
        ambulance_id,
        junction_id,
        distance=None
    ):

        ambulance = self.get_ambulance(
            ambulance_id
        )

        if ambulance is None:

            print(
                f"❌ Ambulance not found: "
                f"{ambulance_id}"
            )

            return False

        ambulance.update_location(
            junction_id=junction_id,
            distance=distance
        )

        print(
            f"📍 {ambulance_id} "
            f"→ Junction {junction_id}"
        )

        if distance is not None:

            print(
                f"   Distance: "
                f"{distance}m"
            )

        return True

    # ============================================
    # MARK AMBULANCE AS PASSED
    # ============================================

    def mark_passed(
        self,
        ambulance_id
    ):

        ambulance = self.get_ambulance(
            ambulance_id
        )

        if ambulance is None:

            print(
                f"❌ Ambulance not found: "
                f"{ambulance_id}"
            )

            return False

        ambulance.mark_passed()

        return True

    # ============================================
    # GET ACTIVE AMBULANCES
    # ============================================

    def get_active_ambulances(self):

        return [

            ambulance

            for ambulance
            in self.detected_ambulances.values()

            if ambulance.emergency_active
        ]

    # ============================================
    # GET STATUS
    # ============================================

    def get_status(self):

        status = {}

        for ambulance_id, ambulance in (
            self.detected_ambulances.items()
        ):

            status[
                ambulance_id
            ] = ambulance.get_status()

        return status