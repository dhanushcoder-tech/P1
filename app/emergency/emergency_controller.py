class EmergencyController:

    def __init__(self):

        self.emergency_active = False

        self.active_vehicle_id = None

        self.active_route = []

        self.current_junction = None

        self.destination_junction = None

        self.history = []

        # Tracking safety state
        self.tracking_lost = False

        self.tracking_timeout = False

    # ============================================================
    # ACTIVATE EMERGENCY
    # ============================================================

    def activate_emergency(
        self,
        vehicle_id,
        route,
        destination
    ):

        self.emergency_active = True

        self.active_vehicle_id = vehicle_id

        self.active_route = route.copy()

        self.destination_junction = destination

        self.tracking_lost = False

        self.tracking_timeout = False

        if self.active_route:

            self.current_junction = (
                self.active_route[0]
            )

        else:

            self.current_junction = None

        event = {
            "event": "EMERGENCY_ACTIVATED",
            "vehicle_id": vehicle_id,
            "route": route.copy(),
            "destination": destination
        }

        self.history.append(event)

        return event

    # ============================================================
    # GET NEXT JUNCTION
    # ============================================================

    def get_next_junction(self):

        if not self.emergency_active:
            return None

        if not self.active_route:
            return None

        if self.current_junction not in self.active_route:
            return None

        current_index = (
            self.active_route.index(
                self.current_junction
            )
        )

        next_index = current_index + 1

        if next_index >= len(self.active_route):
            return None

        return self.active_route[next_index]

    # ============================================================
    # CHECK PRIORITY
    # ============================================================

    def has_priority(
        self,
        junction_id
    ):

        if not self.emergency_active:
            return False

        if self.tracking_lost:
            return False

        if self.tracking_timeout:
            return False

        return (
            junction_id
            == self.get_next_junction()
        )

    # ============================================================
    # MOVE TO JUNCTION
    # ============================================================

    def move_to_junction(
        self,
        junction_id
    ):

        if not self.emergency_active:
            return False

        if self.tracking_lost:
            return False

        if self.tracking_timeout:
            return False

        if junction_id not in self.active_route:
            return False

        current_index = (
            self.active_route.index(
                self.current_junction
            )
        )

        target_index = (
            self.active_route.index(
                junction_id
            )
        )

        if target_index != current_index + 1:
            return False

        self.current_junction = junction_id

        event = {
            "event": "EMERGENCY_JUNCTION_CROSSED",
            "vehicle_id": self.active_vehicle_id,
            "junction_id": junction_id
        }

        self.history.append(event)

        return True

    # ============================================================
    # DESTINATION CHECK
    # ============================================================

    def has_reached_destination(self):

        if not self.emergency_active:
            return False

        return (
            self.current_junction
            == self.destination_junction
        )

    # ============================================================
    # AMBULANCE PASSED
    # ============================================================

    def mark_ambulance_passed(self):

        if not self.emergency_active:
            return False

        if not self.has_reached_destination():
            return False

        event = {
            "event": "AMBULANCE_PASSED",
            "vehicle_id": self.active_vehicle_id,
            "junction_id": self.current_junction
        }

        self.history.append(event)

        return True

    # ============================================================
    # TRACKING LOST
    # ============================================================

    def mark_tracking_lost(self):

        if not self.emergency_active:
            return False

        self.tracking_lost = True

        event = {
            "event": "AMBULANCE_TRACKING_LOST",
            "vehicle_id": self.active_vehicle_id,
            "junction_id": self.current_junction
        }

        self.history.append(event)

        return event

    # ============================================================
    # TIMEOUT FALLBACK
    # ============================================================

    def activate_tracking_timeout(self):

        if not self.emergency_active:
            return False

        self.tracking_timeout = True

        event = {
            "event": "EMERGENCY_TRACKING_TIMEOUT",
            "vehicle_id": self.active_vehicle_id,
            "junction_id": self.current_junction
        }

        self.history.append(event)

        return event

    # ============================================================
    # CHECK FALLBACK
    # ============================================================

    def fallback_required(self):

        return (
            self.tracking_lost
            or self.tracking_timeout
        )

    # ============================================================
    # DEACTIVATE EMERGENCY
    # ============================================================

    def deactivate_emergency(self):

        event = {
            "event": "EMERGENCY_DEACTIVATED",
            "vehicle_id": self.active_vehicle_id
        }

        self.history.append(event)

        self.emergency_active = False

        self.active_vehicle_id = None

        self.active_route = []

        self.current_junction = None

        self.destination_junction = None

        self.tracking_lost = False

        self.tracking_timeout = False

        return event

    # ============================================================
    # STATUS
    # ============================================================

    def get_status(self):

        return {
            "emergency_active":
                self.emergency_active,

            "vehicle_id":
                self.active_vehicle_id,

            "current_junction":
                self.current_junction,

            "destination":
                self.destination_junction,

            "next_junction":
                self.get_next_junction(),

            "route":
                self.active_route.copy(),

            "destination_reached":
                self.has_reached_destination(),

            "tracking_lost":
                self.tracking_lost,

            "tracking_timeout":
                self.tracking_timeout,

            "fallback_required":
                self.fallback_required()
        }

    # ============================================================
    # HISTORY
    # ============================================================

    def get_history(self):

        return self.history.copy()