class EmergencyPriority:

    def __init__(self, emergency_controller):

        self.emergency_controller = emergency_controller

    # ============================================================
    # CHECK IF EMERGENCY PRIORITY IS REQUIRED
    # ============================================================

    def is_required(self, junction_id):

        if not self.emergency_controller.emergency_active:
            return False

        return self.emergency_controller.has_priority(
            junction_id
        )

    # ============================================================
    # GET TARGET JUNCTION
    # ============================================================

    def get_target_junction(self):

        if not self.emergency_controller.emergency_active:
            return None

        return (
            self.emergency_controller.get_next_junction()
        )

    # ============================================================
    # GET EMERGENCY SIGNAL DECISION
    # ============================================================

    def get_signal_decision(self, junction_id):

        emergency_active = (
            self.emergency_controller.emergency_active
        )

        if not emergency_active:

            return {
                "mode": "NORMAL",
                "junction_id": junction_id,
                "emergency_active": False,
                "priority": False
            }

        target_junction = (
            self.emergency_controller.get_next_junction()
        )

        if junction_id != target_junction:

            return {
                "mode": "NORMAL",
                "junction_id": junction_id,
                "emergency_active": True,
                "priority": False,
                "target_junction": target_junction
            }

        return {
            "mode": "EMERGENCY",
            "junction_id": junction_id,
            "emergency_active": True,
            "priority": True,
            "vehicle_id":
                self.emergency_controller.active_vehicle_id,
            "current_junction":
                self.emergency_controller.current_junction,
            "target_junction":
                target_junction,
            "destination":
                self.emergency_controller.destination_junction,

            # Emergency signal instruction
            "signal_action": "GREEN_PRIORITY",

            # Conflicting traffic must stop
            "conflicting_traffic": "RED"
        }

    # ============================================================
    # GET STATUS
    # ============================================================

    def get_status(self):

        return {

            "emergency_active":
                self.emergency_controller.emergency_active,

            "vehicle_id":
                self.emergency_controller.active_vehicle_id,

            "current_junction":
                self.emergency_controller.current_junction,

            "target_junction":
                self.get_target_junction(),

            "priority_required":
                self.is_required(
                    self.get_target_junction()
                )
                if self.get_target_junction()
                else False
        }