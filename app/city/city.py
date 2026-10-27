from app.simulation.junction import Junction
from app.city.coordination import CoordinationManager
from app.city.recommendation import RecommendationEngine


class City:

    def __init__(self):

        # ============================================================
        # CITY JUNCTIONS
        # ============================================================

        self.junctions = {}

        # Create 9 junctions

        for i in range(1, 10):

            junction_id = f"J{i}"

            self.junctions[junction_id] = Junction(
                junction_id
            )

        # ============================================================
        # COORDINATION MANAGER
        # ============================================================

        self.coordinator = CoordinationManager(
            self
        )

        # ============================================================
        # AI RECOMMENDATION ENGINE
        # ============================================================

        self.recommendation_engine = (
            RecommendationEngine()
        )

    # ============================================================
    # GET JUNCTION
    # ============================================================

    def get_junction(
        self,
        junction_id
    ):

        return self.junctions.get(
            junction_id
        )

    # ============================================================
    # GET ALL JUNCTIONS
    # ============================================================

    def get_all_junctions(self):

        return list(
            self.junctions.values()
        )

    # ============================================================
    # GET JUNCTION STATUS
    # ============================================================

    def get_junction_status(
        self,
        junction_id
    ):

        junction = self.get_junction(
            junction_id
        )

        if junction is None:

            return None

        return junction.get_status()

    # ============================================================
    # GET CITY STATUS
    # ============================================================

    def get_city_status(self):

        statuses = []

        for junction in self.junctions.values():

            statuses.append(
                junction.get_status()
            )

        return statuses

    # ============================================================
    # GENERATE AI RECOMMENDATIONS
    # ============================================================

    def generate_recommendations(self):

        # Get performance data

        performance_records = (
            self.coordinator.performance_records
        )

        # Get health results

        health_results = (
            self.coordinator.calculate_all_health_scores()
        )

        # Generate recommendations

        recommendations = (
            self.recommendation_engine.generate_all(

                performance_records,

                health_results
            )
        )

        return recommendations

    # ============================================================
    # GET RECOMMENDATION FOR ONE JUNCTION
    # ============================================================

    def get_recommendation(
        self,
        junction_id
    ):

        return (
            self.recommendation_engine
            .get_junction_recommendation(
                junction_id
            )
        )

    # ============================================================
    # GET CRITICAL RECOMMENDATIONS
    # ============================================================

    def get_critical_recommendations(self):

        return (
            self.recommendation_engine
            .get_critical_junctions()
        )

    # ============================================================
    # GET HIGH PRIORITY RECOMMENDATIONS
    # ============================================================

    def get_high_priority_recommendations(self):

        return (
            self.recommendation_engine
            .get_high_priority_junctions()
        )

    # ============================================================
    # CITY SUMMARY
    # ============================================================

    def get_summary(self):

        health_summary = (
            self.coordinator
            .get_health_summary()
        )

        recommendation_status = (
            self.recommendation_engine
            .get_status()
        )

        return {

            "total_junctions":
                len(self.junctions),

            "health":
                health_summary,

            "recommendations":
                recommendation_status
        }