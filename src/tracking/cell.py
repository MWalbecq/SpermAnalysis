from math import sqrt

class Cell:
    def __init__(self, number_id: int) -> None:
        self.number_id = number_id
        self.positions = [[0, 0]] * 25

    def get_number_id(self):
        return self.number_id
    
    def get_positions(self):
        return self.positions

    def set_position(self, frame:int, coordinates: list):
        self.positions[frame] = coordinates
    
    def get_last_position(self):
        return [pos for pos in self.positions if pos != [0, 0]][-1][:]

    def get_distance(self, coordinates: list):
        x_pos, y_pos = coordinates
        x_cell, y_cell = self.get_last_position()
        return sqrt(pow(x_pos - x_cell, 2) + pow(y_pos - y_cell, 2))