class EmergencyOverride:

    def __init__(self, emergency_controller):

        self.emergency_controller = emergency_controller

        self.normal_control_paused = False

    # ============================================================
    # CHECK EMERGENCY
    # ============================================================

    def is_override_active(self):

        return (
            self.emergency_controller.emergency_active
        )

    # ============================================================
    # PAUSE NORMAL TRAFFIC CONTROL
    # ============================================================

    def pause_normal_control(self):

        if not self.is_override_active():

            self.normal_control_paused = False

            return False

        self.normal_control_paused = True

        return True

    # ============================================================
    # RESUME NORMAL TRAFFIC CONTROL
    # ============================================================

    def resume_normal_control(self):

        self.normal_control_paused = False

        return True

    # ============================================================
    # SHOULD THIS JUNCTION BE OVERRIDDEN?
    # ============================================================

    def should_override(self, junction_id):

        if not self.is_override_active():

            return False

        return (
            self.emergency_controller.has_priority(
                junction_id
            )
        )

    # ============================================================
    # SHOULD NORMAL AI RUN?
    # ============================================================

    def should_run_normal_control(
        self,
        junction_id
    ):

        # Emergency is active and normal control
        # has been paused.

        if self.normal_control_paused:

            return False

        # Target junction is under emergency control.

        if self.should_override(junction_id):

            return False

        return True

    # ============================================================
    # GET CONTROL DECISION
    # ============================================================

    def get_decision(self, junction_id):

        # Emergency override

        if self.should_override(junction_id):

            return {

                "override": True,

                "normal_control": False,

                "mode": "EMERGENCY",

                "junction_id":
                    junction_id,

                "vehicle_id":
                    self.emergency_controller.active_vehicle_id,

                "current_junction":
                    self.emergency_controller.current_junction,

                "target_junction":
                    self.emergency_controller.get_next_junction(),

                "destination":
                    self.emergency_controller.destination_junction
            }

        # Normal control

        return {

            "override": False,

            "normal_control":
                self.should_run_normal_control(
                    junction_id
                ),

            "mode": "NORMAL",

            "junction_id":
                junction_id
        }

    # ============================================================
    # STATUS
    # ============================================================

    def get_status(self):

        return {

            "emergency_active":
                self.emergency_controller.emergency_active,

            "normal_control_paused":
                self.normal_control_paused,

            "vehicle_id":
                self.emergency_controller.active_vehicle_id,

            "current_junction":
                self.emergency_controller.current_junction,

            "target_junction":
                self.emergency_controller.get_next_junction()
        }