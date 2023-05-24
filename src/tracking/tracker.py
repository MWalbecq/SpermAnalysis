import os
import pickle

import numpy as np
from scipy.interpolate import interp1d

from tracking.cell import Cell
from utils.files import get_key_labels_files


class CellTracker:
    def __init__(self, folder_path: str, cells: list) -> None:
        self.folder_path = folder_path
        self.cells = cells

    def get_cell_coordinates(self, line: str) -> list:
        return list(map(float, line.split(" ")[1:3]))

    def get_cell_position(self, filename: str) -> list:
        with open(self.folder_path + "\\" + filename) as f:
            return list(map(self.get_cell_coordinates, f.readlines()))

    def initialize_cells(self):
        initial_file = os.listdir(self.folder_path)[0]
        for index, cell_position in enumerate(
            self.get_cell_position(filename=initial_file)
        ):
            cell = Cell(number_id=index + 1)
            cell.positions[0] = cell_position
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
        for coordinates in self.get_cell_position(filename=filename):
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
            cell.positions[frame+1] = cell_coords_mapping[cell][0]

    def track(self):
        files = sorted(os.listdir(self.folder_path)[1:], key=get_key_labels_files)
        for frame, filename in enumerate(files):
            cell_coords_mapping = self.associate_next_coords_to_cells(filename=filename)
            cell_coords_mapping = self.create_cells_if_multiple_coords(
                cell_coords_mapping=cell_coords_mapping
            )
            self.set_new_positions(frame=frame, cell_coords_mapping=cell_coords_mapping)

    def interpolate_missing_coordinates(self):
        for cell in self.cells:
            positions = cell.positions
            values = [positions[i] for i in range(25) if positions[i] != [0, 0]]
            frames = [i for i in range(25) if positions[i] != [0, 0]]
            missing_frames = [i for i in range(25) if positions[i] == [0, 0]]

            if len(frames) > len(missing_frames):
                x_coords, y_coords = zip(*values)
                interp = interp1d(x=frames, y=x_coords, kind="nearest", fill_value="extrapolate")
                x_interpolated = interp(missing_frames)

                interp = interp1d(frames, y_coords, kind="nearest", fill_value="extrapolate")
                y_interpolated = interp(missing_frames)

                interpolated = values + list(map(list, zip(x_interpolated, y_interpolated)))
                frames = frames + missing_frames
                sorted_interpolated = [x for _, x in sorted(zip(frames, interpolated))]

                cell.positions = sorted_interpolated

    def find_zero_sublist(self, lst: list) ->list:
        all = []
        nb_zero = 0
        start = [0, 0]
        start_index = 0
        
        for index, elem in enumerate(lst):
            if (start != [0, 0]) and (elem != [0, 0]):
                if nb_zero == 0:
                    start = elem
                    start_index = index
                    
                else:
                    all.append((start_index, [start] + [[0, 0]] * nb_zero + [elem]))
                    start = [0, 0]
            
            if (start == [0, 0]) and (elem != [0, 0]):
                nb_zero = 0
                start = elem
                start_index = index
                
            if (start != [0, 0]) and (elem == [0, 0]):
                nb_zero += 1
    
        return all

    def fill_gap_positions(self):
        for cell in self.cells:
            zero_sublist = self.find_zero_sublist(cell.positions)
            for elem in zero_sublist:
                index, lst = elem
                new_pos = np.round(np.linspace(lst[0], lst[-1], len(lst)), 6).tolist()
                for coord in new_pos:
                    cell.positions[index] = coord
                    index += 1

    def get_pickle(self):
        cells_path = {}
        for cell in self.cells:
            if [0, 0] not in cell.positions:
                cells_path.update({cell.number_id: cell.positions})

        with open(r'data\track\result.pickle', 'wb') as f:
            pickle.dump(cells_path, f)