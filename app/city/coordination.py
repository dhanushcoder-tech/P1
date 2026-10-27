class CoordinationManager:

    def __init__(self, city):

        self.city = city

        self.predictions = []
        self.green_wave_requests = []
        self.signal_decisions = []

        self.junction_locks = {}

        # Performance analytics
        self.performance_records = []

        # Junction health
        self.health_scores = {}

    # ============================================================
    # TRAFFIC PREDICTION
    # ============================================================

    def predict_incoming_traffic(
        self,
        source,
        destination,
        vehicle_count,
        travel_time
    ):

        prediction = {
            "source": source,
            "destination": destination,
            "vehicle_count": vehicle_count,
            "travel_time": travel_time,
            "eta": travel_time
        }

        self.predictions.append(prediction)

        return prediction

    # ============================================================
    # PRIORITY
    # ============================================================

    def calculate_priority(
        self,
        vehicle_count,
        travel_time
    ):

        if vehicle_count >= 30:

            priority = "HIGH"
            priority_score = 3

        elif vehicle_count >= 15:

            priority = "MEDIUM"
            priority_score = 2

        else:

            priority = "LOW"
            priority_score = 1

        if travel_time <= 3:

            priority_score += 1

        if priority_score >= 4:

            priority = "CRITICAL"

        elif priority_score >= 3:

            priority = "HIGH"

        elif priority_score >= 2:

            priority = "MEDIUM"

        else:

            priority = "LOW"

        return {
            "priority": priority,
            "priority_score": priority_score
        }

    # ============================================================
    # CREATE GREEN WAVE REQUEST
    # ============================================================

    def create_green_wave_request(
        self,
        prediction
    ):

        priority_data = self.calculate_priority(
            prediction["vehicle_count"],
            prediction["travel_time"]
        )

        request = {

            "source":
                prediction["source"],

            "destination":
                prediction["destination"],

            "vehicle_count":
                prediction["vehicle_count"],

            "eta":
                prediction["eta"],

            "priority":
                priority_data["priority"],

            "priority_score":
                priority_data["priority_score"],

            "status":
                "PENDING",

            "wait_count":
                0
        }

        self.green_wave_requests.append(
            request
        )

        return request

    # ============================================================
    # GET INCOMING DIRECTION
    # ============================================================

    def get_incoming_direction(
        self,
        source,
        destination
    ):

        direction_map = {

            ("J1", "J2"): "WEST",
            ("J2", "J3"): "WEST",

            ("J3", "J2"): "EAST",
            ("J2", "J1"): "EAST",

            ("J4", "J5"): "WEST",
            ("J5", "J6"): "WEST",

            ("J6", "J5"): "EAST",
            ("J5", "J4"): "EAST",

            ("J7", "J8"): "WEST",
            ("J8", "J9"): "WEST",

            ("J9", "J8"): "EAST",
            ("J8", "J7"): "EAST",

            ("J1", "J4"): "NORTH",
            ("J4", "J7"): "NORTH",

            ("J7", "J4"): "SOUTH",
            ("J4", "J1"): "SOUTH",

            ("J2", "J5"): "NORTH",
            ("J5", "J8"): "NORTH",

            ("J8", "J5"): "SOUTH",
            ("J5", "J2"): "SOUTH",

            ("J3", "J6"): "NORTH",
            ("J6", "J9"): "NORTH",

            ("J9", "J6"): "SOUTH",
            ("J6", "J3"): "SOUTH"
        }

        return direction_map.get(
            (source, destination),
            "NORTH"
        )

    # ============================================================
    # CONFLICT DETECTION
    # ============================================================

    def check_conflict(
        self,
        request
    ):

        junction_id = request["destination"]

        direction = self.get_incoming_direction(
            request["source"],
            request["destination"]
        )

        current_lock = self.junction_locks.get(
            junction_id
        )

        if current_lock is None:

            return {
                "conflict": False,
                "reason": "Junction available"
            }

        if current_lock["direction"] == direction:

            return {
                "conflict": False,
                "reason": "Same direction"
            }

        return {

            "conflict":
                True,

            "reason":
                f"{current_lock['direction']} "
                f"already GREEN",

            "current_direction":
                current_lock["direction"]
        }

    # ============================================================
    # PROCESS GREEN WAVE REQUEST
    # ============================================================

    def process_green_wave_request(
        self,
        request
    ):

        if request["status"] not in [
            "PENDING",
            "WAITING"
        ]:

            return False

        if request["vehicle_count"] <= 0:

            request["status"] = "REJECTED"

            return False

        conflict = self.check_conflict(
            request
        )

        if conflict["conflict"]:

            request["wait_count"] += 1

            request["status"] = "WAITING"

            return False

        request["status"] = "ACCEPTED"

        return True

    # ============================================================
    # SIGNAL RESPONSE
    # ============================================================

    def respond_to_green_wave_request(
        self,
        request
    ):

        if request["status"] != "ACCEPTED":

            return None

        decision = {

            "junction":
                request["destination"],

            "source":
                request["source"],

            "vehicle_count":
                request["vehicle_count"],

            "priority":
                request["priority"],

            "action":
                "PREPARE_GREEN",

            "status":
                "READY"
        }

        self.signal_decisions.append(
            decision
        )

        request["status"] = "SIGNAL_PREPARED"

        return decision

    # ============================================================
    # GREEN WAVE TIMING
    # ============================================================

    def calculate_green_wave_timing(
        self,
        request
    ):

        if request["status"] != "SIGNAL_PREPARED":

            return None

        base_green = 10

        vehicle_time = (
            request["vehicle_count"] * 2
        )

        priority_bonus = {

            "LOW": 0,
            "MEDIUM": 5,
            "HIGH": 10,
            "CRITICAL": 15
        }

        bonus = priority_bonus.get(
            request["priority"],
            0
        )

        green_time = (
            base_green
            + vehicle_time
            + bonus
        )

        green_time = max(
            10,
            min(
                green_time,
                60
            )
        )

        timing = {

            "junction":
                request["destination"],

            "source":
                request["source"],

            "vehicle_count":
                request["vehicle_count"],

            "eta":
                request["eta"],

            "priority":
                request["priority"],

            "recommended_green":
                green_time,

            "status":
                "TIMING_READY"
        }

        request["status"] = "TIMING_READY"

        return timing

    # ============================================================
    # APPLY SIGNAL COORDINATION
    # ============================================================

    def apply_signal_coordination(
        self,
        request,
        timing
    ):

        junction_id = request["destination"]

        junction = self.city.junctions.get(
            junction_id
        )

        if junction is None:

            return False

        direction = self.get_incoming_direction(
            request["source"],
            request["destination"]
        )

        self.junction_locks[junction_id] = {

            "direction":
                direction,

            "source":
                request["source"],

            "green_duration":
                timing["recommended_green"]
        }

        junction.apply_green(
            direction,
            timing["recommended_green"]
        )

        request["status"] = "GREEN_ACTIVE"

        self.signal_decisions.append({

            "junction":
                junction_id,

            "source":
                request["source"],

            "direction":
                direction,

            "green_duration":
                timing["recommended_green"],

            "status":
                "GREEN_ACTIVE"
        })

        return True

    # ============================================================
    # RELEASE JUNCTION
    # ============================================================

    def release_junction(
        self,
        junction_id
    ):

        self.junction_locks.pop(
            junction_id,
            None
        )

        return True

    # ============================================================
    # PERFORMANCE RECORD
    # ============================================================

    def record_performance(
        self,
        junction_id,
        vehicle_count,
        queue_length,
        waiting_time,
        throughput,
        green_time,
        total_cycle_time
    ):

        if total_cycle_time <= 0:

            efficiency = 0

        else:

            efficiency = (
                green_time /
                total_cycle_time
            ) * 100

        record = {

            "junction_id":
                junction_id,

            "vehicle_count":
                vehicle_count,

            "queue_length":
                queue_length,

            "waiting_time":
                waiting_time,

            "throughput":
                throughput,

            "green_time":
                green_time,

            "total_cycle_time":
                total_cycle_time,

            "signal_efficiency":
                round(
                    efficiency,
                    2
                )
        }

        self.performance_records.append(
            record
        )

        return record

    # ============================================================
    # PERFORMANCE SUMMARY
    # ============================================================

    def get_performance_summary(self):

        if not self.performance_records:

            return {

                "average_waiting_time":
                    0,

                "average_queue_length":
                    0,

                "total_throughput":
                    0,

                "average_signal_efficiency":
                    0,

                "junctions_measured":
                    0
            }

        total = len(
            self.performance_records
        )

        average_waiting = (

            sum(
                record["waiting_time"]
                for record
                in self.performance_records
            )

            / total
        )

        average_queue = (

            sum(
                record["queue_length"]
                for record
                in self.performance_records
            )

            / total
        )

        throughput = sum(

            record["throughput"]

            for record
            in self.performance_records
        )

        efficiency = (

            sum(
                record["signal_efficiency"]
                for record
                in self.performance_records
            )

            / total
        )

        return {

            "average_waiting_time":
                round(
                    average_waiting,
                    2
                ),

            "average_queue_length":
                round(
                    average_queue,
                    2
                ),

            "total_throughput":
                throughput,

            "average_signal_efficiency":
                round(
                    efficiency,
                    2
                ),

            "junctions_measured":
                total
        }

    # ============================================================
    # S9.14 - JUNCTION HEALTH SCORE
    # ============================================================

    def calculate_junction_health(
        self,
        record
    ):

        waiting_time = record[
            "waiting_time"
        ]

        queue_length = record[
            "queue_length"
        ]

        efficiency = record[
            "signal_efficiency"
        ]

        throughput = record[
            "throughput"
        ]

        vehicle_count = record[
            "vehicle_count"
        ]

        # --------------------------------------------------------
        # WAITING SCORE
        # --------------------------------------------------------

        if waiting_time <= 30:

            waiting_score = 100

        elif waiting_time <= 60:

            waiting_score = 75

        elif waiting_time <= 90:

            waiting_score = 50

        elif waiting_time <= 120:

            waiting_score = 25

        else:

            waiting_score = 0

        # --------------------------------------------------------
        # QUEUE SCORE
        # --------------------------------------------------------

        if queue_length <= 10:

            queue_score = 100

        elif queue_length <= 20:

            queue_score = 75

        elif queue_length <= 30:

            queue_score = 50

        elif queue_length <= 40:

            queue_score = 25

        else:

            queue_score = 0

        # --------------------------------------------------------
        # SIGNAL EFFICIENCY SCORE
        # --------------------------------------------------------

        if efficiency >= 60:

            efficiency_score = 100

        elif efficiency >= 45:

            efficiency_score = 80

        elif efficiency >= 30:

            efficiency_score = 60

        elif efficiency >= 20:

            efficiency_score = 40

        else:

            efficiency_score = 20

        # --------------------------------------------------------
        # THROUGHPUT SCORE
        # --------------------------------------------------------

        if vehicle_count <= 0:

            throughput_score = 0

        else:

            throughput_ratio = (
                throughput /
                vehicle_count
            ) * 100

            throughput_score = min(
                throughput_ratio,
                100
            )

        # --------------------------------------------------------
        # FINAL WEIGHTED SCORE
        # --------------------------------------------------------

        health_score = (

            waiting_score * 0.30

            + queue_score * 0.25

            + efficiency_score * 0.20

            + throughput_score * 0.25
        )

        health_score = round(
            health_score,
            2
        )

        # --------------------------------------------------------
        # STATUS
        # --------------------------------------------------------

        if health_score >= 75:

            status = "EXCELLENT"

        elif health_score >= 50:

            status = "MODERATE"

        else:

            status = "UNDERPERFORMING"

        result = {

            "junction_id":
                record["junction_id"],

            "health_score":
                health_score,

            "status":
                status,

            "waiting_score":
                waiting_score,

            "queue_score":
                queue_score,

            "efficiency_score":
                efficiency_score,

            "throughput_score":
                round(
                    throughput_score,
                    2
                )
        }

        self.health_scores[
            record["junction_id"]
        ] = result

        return result

    # ============================================================
    # CALCULATE ALL HEALTH SCORES
    # ============================================================

    def calculate_all_health_scores(self):

        results = []

        for record in self.performance_records:

            result = (
                self.calculate_junction_health(
                    record
                )
            )

            results.append(
                result
            )

        return results

    # ============================================================
    # HEALTH SUMMARY
    # ============================================================

    def get_health_summary(self):

        if not self.health_scores:

            self.calculate_all_health_scores()

        excellent = 0
        moderate = 0
        underperforming = 0

        for result in self.health_scores.values():

            if result["status"] == "EXCELLENT":

                excellent += 1

            elif result["status"] == "MODERATE":

                moderate += 1

            else:

                underperforming += 1

        return {

            "excellent":
                excellent,

            "moderate":
                moderate,

            "underperforming":
                underperforming,

            "total":
                len(
                    self.health_scores
                )
        }

    # ============================================================
    # GREEN-WAVE SUCCESS RATE
    # ============================================================

    def get_green_wave_success_rate(self):

        total = len(
            self.green_wave_requests
        )

        if total == 0:

            return 0

        successful = sum(

            1

            for request
            in self.green_wave_requests

            if request["status"]
            == "GREEN_ACTIVE"
        )

        return round(
            (
                successful /
                total
            ) * 100,
            2
        )

    # ============================================================
    # STATUS
    # ============================================================

    def get_status(self):

        return {

            "total_predictions":
                len(
                    self.predictions
                ),

            "total_green_wave_requests":
                len(
                    self.green_wave_requests
                ),

            "total_signal_decisions":
                len(
                    self.signal_decisions
                ),

            "performance_records":
                len(
                    self.performance_records
                ),

            "health_scores":
                len(
                    self.health_scores
                ),

            "active_junction_locks":
                len(
                    self.junction_locks
                )
        }