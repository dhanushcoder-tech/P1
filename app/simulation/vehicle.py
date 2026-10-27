import uuid


class Vehicle:

    def __init__(self, vehicle_type="car"):

        self.id = str(uuid.uuid4())[:8]

        self.vehicle_type = vehicle_type

        self.current_junction = None
        self.destination_junction = None

        self.is_moving = False

    def start(self):

        self.is_moving = True

    def stop(self):

        self.is_moving = False