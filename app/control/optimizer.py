from app.control.priority import PriorityManager


class TrafficOptimizer:

    def __init__(
        self,
        min_green=5,
        max_green=30
    ):

        self.min_green = min_green
        self.max_green = max_green

        self.priority_manager = (
            PriorityManager()
        )

    def calculate_lane_score(self, lane):

        vehicle_score = (
            lane.vehicle_count * 1.5
        )

        queue_score = (
            lane.queue_length * 2.0
        )

        waiting_score = (
            lane.get_average_waiting_time()
            * 0.8
        )

        density_score = (
            lane.traffic_density
            * 100
            * 1.5
        )

        total_score = (
            vehicle_score
            + queue_score
            + waiting_score
            + density_score
        )

        return round(
            total_score,
            2
        )

    def calculate_group_score(
        self,
        lanes
    ):

        return round(
            sum(
                self.calculate_lane_score(
                    lane
                )
                for lane in lanes
            ),
            2
        )

    def calculate_green_time(
        self,
        group_score,
        total_score
    ):

        if total_score <= 0:

            return self.min_green

        ratio = (
            group_score /
            total_score
        )

        green_range = (
            self.max_green -
            self.min_green
        )

        green_time = (
            self.min_green
            + ratio * green_range
        )

        return round(
            max(
                self.min_green,
                min(
                    self.max_green,
                    green_time
                )
            ),
            1
        )

    def optimize(
        self,
        junction,
        current_green_group=None
    ):

        north = junction.get_lane(
            "NORTH"
        )

        south = junction.get_lane(
            "SOUTH"
        )

        east = junction.get_lane(
            "EAST"
        )

        west = junction.get_lane(
            "WEST"
        )

        ns_score = (
            self.calculate_group_score(
                [north, south]
            )
        )

        ew_score = (
            self.calculate_group_score(
                [east, west]
            )
        )

        # Update fairness information
        if current_green_group:

            self.priority_manager.update_waiting_cycles(
                current_green_group
            )

        # Apply fairness
        scores = (
            self.priority_manager.apply_fairness(
                ns_score,
                ew_score
            )
        )

        final_ns_score = scores["NS"]
        final_ew_score = scores["EW"]

        total_score = (
            final_ns_score
            + final_ew_score
        )

        # Check starvation
        force_ns = (
            self.priority_manager
            .should_force_service("NS")
        )

        force_ew = (
            self.priority_manager
            .should_force_service("EW")
        )

        if force_ns:

            final_ns_score = (
                final_ew_score + 1
            )

        if force_ew:

            final_ew_score = (
                final_ns_score + 1
            )

        total_score = (
            final_ns_score
            + final_ew_score
        )

        ns_green = (
            self.calculate_green_time(
                final_ns_score,
                total_score
            )
        )

        ew_green = (
            self.calculate_green_time(
                final_ew_score,
                total_score
            )
        )

        return {

            "NS": {

                "score": round(
                    final_ns_score,
                    2
                ),

                "green_time": ns_green,

                "fairness": scores[
                    "NS_fairness"
                ],

                "waiting_cycles":
                    self.priority_manager
                    .waiting_cycles["NS"]

            },

            "EW": {

                "score": round(
                    final_ew_score,
                    2
                ),

                "green_time": ew_green,

                "fairness": scores[
                    "EW_fairness"
                ],

                "waiting_cycles":
                    self.priority_manager
                    .waiting_cycles["EW"]

            }
        }