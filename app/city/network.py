class CityNetwork:

    def __init__(self):

        self.connections = {}

    def add_junction(self, junction_id):

        if junction_id not in self.connections:

            self.connections[junction_id] = []

    def connect(
        self,
        junction_a,
        junction_b
    ):

        self.add_junction(junction_a)
        self.add_junction(junction_b)

        if junction_b not in self.connections[junction_a]:

            self.connections[junction_a].append(
                junction_b
            )

        if junction_a not in self.connections[junction_b]:

            self.connections[junction_b].append(
                junction_a
            )

    def get_neighbors(self, junction_id):

        return self.connections.get(
            junction_id,
            []
        )

    def get_all_connections(self):

        return self.connections