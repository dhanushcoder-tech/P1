class MissionManager:

    def __init__(self):

        self.active_missions = {}

        self.completed_missions = {}

        self.mission_counter = 0

    # ============================================================
    # START MISSION
    # ============================================================

    def start_mission(
        self,
        vehicle,
        route
    ):

        self.mission_counter += 1

        mission_id = (
            f"MISSION-{self.mission_counter:04d}"
        )

        mission = {

            "mission_id":
                mission_id,

            "vehicle_id":
                vehicle.vehicle_id,

            "vehicle_type":
                vehicle.vehicle_type,

            "source":
                vehicle.source_junction,

            "destination":
                vehicle.destination_junction,

            "route":
                route.copy(),

            "status":
                "ACTIVE"
        }

        self.active_missions[
            mission_id
        ] = mission

        return mission

    # ============================================================
    # COMPLETE MISSION
    # ============================================================

    def complete_mission(
        self,
        mission_id,
        final_junction
    ):

        mission = self.active_missions.get(
            mission_id
        )

        if mission is None:

            raise ValueError(
                f"Mission {mission_id} not found."
            )

        mission["final_junction"] = (
            final_junction
        )

        mission["status"] = (
            "COMPLETED"
        )

        self.completed_missions[
            mission_id
        ] = mission

        del self.active_missions[
            mission_id
        ]

        return mission

    # ============================================================
    # CANCEL MISSION
    # ============================================================

    def cancel_mission(
        self,
        mission_id,
        reason
    ):

        mission = self.active_missions.get(
            mission_id
        )

        if mission is None:

            raise ValueError(
                f"Mission {mission_id} not found."
            )

        mission["status"] = "CANCELLED"

        mission["reason"] = reason

        self.completed_missions[
            mission_id
        ] = mission

        del self.active_missions[
            mission_id
        ]

        return mission

    # ============================================================
    # GET ACTIVE MISSIONS
    # ============================================================

    def get_active_missions(self):

        return list(
            self.active_missions.values()
        )

    # ============================================================
    # GET COMPLETED MISSIONS
    # ============================================================

    def get_completed_missions(self):

        return list(
            self.completed_missions.values()
        )

    # ============================================================
    # SYSTEM STATUS
    # ============================================================

    def get_status(self):

        return {

            "active_missions":
                len(self.active_missions),

            "completed_missions":
                len(self.completed_missions),

            "total_missions":
                self.mission_counter
        }