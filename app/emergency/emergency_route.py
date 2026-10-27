import heapq


class EmergencyRoute:

    def __init__(self):

        self.road_network = {

            "J1": {"J2": 1, "J4": 1},

            "J2": {
                "J1": 1,
                "J3": 1,
                "J5": 1
            },

            "J3": {
                "J2": 1,
                "J6": 1
            },

            "J4": {
                "J1": 1,
                "J5": 1,
                "J7": 1
            },

            "J5": {
                "J2": 1,
                "J4": 1,
                "J6": 1,
                "J8": 1
            },

            "J6": {
                "J3": 1,
                "J5": 1,
                "J9": 1
            },

            "J7": {
                "J4": 1,
                "J8": 1
            },

            "J8": {
                "J5": 1,
                "J7": 1,
                "J9": 1
            },

            "J9": {
                "J6": 1,
                "J8": 1
            }
        }

    # ============================================================
    # CALCULATE SHORTEST ROUTE
    # ============================================================

    def calculate_route(
        self,
        source,
        destination,
        blocked_junctions=None,
        traffic_penalties=None
    ):

        if source not in self.road_network:
            raise ValueError(
                f"Invalid source junction: {source}"
            )

        if destination not in self.road_network:
            raise ValueError(
                f"Invalid destination junction: {destination}"
            )

        if blocked_junctions is None:
            blocked_junctions = []

        if traffic_penalties is None:
            traffic_penalties = {}

        if source in blocked_junctions:
            raise ValueError(
                "Source junction is blocked."
            )

        if destination in blocked_junctions:
            raise ValueError(
                "Destination junction is blocked."
            )

        distances = {
            junction: float("inf")
            for junction in self.road_network
        }

        previous = {
            junction: None
            for junction in self.road_network
        }

        distances[source] = 0

        priority_queue = [
            (0, source)
        ]

        visited = set()

        while priority_queue:

            current_distance, current = (
                heapq.heappop(
                    priority_queue
                )
            )

            if current in visited:
                continue

            visited.add(current)

            if current == destination:
                break

            for neighbor, road_distance in (
                self.road_network[current].items()
            ):

                if neighbor in blocked_junctions:
                    continue

                if neighbor in visited:
                    continue

                traffic_penalty = (
                    traffic_penalties.get(
                        neighbor,
                        0
                    )
                )

                new_distance = (
                    current_distance
                    + road_distance
                    + traffic_penalty
                )

                if (
                    new_distance
                    < distances[neighbor]
                ):

                    distances[neighbor] = (
                        new_distance
                    )

                    previous[neighbor] = (
                        current
                    )

                    heapq.heappush(

                        priority_queue,

                        (
                            new_distance,
                            neighbor
                        )
                    )

        # ========================================================
        # BUILD ROUTE
        # ========================================================

        if (
            distances[destination]
            == float("inf")
        ):

            return {

                "source":
                    source,

                "destination":
                    destination,

                "route":
                    [],

                "distance":
                    0,

                "junctions":
                    0,

                "blocked_junctions":
                    blocked_junctions,

                "status":
                    "NO_ROUTE"
            }

        route = []

        current = destination

        while current is not None:

            route.insert(
                0,
                current
            )

            current = previous[current]

        return {

            "source":
                source,

            "destination":
                destination,

            "route":
                route,

            "distance":
                distances[destination],

            "junctions":
                len(route),

            "blocked_junctions":
                blocked_junctions,

            "traffic_penalties":
                traffic_penalties,

            "status":
                "ROUTE_FOUND"
        }

    # ============================================================
    # GET NEXT JUNCTION
    # ============================================================

    def get_next_junction(
        self,
        route,
        current_junction
    ):

        if current_junction not in route:
            return None

        index = route.index(
            current_junction
        )

        if index + 1 >= len(route):
            return None

        return route[index + 1]

    # ============================================================
    # GET REMAINING ROUTE
    # ============================================================

    def get_remaining_route(
        self,
        route,
        current_junction
    ):

        if current_junction not in route:
            return []

        index = route.index(
            current_junction
        )

        return route[index:]

    # ============================================================
    # TRACK VEHICLE
    # ============================================================

    def track_vehicle(
        self,
        vehicle,
        route_result
    ):

        route = route_result["route"]

        current_junction = (
            vehicle.source_junction
        )

        remaining_route = (
            self.get_remaining_route(
                route,
                current_junction
            )
        )

        next_junction = (
            self.get_next_junction(
                route,
                current_junction
            )
        )

        if (
            current_junction
            == vehicle.destination_junction
        ):

            status = "DESTINATION_REACHED"

        elif next_junction is None:

            status = "ROUTE_COMPLETED"

        else:

            status = "MOVING"

        return {

            "vehicle_id":
                vehicle.vehicle_id,

            "vehicle_type":
                vehicle.vehicle_type,

            "current_junction":
                current_junction,

            "destination":
                vehicle.destination_junction,

            "next_junction":
                next_junction,

            "remaining_route":
                remaining_route,

            "remaining_junctions":
                len(remaining_route),

            "status":
                status
        }

    # ============================================================
    # MOVE VEHICLE
    # ============================================================

    def move_vehicle(
        self,
        vehicle,
        route_result
    ):

        tracking = self.track_vehicle(
            vehicle,
            route_result
        )

        next_junction = (
            tracking["next_junction"]
        )

        if next_junction is None:
            return tracking

        vehicle.update_location(
            next_junction
        )

        return self.track_vehicle(
            vehicle,
            route_result
        )

    # ============================================================
    # RECALCULATE ROUTE
    # ============================================================

    def recalculate_route(
        self,
        vehicle,
        blocked_junctions=None,
        traffic_penalties=None
    ):

        return self.calculate_route(

            source=vehicle.source_junction,

            destination=(
                vehicle.destination_junction
            ),

            blocked_junctions=blocked_junctions,

            traffic_penalties=traffic_penalties
        )