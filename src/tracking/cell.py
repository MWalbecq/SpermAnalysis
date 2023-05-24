from math import sqrt

class Cell:
    def __init__(self, number_id: int) -> None:
        self.number_id = number_id
        self.positions = [[0, 0]] * 25
        self.motility = 5
        self.total_distance = 0
        self.linearity = 0
        self.avg_speed = 0

    def get_last_position(self):
        return [pos for pos in self.positions if pos != [0, 0]][-1][:]

    def get_distance(self, coordinates: list):
        x_pos, y_pos = coordinates
        x_cell, y_cell = self.get_last_position()
        return sqrt(pow(x_pos - x_cell, 2) + pow(y_pos - y_cell, 2))