class Road:

    def __init__(
        self,
        road_id,
        source,
        destination,
        travel_time=5
    ):

        self.road_id = road_id

        self.source = source

        self.destination = destination

        self.travel_time = travel_time

        self.vehicles = []

    def add_vehicle(self, vehicle):

        vehicle.road_time = 0

        self.vehicles.append(vehicle)

    def update(self):

        arrived = []

        for vehicle in self.vehicles:

            vehicle.road_time += 1

            if vehicle.road_time >= self.travel_time:

                arrived.append(vehicle)

        for vehicle in arrived:

            self.vehicles.remove(vehicle)

        return arrived

    def get_vehicle_count(self):

        return len(self.vehicles)

    def get_status(self):

        return {
            "road_id": self.road_id,
            "source": self.source,
            "destination": self.destination,
            "travel_time": self.travel_time,
            "vehicles": self.get_vehicle_count()
        }