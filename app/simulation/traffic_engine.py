import random
import time

from app.simulation.vehicle import Vehicle


class TrafficEngine:

    def __init__(self, junction):

        self.junction = junction

        self.simulation_time = 0

        # Maximum vehicles that can pass
        # from one lane per simulation tick
        self.vehicles_per_green_tick = 2

        self.vehicle_types = [
            "car",
            "car",
            "car",
            "car",
            "motorcycle",
            "motorcycle",
            "bus",
            "truck"
        ]

    def spawn_vehicle(self, direction):
        """Create and add a vehicle to a lane."""

        vehicle_type = random.choice(
            self.vehicle_types
        )

        vehicle = Vehicle(vehicle_type)

        vehicle.entered_simulation_time = (
            self.simulation_time
        )

        lane = self.junction.get_lane(
            direction
        )

        added = lane.add_vehicle(vehicle)

        if added:

            print(
                f"➕ [{self.simulation_time:03d}s] "
                f"{vehicle.vehicle_type.upper()} "
                f"entered {direction}"
            )

    def spawn_random_traffic(self):
        """
        Randomly generate traffic.
        Each direction has a chance of
        receiving new vehicles.
        """

        directions = [
            "NORTH",
            "SOUTH",
            "EAST",
            "WEST"
        ]

        for direction in directions:

            # 60% probability
            if random.random() < 0.60:

                self.spawn_vehicle(direction)

    def process_signals(self):
        """
        GREEN lanes release vehicles.
        RED lanes accumulate waiting time.
        """

        for direction, lane in (
            self.junction.lanes.items()
        ):

            signal = self.junction.signal_state[
                direction
            ]

            if signal == "GREEN":

                self.release_vehicles(
                    direction
                )

            else:

                lane.update_waiting_time(1)

    def release_vehicles(self, direction):

        lane = self.junction.get_lane(
            direction
        )

        vehicles_to_release = min(
            self.vehicles_per_green_tick,
            lane.vehicle_count
        )

        for _ in range(
            vehicles_to_release
        ):

            vehicle = lane.remove_vehicle()

            if vehicle:

                vehicle.start()

                print(
                    f"🚗 [{self.simulation_time:03d}s] "
                    f"{vehicle.vehicle_type.upper()} "
                    f"passed from {direction} "
                    f"(waited {vehicle.waiting_time:.1f}s)"
                )

    def update(self):
        """
        Run one simulation tick.
        One tick = one second.
        """

        self.simulation_time += 1

        # New vehicles arrive
        self.spawn_random_traffic()

        # Signals control movement
        self.process_signals()

    def print_status(self):

        print(
            "\n"
            "=========================================="
        )

        print(
            f"⏱ SIMULATION TIME: "
            f"{self.simulation_time} seconds"
        )

        print(
            "=========================================="
        )

        for direction, lane in (
            self.junction.lanes.items()
        ):

            signal = self.junction.signal_state[
                direction
            ]

            status = lane.get_status()

            print(
                f"\n{direction} "
                f"[{signal}]"
            )

            print(
                f"  Vehicles: "
                f"{status['vehicle_count']}"
            )

            print(
                f"  Queue: "
                f"{status['queue_length']}"
            )

            print(
                f"  Density: "
                f"{status['traffic_density']}"
            )

            print(
                f"  Avg Wait: "
                f"{status['average_waiting_time']} sec"
            )