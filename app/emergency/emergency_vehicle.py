from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class EmergencyVehicle:
    """
    Represents an emergency vehicle detected in the city.

    Currently supports ambulance/emergency priority logic.
    """

    vehicle_id: str
    vehicle_type: str = "ambulance"

    # Current position
    current_junction: Optional[str] = None

    # Destination
    destination_junction: Optional[str] = None

    # Route through the city
    route: List[str] = field(default_factory=list)

    # Current position in the route
    route_index: int = 0

    # Emergency status
    detected: bool = False
    active: bool = False
    priority: bool = True

    # Signal currently being prioritized
    priority_junction: Optional[str] = None

    # Whether the emergency vehicle has crossed the junction
    crossed_current_junction: bool = False

    def activate(self):
        """Activate emergency priority."""
        self.detected = True
        self.active = True
        self.priority = True

    def deactivate(self):
        """Deactivate emergency priority."""
        self.active = False
        self.priority = False
        self.priority_junction = None

    def set_route(self, route: List[str]):
        """Set the emergency vehicle's route."""
        self.route = route
        self.route_index = 0

        if route:
            self.current_junction = route[0]

    def get_next_junction(self) -> Optional[str]:
        """Return the next junction in the emergency route."""

        if not self.route:
            return None

        next_index = self.route_index + 1

        if next_index < len(self.route):
            return self.route[next_index]

        return None

    def move_to_next_junction(self) -> Optional[str]:
        """Move the emergency vehicle to the next junction."""

        next_junction = self.get_next_junction()

        if next_junction is None:
            return None

        self.route_index += 1
        self.current_junction = next_junction
        self.crossed_current_junction = False

        return next_junction

    def has_reached_destination(self) -> bool:
        """Check whether the emergency vehicle reached its destination."""

        if not self.route:
            return False

        return self.route_index >= len(self.route) - 1

    def mark_crossed(self):
        """Mark the current junction as crossed."""
        self.crossed_current_junction = True

    def __str__(self):
        return (
            f"EmergencyVehicle("
            f"id={self.vehicle_id}, "
            f"type={self.vehicle_type}, "
            f"junction={self.current_junction}, "
            f"active={self.active})"
        )