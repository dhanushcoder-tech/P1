class RecommendationEngine:

    def __init__(self):
        self.recommendations = []
        self.commands = []
        self.execution_history = []
        self.performance_comparison = []
        self.city_summary = {}

    # ============================================================
    # RECOMMENDATION
    # ============================================================

    def generate_recommendation(self, record, health):

        junction_id = record["junction_id"]

        queue_length = record["queue_length"]
        waiting_time = record["waiting_time"]
        throughput = record["throughput"]
        vehicle_count = record["vehicle_count"]
        efficiency = record["signal_efficiency"]

        health_score = health["health_score"]
        health_status = health["status"]

        recommendations = []

        if queue_length > 40:
            recommendations.append(
                "Severe queue detected. Increase green time."
            )

        elif queue_length > 25:
            recommendations.append(
                "High queue detected. Allocate additional green time."
            )

        elif queue_length > 15:
            recommendations.append(
                "Moderate queue detected. Optimize traffic capacity."
            )

        if waiting_time > 120:
            recommendations.append(
                "Very high waiting time. Immediate optimization required."
            )

        elif waiting_time > 90:
            recommendations.append(
                "High waiting time. Extend green duration."
            )

        elif waiting_time > 60:
            recommendations.append(
                "Elevated waiting time. Consider adaptive signal timing."
            )

        if efficiency < 20:
            recommendations.append(
                "Very low signal efficiency."
            )

        elif efficiency < 30:
            recommendations.append(
                "Low signal efficiency."
            )

        elif efficiency < 45:
            recommendations.append(
                "Moderate signal efficiency."
            )

        if vehicle_count > 0:
            throughput_ratio = (
                throughput / vehicle_count
            ) * 100
        else:
            throughput_ratio = 0

        if throughput_ratio < 40:
            recommendations.append(
                "Low throughput. Increase vehicle discharge capacity."
            )

        elif throughput_ratio < 60:
            recommendations.append(
                "Traffic throughput is below optimal levels."
            )

        if health_status == "UNDERPERFORMING":
            recommendations.append(
                "Junction requires immediate optimization."
            )

        elif health_status == "MODERATE":
            recommendations.append(
                "Junction performance is moderate."
            )

        else:
            recommendations.append(
                "Junction is performing efficiently."
            )

        if queue_length > 25 and waiting_time > 60:

            action = (
                "Increase green time for the busiest approach "
                "and reduce unnecessary red time."
            )

            command_type = "EXTEND_GREEN"

        elif waiting_time > 90:

            action = (
                "Prioritize the direction with the highest waiting time."
            )

            command_type = "WAIT_PRIORITY"

        elif efficiency < 30:

            action = (
                "Rebalance the signal cycle."
            )

            command_type = "REBALANCE_SIGNAL"

        elif throughput_ratio < 50:

            action = (
                "Improve vehicle throughput."
            )

            command_type = "OPTIMIZE_THROUGHPUT"

        else:

            action = (
                "Maintain the current signal strategy."
            )

            command_type = "MONITOR"

        if health_score < 40:
            improvement_percent = 30

        elif health_score < 50:
            improvement_percent = 25

        elif health_score < 65:
            improvement_percent = 20

        elif health_score < 75:
            improvement_percent = 12

        else:
            improvement_percent = 5

        if health_score < 40:
            priority = "CRITICAL"

        elif health_score < 50:
            priority = "HIGH"

        elif health_score < 70:
            priority = "MEDIUM"

        else:
            priority = "LOW"

        health_factor = 100 - health_score
        queue_factor = min(queue_length, 100)

        waiting_factor = (
            min(waiting_time, 180) / 180
        ) * 100

        efficiency_factor = (
            100 - min(efficiency, 100)
        )

        priority_score = (
            health_factor * 0.40
            + queue_factor * 0.25
            + waiting_factor * 0.25
            + efficiency_factor * 0.10
        )

        recommendation = {

            "junction_id":
                junction_id,

            "health_score":
                health_score,

            "health_status":
                health_status,

            "priority":
                priority,

            "priority_score":
                round(priority_score, 2),

            "command_type":
                command_type,

            "problem": {

                "queue_length":
                    queue_length,

                "waiting_time":
                    waiting_time,

                "signal_efficiency":
                    efficiency,

                "throughput":
                    throughput,

                "vehicle_count":
                    vehicle_count
            },

            "recommendations":
                recommendations,

            "main_action":
                action,

            "expected_improvement":
                improvement_percent,

            "status":
                "ACTIVE"
        }

        self.recommendations.append(
            recommendation
        )

        return recommendation

    # ============================================================
    # GENERATE ALL
    # ============================================================

    def generate_all(
        self,
        performance_records,
        health_results
    ):

        self.recommendations = []

        health_map = {
            health["junction_id"]: health
            for health in health_results
        }

        results = []

        for record in performance_records:

            health = health_map.get(
                record["junction_id"]
            )

            if health is None:
                continue

            results.append(
                self.generate_recommendation(
                    record,
                    health
                )
            )

        return results

    # ============================================================
    # RANK
    # ============================================================

    def rank_recommendations(self):

        ranked = sorted(
            self.recommendations,
            key=lambda item:
                item["priority_score"],
            reverse=True
        )

        for index, recommendation in enumerate(
            ranked,
            start=1
        ):

            recommendation["rank"] = index

        self.recommendations = ranked

        return ranked

    # ============================================================
    # CREATE COMMAND
    # ============================================================

    def create_command(
        self,
        recommendation
    ):

        command = {

            "command_id":
                f"CMD-{recommendation['junction_id']}-"
                f"{recommendation.get('rank', 0)}",

            "junction_id":
                recommendation["junction_id"],

            "command_type":
                recommendation["command_type"],

            "priority":
                recommendation["priority"],

            "priority_score":
                recommendation["priority_score"],

            "reason":
                recommendation["main_action"],

            "target_queue":
                recommendation["problem"]["queue_length"],

            "target_waiting_time":
                recommendation["problem"]["waiting_time"],

            "expected_improvement":
                recommendation["expected_improvement"],

            "status":
                "READY",

            "execution_mode":
                "SIMULATION"
        }

        self.commands.append(command)

        return command

    # ============================================================
    # CREATE ALL COMMANDS
    # ============================================================

    def create_all_commands(self):

        self.commands = []

        self.rank_recommendations()

        for recommendation in self.recommendations:

            self.create_command(
                recommendation
            )

        return self.commands

    # ============================================================
    # EXECUTE COMMAND
    # ============================================================

    def execute_command(self, command):

        command["status"] = "READY"

        command["status"] = "EXECUTING"

        command["status"] = "APPLIED"

        command["status"] = "MONITORING"

        command["status"] = "COMPLETED"

        self.execution_history.append({

            "command_id":
                command["command_id"],

            "junction_id":
                command["junction_id"],

            "command_type":
                command["command_type"],

            "priority":
                command["priority"],

            "final_status":
                command["status"],

            "execution_mode":
                command["execution_mode"]
        })

        return command

    # ============================================================
    # EXECUTE ALL
    # ============================================================

    def execute_all_commands(
        self,
        commands=None
    ):

        if commands is None:
            commands = self.commands

        results = []

        for command in commands:

            results.append(
                self.execute_command(
                    command
                )
            )

        return results

    # ============================================================
    # POST EXECUTION
    # ============================================================

    def calculate_post_execution_result(
        self,
        recommendation
    ):

        problem = recommendation["problem"]

        before_queue = problem["queue_length"]
        before_waiting = problem["waiting_time"]
        before_efficiency = problem["signal_efficiency"]
        before_throughput = problem["throughput"]

        improvement = recommendation[
            "expected_improvement"
        ]

        after_queue = (
            before_queue
            * (1 - improvement / 100)
        )

        after_waiting = (
            before_waiting
            * (1 - improvement / 100)
        )

        efficiency_gain = (
            (100 - before_efficiency)
            * (improvement / 100)
        )

        after_efficiency = min(
            before_efficiency
            + efficiency_gain,
            100
        )

        throughput_gain = (
            before_throughput
            * (improvement / 100)
        )

        after_throughput = (
            before_throughput
            + throughput_gain
        )

        return {

            "junction_id":
                recommendation["junction_id"],

            "command_type":
                recommendation["command_type"],

            "status":
                "SIMULATED",

            "before": {

                "queue_length":
                    before_queue,

                "waiting_time":
                    before_waiting,

                "signal_efficiency":
                    before_efficiency,

                "throughput":
                    before_throughput
            },

            "after": {

                "queue_length":
                    round(after_queue, 2),

                "waiting_time":
                    round(after_waiting, 2),

                "signal_efficiency":
                    round(after_efficiency, 2),

                "throughput":
                    round(after_throughput, 2)
            },

            "improvement": {

                "queue_reduction":
                    round(
                        before_queue - after_queue,
                        2
                    ),

                "waiting_time_reduction":
                    round(
                        before_waiting - after_waiting,
                        2
                    ),

                "efficiency_gain":
                    round(
                        after_efficiency
                        - before_efficiency,
                        2
                    ),

                "throughput_gain":
                    round(
                        after_throughput
                        - before_throughput,
                        2
                    )
            }
        }

    # ============================================================
    # ALL POST EXECUTION
    # ============================================================

    def calculate_all_post_execution_results(self):

        self.performance_comparison = []

        for recommendation in self.recommendations:

            result = (
                self.calculate_post_execution_result(
                    recommendation
                )
            )

            self.performance_comparison.append(
                result
            )

        return self.performance_comparison

    # ============================================================
    # CITY-WIDE SUMMARY
    # ============================================================

    def generate_city_summary(self):

        comparison = self.performance_comparison

        total_junctions = len(
            comparison
        )

        total_queue_before = 0
        total_queue_after = 0

        total_waiting_before = 0
        total_waiting_after = 0

        total_throughput_before = 0
        total_throughput_after = 0

        total_efficiency_before = 0
        total_efficiency_after = 0

        for result in comparison:

            total_queue_before += (
                result["before"]["queue_length"]
            )

            total_queue_after += (
                result["after"]["queue_length"]
            )

            total_waiting_before += (
                result["before"]["waiting_time"]
            )

            total_waiting_after += (
                result["after"]["waiting_time"]
            )

            total_throughput_before += (
                result["before"]["throughput"]
            )

            total_throughput_after += (
                result["after"]["throughput"]
            )

            total_efficiency_before += (
                result["before"]["signal_efficiency"]
            )

            total_efficiency_after += (
                result["after"]["signal_efficiency"]
            )

        if total_junctions > 0:

            average_efficiency_before = (
                total_efficiency_before
                / total_junctions
            )

            average_efficiency_after = (
                total_efficiency_after
                / total_junctions
            )

        else:

            average_efficiency_before = 0
            average_efficiency_after = 0

        queue_reduction = (
            total_queue_before
            - total_queue_after
        )

        waiting_reduction = (
            total_waiting_before
            - total_waiting_after
        )

        throughput_gain = (
            total_throughput_after
            - total_throughput_before
        )

        efficiency_gain = (
            average_efficiency_after
            - average_efficiency_before
        )

        completed_commands = len([

            command
            for command in self.commands

            if command["status"]
            == "COMPLETED"
        ])

        critical_count = len(
            self.get_critical_junctions()
        )

        high_count = len(
            self.get_high_priority_junctions()
        )

        if critical_count > 0:

            city_status = "CRITICAL"

        elif high_count > 0:

            city_status = "HIGH ATTENTION"

        else:

            city_status = "STABLE"

        self.city_summary = {

            "city_status":
                city_status,

            "junctions":
                total_junctions,

            "recommendations":
                len(self.recommendations),

            "commands":
                len(self.commands),

            "completed_commands":
                completed_commands,

            "critical_junctions":
                critical_count,

            "high_priority_junctions":
                high_count,

            "queue": {

                "before":
                    round(total_queue_before, 2),

                "after":
                    round(total_queue_after, 2),

                "reduction":
                    round(queue_reduction, 2)
            },

            "waiting_time": {

                "before":
                    round(total_waiting_before, 2),

                "after":
                    round(total_waiting_after, 2),

                "reduction":
                    round(waiting_reduction, 2)
            },

            "throughput": {

                "before":
                    round(total_throughput_before, 2),

                "after":
                    round(total_throughput_after, 2),

                "gain":
                    round(throughput_gain, 2)
            },

            "signal_efficiency": {

                "before":
                    round(
                        average_efficiency_before,
                        2
                    ),

                "after":
                    round(
                        average_efficiency_after,
                        2
                    ),

                "gain":
                    round(
                        efficiency_gain,
                        2
                    )
            },

            "execution_mode":
                "SIMULATION"
        }

        return self.city_summary

    # ============================================================
    # GETTERS
    # ============================================================

    def get_execution_history(self):
        return self.execution_history.copy()

    def get_comparison(self):
        return self.performance_comparison.copy()

    def get_city_summary(self):
        return self.city_summary.copy()

    def get_commands(self):
        return self.commands.copy()

    def get_top_priority(self, count=3):

        if not self.recommendations:
            return []

        return self.rank_recommendations()[:count]

    def get_critical_junctions(self):

        return [
            recommendation
            for recommendation in self.recommendations
            if recommendation["priority"]
            == "CRITICAL"
        ]

    def get_high_priority_junctions(self):

        return [
            recommendation
            for recommendation in self.recommendations
            if recommendation["priority"]
            in ["CRITICAL", "HIGH"]
        ]

    # ============================================================
    # STATUS
    # ============================================================

    def get_status(self):

        completed = len([

            command
            for command in self.commands

            if command["status"]
            == "COMPLETED"
        ])

        return {

            "total_recommendations":
                len(self.recommendations),

            "total_commands":
                len(self.commands),

            "completed_commands":
                completed,

            "comparison_results":
                len(self.performance_comparison),

            "critical":
                len(
                    self.get_critical_junctions()
                ),

            "high_priority":
                len(
                    self.get_high_priority_junctions()
                )
        }