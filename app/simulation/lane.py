from dataclasses import dataclass, field
from typing import List


@dataclass
class Lane:
    direction: str

    vehicle_count: int = 0
    queue_length: int = 0
    total_waiting_time: float = 0.0
    traffic_density: float = 0.0

    vehicles: List = field(default_factory=list)

    MAX_LANE_CAPACITY = 100

    def add_vehicle(self, vehicle):
        """Add a vehicle to the lane."""

        if self.vehicle_count >= self.MAX_LANE_CAPACITY:
            return False

        self.vehicles.append(vehicle)

        self.update_metrics()

        return True

    def remove_vehicle(self):
        """Remove the first vehicle from the queue."""

        if not self.vehicles:
            return None

        vehicle = self.vehicles.pop(0)

        self.update_metrics()

        return vehicle

    def update_metrics(self):
        """Update vehicle count, queue length and density."""

        self.vehicle_count = len(self.vehicles)

        self.queue_length = len(self.vehicles)

        self.traffic_density = (
            self.vehicle_count /
            self.MAX_LANE_CAPACITY
        )

    def update_waiting_time(self, seconds):
        """Increase waiting time for stopped vehicles."""

        for vehicle in self.vehicles:

            if not vehicle.is_moving:

                vehicle.wait(seconds)

        self.update_total_waiting_time()

    def update_total_waiting_time(self):

        self.total_waiting_time = sum(
            vehicle.waiting_time
            for vehicle in self.vehicles
        )

    def get_average_waiting_time(self):

        if self.vehicle_count == 0:
            return 0

        return (
            self.total_waiting_time /
            self.vehicle_count
        )

    def get_status(self):

        return {
            "direction": self.direction,
            "vehicle_count": self.vehicle_count,
            "queue_length": self.queue_length,
            "average_waiting_time": round(
                self.get_average_waiting_time(),
                2
            ),
            "traffic_density": round(
                self.traffic_density,
                2
            )
        }