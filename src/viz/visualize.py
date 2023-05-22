import cv2
import random
import os

from PIL import Image, ImageFont, ImageDraw
import numpy as np

from utils.files import get_key_img_files

class Visualizer:
    def __init__(self, filename: str, path_video: str) -> None:
        self.filename = filename
        self.path_video = path_video

    def create_folder(self):
        os.mkdir(rf"data\viz\{self.filename}")

    def cut_video_into_frames(self):
        vidcap = cv2.VideoCapture(self.path_video)
        success, image = vidcap.read()
        count = 0
        while success:
            cv2.imwrite(rf"data\viz\{self.filename}\{self.filename}_{count}.jpg", image)
            success,image = vidcap.read()
            count += 1
        
    def get_cells(self):
        with open(r"data\track\result.txt", "r") as f:
            lines = f.read().splitlines()
        len_cells = int(len(lines) / 25)
        cells = [cell.tolist() for cell in np.array_split(lines, len_cells)]
        cells = [[list(map(float, item.split()[2:4])) for item in sublist] for sublist in cells]


        return cells, len_cells
        
    def get_colors(self, len_cells: int):
        colors = []
        for _ in range(len_cells):
            de = random.randint(0,255)
            re = random.randint(0,255)
            we = random.randint(0,255)
            colors.append((de, re, we))

        return colors

    def draw_cells_trajectory(self):
        font = ImageFont.truetype("arial.ttf")
        for index, image_name in enumerate(sorted(os.listdir(rf"data\viz\{self.filename}"), key=get_key_img_files)):
            image = Image.open(rf"data\viz\{self.filename}\{image_name}")
            width, height = image.size
            image_edit = ImageDraw.Draw(image)
        
            cells, len_cells = self.get_cells()
            colors = self.get_colors(len_cells=len_cells)

            for cell, color in zip(cells, colors):
                for j in range(0, index):
                    if (cell[j] != [0, 0]) and (cell[j+1] != [0, 0]): # TODO Check
                        x_before, y_before = cell[j][0] * width, cell[j][1] * height
                        x_after, y_after = cell[j+1][0] * width, cell[j+1][1] * height
                        image_edit.line(((x_before, y_before), (x_after, y_after)), width=1, fill=color)

                x, y = cell[index][0] * width, cell[index][1] * height
                image_edit.ellipse((x, y, x + 5, y + 5), fill=color, outline=(0, 0, 0))
                image_edit.text((x, y + 10), str(cells.index(cell)), (255, 255, 255), font=font)

            image.save(rf"data\viz\{self.filename}\{image_name}")
