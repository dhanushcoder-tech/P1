class EmergencyGreenWave:

    def __init__(self):

        self.wave_history = []

    # ============================================================
    # ACTIVATE GREEN WAVE
    # ============================================================

    def activate_green_wave(
        self,
        city,
        route,
        current_junction,
        look_ahead=3,
        direction="NORTH"
    ):

        if current_junction not in route:

            raise ValueError(
                f"{current_junction} is not in the route."
            )

        current_index = route.index(
            current_junction
        )

        upcoming_junctions = route[
            current_index + 1:
            current_index + 1 + look_ahead
        ]

        activated_junctions = []

        for junction_id in upcoming_junctions:

            junction = city.junctions.get(
                junction_id
            )

            if junction is None:
                continue

            directions = [
                "NORTH",
                "SOUTH",
                "EAST",
                "WEST"
            ]

            # Set all signals RED
            for signal_direction in directions:

                junction.set_signal(
                    signal_direction,
                    "RED"
                )

            # Emergency GREEN signal
            junction.set_signal(
                direction,
                "GREEN"
            )

            activated_junctions.append({

                "junction_id":
                    junction_id,

                "direction":
                    direction,

                "signals":
                    junction.get_status()["signals"],

                "status":
                    "GREEN_WAVE_ACTIVE"
            })

        result = {

            "current_junction":
                current_junction,

            "look_ahead":
                look_ahead,

            "activated_count":
                len(activated_junctions),

            "junctions":
                activated_junctions,

            "status":
                "EMERGENCY_GREEN_WAVE_ACTIVE"
        }

        self.wave_history.append(
            result
        )

        return result

    # ============================================================
    # RELEASE GREEN WAVE
    # ============================================================

    def release_green_wave(
        self,
        city,
        junction_ids
    ):

        released = []

        for junction_id in junction_ids:

            junction = city.junctions.get(
                junction_id
            )

            if junction is None:
                continue

            directions = [
                "NORTH",
                "SOUTH",
                "EAST",
                "WEST"
            ]

            for direction in directions:

                junction.set_signal(
                    direction,
                    "RED"
                )

            released.append(
                junction_id
            )

        return {

            "released_junctions":
                released,

            "status":
                "GREEN_WAVE_RELEASED"
        }

    # ============================================================
    # GET HISTORY
    # ============================================================

    def get_history(self):

        return self.wave_history.copy()