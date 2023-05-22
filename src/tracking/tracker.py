import os

import numpy as np

from tracking.cell import Cell
from utils.files import get_key_labels_files


class CellTracker:
    def __init__(self, folder_path: str) -> None:
        self.folder_path = folder_path
        self.cells = []

    def get_cell_coordinates(self, line: str) -> list:
        return list(map(float, line.split(" ")[1:3]))

    def get_cells_positions(self, filename: str) -> list:
        with open(self.folder_path + "\\" + filename) as f:
            return list(map(self.get_cell_coordinates, f.readlines()))

    def initialize_cells(self):
        initial_file = os.listdir(self.folder_path)[0]
        for index, cell_position in enumerate(
            self.get_cells_positions(filename=initial_file)
        ):
            cell = Cell(number_id=index + 1)
            cell.set_position(frame=0, coordinates=cell_position)
            self.cells.append(cell)

    def get_nearest_cell(self, coordinates: list) -> Cell:
        nearest_cell = self.cells[0]
        distance_min = nearest_cell.get_distance(coordinates=coordinates)

        for cell in self.cells[1:]:
            if cell.get_distance(coordinates=coordinates) < distance_min:
                nearest_cell = cell
                distance_min = cell.get_distance(coordinates=coordinates)

        return nearest_cell

    def associate_next_coords_to_cells(self, filename: str) -> dict:
        cell_coords_mapping = {}
        for coordinates in self.get_cells_positions(filename=filename):
            nearest_cell = self.get_nearest_cell(coordinates=coordinates)

            if nearest_cell not in cell_coords_mapping.keys():
                cell_coords_mapping.update({nearest_cell: [coordinates]})

            else:
                cell_coords_mapping[nearest_cell].append(coordinates)

        return cell_coords_mapping

    def create_cells_if_multiple_coords(self, cell_coords_mapping: dict) -> dict:
        cells_with_multiple_coords = {
            key: value for key, value in cell_coords_mapping.items() if len(value) > 1
        }
        for cell, all_coordinates in cells_with_multiple_coords.items():
            all_diff = list(map(cell.get_distance, all_coordinates))
            selected_coords = all_coordinates[all_diff.index(min(all_diff))]
            other_coords = [
                coords for coords in all_coordinates if coords != selected_coords
            ]

            cell_coords_mapping.update({cell: [selected_coords]})
            for coords in other_coords:
                new_cell = Cell(number_id=len(self.cells) + 1)
                self.cells.append(new_cell)
                cell_coords_mapping.update({new_cell: [coords]})

        return cell_coords_mapping

    def set_new_positions(self, frame: int, cell_coords_mapping: dict):
        for cell in cell_coords_mapping:
            cell.set_position(frame=frame + 1, coordinates=cell_coords_mapping[cell][0])

    def track(self):
        files = sorted(os.listdir(self.folder_path)[1:], key=get_key_labels_files)
        for frame, filename in enumerate(files):
            cell_coords_mapping = self.associate_next_coords_to_cells(filename=filename)
            cell_coords_mapping = self.create_cells_if_multiple_coords(
                cell_coords_mapping=cell_coords_mapping
            )
            self.set_new_positions(frame=frame, cell_coords_mapping=cell_coords_mapping)

    def find_zero_sublist(self, lst: list) ->list:
        results = []
        count_zeros = 0
        for i in range(1, len(lst)):
            if lst[i] == [0, 0]:
                count_zeros += 1
            else:
                if count_zeros <= 3 and count_zeros > 0:
                    results.append(
                        (i - count_zeros - 1, lst[i - count_zeros - 1 : i + 1])
                    )
                count_zeros = 0
        return results

    def fill_gap_positions(self):
        for cell in self.cells:
            zero_sublist = self.find_zero_sublist(cell.positions)
            for elem in zero_sublist:
                index, lst = elem
                new_pos = np.round(np.linspace(lst[0], lst[-1], len(lst)), 6).tolist()
                for coord in new_pos:
                    cell.set_position(frame=index, coordinates=coord)
                    index += 1

    def write_result(self):
        with open(rf"data\track\result.txt", "w") as f:
            for cell in self.cells:
                for frame in range(25):
                    position = " ".join(list(map(str, cell.get_positions()[frame])))
                    f.write(f"{frame+1} {cell.get_number_id()} {position}\n")
