class PriorityManager:

    def __init__(
        self,
        max_wait_threshold=60,
        fairness_weight=2.0
    ):

        self.max_wait_threshold = (
            max_wait_threshold
        )

        self.fairness_weight = (
            fairness_weight
        )

        self.waiting_cycles = {
            "NS": 0,
            "EW": 0
        }

    def update_waiting_cycles(
        self,
        current_green_group
    ):
        """
        Increase the waiting cycle count
        for the group that is NOT currently green.
        """

        groups = ["NS", "EW"]

        for group in groups:

            if group != current_green_group:

                self.waiting_cycles[group] += 1

            else:

                # Reset after receiving service
                self.waiting_cycles[group] = 0

    def get_fairness_score(self, group):

        return (
            self.waiting_cycles[group]
            * self.fairness_weight
        )

    def get_starvation_boost(self, group):

        cycles = self.waiting_cycles[group]

        if cycles >= 5:

            return 20.0

        if cycles >= 3:

            return 10.0

        return 0.0

    def apply_fairness(
        self,
        ns_score,
        ew_score
    ):

        ns_fairness = (
            self.get_fairness_score("NS")
            + self.get_starvation_boost("NS")
        )

        ew_fairness = (
            self.get_fairness_score("EW")
            + self.get_starvation_boost("EW")
        )

        final_ns_score = (
            ns_score + ns_fairness
        )

        final_ew_score = (
            ew_score + ew_fairness
        )

        return {

            "NS": round(
                final_ns_score,
                2
            ),

            "EW": round(
                final_ew_score,
                2
            ),

            "NS_fairness": round(
                ns_fairness,
                2
            ),

            "EW_fairness": round(
                ew_fairness,
                2
            )
        }

    def should_force_service(
        self,
        group
    ):
        """
        If a group has waited too long,
        force it to receive service.
        """

        return (
            self.waiting_cycles[group]
            >= 8
        )