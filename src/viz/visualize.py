import cv2
import random
import os

from PIL import Image, ImageFont, ImageDraw
import numpy as np

from utils.files import get_key_img_files
from tracking.cell import Cell

class Visualizer:
    def __init__(self, cells: list[Cell], filename: str, path_video: str) -> None:
        self.cells = cells
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
                
    def get_colors(self):
        colors = [
            "#60f04a", # 1
            "#fae282", # 2
            "#eb9f94", # 3
            "#ffb338", # 4
            "#f571e1", # 5
        ]
        return colors

    def draw_cells_trajectory(self):
        font = ImageFont.truetype("arial.ttf")
        colors = self.get_colors()

        for index, image_name in enumerate(sorted(os.listdir(rf"data\viz\{self.filename}"), key=get_key_img_files)):
            image = Image.open(rf"data\viz\{self.filename}\{image_name}")
            width, height = image.size
            image_edit = ImageDraw.Draw(image)
        
            for cell in self.cells:
                positions = cell.positions
                if [0, 0] not in positions:
                    for j in range(0, index):
                        if (positions[j] != [0, 0]) and (positions[j+1] != [0, 0]): # TODO Check
                            x_before, y_before = positions[j][0] * width, positions[j][1] * height
                            x_after, y_after = positions[j+1][0] * width, positions[j+1][1] * height
                            image_edit.line(((x_before, y_before), (x_after, y_after)), width=1, fill=colors[cell.motility - 1])

                    x, y = positions[index][0] * width, positions[index][1] * height
                    image_edit.ellipse((x, y, x + 5, y + 5), fill=colors[cell.motility - 1], outline=(0, 0, 0))
                    image_edit.text((x, y + 10), f"{cell.number_id}({cell.motility})", (255, 255, 255), font=font)

            image.save(rf"data\viz\{self.filename}\{image_name}")
