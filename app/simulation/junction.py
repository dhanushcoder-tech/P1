class Junction:

    def __init__(self, junction_id):

        self.junction_id = junction_id

        self.signal_state = {
            "NORTH": "RED",
            "SOUTH": "RED",
            "EAST": "RED",
            "WEST": "RED"
        }

        # Current coordinated green direction
        self.active_direction = None

        # Current green duration
        self.green_duration = 0

    # ==================================================
    # SET SIGNAL
    # ==================================================

    def set_signal(self, direction, state):

        if direction not in self.signal_state:

            raise ValueError(
                f"Invalid direction: {direction}"
            )

        if state not in [
            "RED",
            "YELLOW",
            "GREEN"
        ]:

            raise ValueError(
                f"Invalid signal state: {state}"
            )

        self.signal_state[direction] = state

        if state == "GREEN":

            self.active_direction = direction

    # ==================================================
    # SET ALL RED
    # ==================================================

    def set_all_red(self):

        for direction in self.signal_state:

            self.signal_state[direction] = "RED"

        self.active_direction = None

    # ==================================================
    # APPLY GREEN
    # ==================================================

    def apply_green(
        self,
        direction,
        duration
    ):

        if direction not in self.signal_state:

            raise ValueError(
                f"Invalid direction: {direction}"
            )

        # Safety:
        # conflicting directions are red.

        self.set_all_red()

        self.signal_state[direction] = "GREEN"

        self.active_direction = direction

        self.green_duration = duration

    # ==================================================
    # APPLY YELLOW
    # ==================================================

    def apply_yellow(self, direction):

        if direction not in self.signal_state:

            raise ValueError(
                f"Invalid direction: {direction}"
            )

        self.signal_state[direction] = "YELLOW"

    # ==================================================
    # GET ACTIVE DIRECTION
    # ==================================================

    def get_active_direction(self):

        return self.active_direction

    # ==================================================
    # GET STATUS
    # ==================================================

    def get_status(self):

        return {

            "junction_id":
                self.junction_id,

            "signals":
                self.signal_state.copy(),

            "active_direction":
                self.active_direction,

            "green_duration":
                self.green_duration
        }