class SignalController:

    def __init__(
        self,
        junction,
        optimizer,
        green_duration=10,
        yellow_duration=3,
        all_red_duration=1
    ):

        self.junction = junction

        self.optimizer = optimizer

        self.green_duration = green_duration

        self.yellow_duration = yellow_duration

        self.all_red_duration = all_red_duration

        # -------------------------------------------
        # SIGNAL PHASE
        # -------------------------------------------

        self.phases = [
            "NS",
            "EW"
        ]

        self.current_phase_index = 0

        self.current_phase = "NS"

        self.state = "GREEN"

        self.timer = green_duration

        # -------------------------------------------
        # GREEN WAVE
        # -------------------------------------------

        self.green_wave_request = None

        self.green_wave_active = False

        # -------------------------------------------
        # INITIAL SIGNAL
        # -------------------------------------------

        self.update_signal_state()

    # ===============================================
    # GREEN-WAVE REQUEST
    # ===============================================

    def request_green_wave(
        self,
        source,
        vehicle_count,
        eta
    ):

        self.green_wave_request = {

            "source": source,

            "vehicle_count": vehicle_count,

            "eta": eta
        }

        print(
            f"📡 {self.junction.junction_id}: "
            f"Green-wave request received | "
            f"Source: {source} | "
            f"Vehicles: {vehicle_count} | "
            f"ETA: {eta}s"
        )

        # -------------------------------------------
        # PREPARE SIGNAL
        # -------------------------------------------

        # If traffic is arriving soon,
        # extend the current green phase.

        if eta <= 2:

            self.green_wave_active = True

            if self.state == "GREEN":

                extension = min(
                    5,
                    vehicle_count
                )

                self.timer += extension

                print(
                    f"🟢 {self.junction.junction_id}: "
                    f"GREEN WAVE ACTIVE | "
                    f"+{extension}s GREEN"
                )

    # ===============================================
    # UPDATE
    # ===============================================

    def update(self):

        # -------------------------------------------
        # COUNTDOWN
        # -------------------------------------------

        self.timer -= 1

        # -------------------------------------------
        # GREEN-WAVE PREPARATION
        # -------------------------------------------

        if self.green_wave_request:

            eta = (
                self.green_wave_request[
                    "eta"
                ]
            )

            # If wave is close and we're red,
            # prepare the next phase.

            if eta <= 2:

                if self.state == "RED":

                    print(
                        f"🟢 {self.junction.junction_id}: "
                        f"Preparing green for "
                        f"incoming wave"
                    )

        # -------------------------------------------
        # PHASE TRANSITION
        # -------------------------------------------

        if self.timer <= 0:

            self.transition()

        # -------------------------------------------
        # UPDATE SIGNAL
        # -------------------------------------------

        self.update_signal_state()

    # ===============================================
    # SIGNAL TRANSITION
    # ===============================================

    def transition(self):

        if self.state == "GREEN":

            self.state = "YELLOW"

            self.timer = (
                self.yellow_duration
            )

        elif self.state == "YELLOW":

            self.state = "RED"

            self.timer = (
                self.all_red_duration
            )

        elif self.state == "RED":

            # ---------------------------------------
            # NEXT PHASE
            # ---------------------------------------

            self.current_phase_index = (
                (self.current_phase_index + 1)
                % len(self.phases)
            )

            self.current_phase = (
                self.phases[
                    self.current_phase_index
                ]
            )

            self.state = "GREEN"

            # ---------------------------------------
            # GREEN-WAVE EXTENSION
            # ---------------------------------------

            green_time = (
                self.green_duration
            )

            if self.green_wave_active:

                green_time += 5

                print(
                    f"🌊 {self.junction.junction_id}: "
                    f"GREEN WAVE GREEN PHASE"
                )

                self.green_wave_active = False

                self.green_wave_request = None

            self.timer = green_time

    # ===============================================
    # UPDATE JUNCTION SIGNAL
    # ===============================================

    def update_signal_state(self):

        if self.state == "GREEN":

            if self.current_phase == "NS":

                self.junction.set_signal(
                    "NORTH",
                    "GREEN"
                )

                self.junction.set_signal(
                    "SOUTH",
                    "GREEN"
                )

                self.junction.set_signal(
                    "EAST",
                    "RED"
                )

                self.junction.set_signal(
                    "WEST",
                    "RED"
                )

            else:

                self.junction.set_signal(
                    "NORTH",
                    "RED"
                )

                self.junction.set_signal(
                    "SOUTH",
                    "RED"
                )

                self.junction.set_signal(
                    "EAST",
                    "GREEN"
                )

                self.junction.set_signal(
                    "WEST",
                    "GREEN"
                )

        elif self.state == "YELLOW":

            if self.current_phase == "NS":

                self.junction.set_signal(
                    "NORTH",
                    "YELLOW"
                )

                self.junction.set_signal(
                    "SOUTH",
                    "YELLOW"
                )

                self.junction.set_signal(
                    "EAST",
                    "RED"
                )

                self.junction.set_signal(
                    "WEST",
                    "RED"
                )

            else:

                self.junction.set_signal(
                    "NORTH",
                    "RED"
                )

                self.junction.set_signal(
                    "SOUTH",
                    "RED"
                )

                self.junction.set_signal(
                    "EAST",
                    "YELLOW"
                )

                self.junction.set_signal(
                    "WEST",
                    "YELLOW"
                )

        else:

            self.junction.set_signal(
                "NORTH",
                "RED"
            )

            self.junction.set_signal(
                "SOUTH",
                "RED"
            )

            self.junction.set_signal(
                "EAST",
                "RED"
            )

            self.junction.set_signal(
                "WEST",
                "RED"
            )

    # ===============================================
    # CURRENT PHASE
    # ===============================================

    def get_current_phase(self):

        return self.current_phase

    # ===============================================
    # CURRENT STATE
    # ===============================================

    def get_state(self):

        return self.state

    # ===============================================
    # TIMER
    # ===============================================

    def get_timer(self):

        return self.timer

    # ===============================================
    # GREEN-WAVE STATUS
    # ===============================================

    def get_green_wave_status(self):

        return {

            "active":
                self.green_wave_active,

            "request":
                self.green_wave_request
        }