import os

from ultralytics import YOLO

from parameters.motility import MotilityCalculator
from tracking.tracker import CellTracker
from utils.files import get_key_detect_folder
from viz.visualize import Visualizer

if __name__ == "__main__":
    # Replace with UI ? (Path to the video)
    ############################################################################################
    #                               MODIFY PATH TO THE VIDEO HERE                              #   
    path_video = r"C:\Users\Maximilien\Desktop\General\Niort\vid_24355_0.mpg"                  #
    ############################################################################################
    
    # Detection
    model = YOLO(r"data\model\small_360_4_SGD\weights\last.pt")
    model.predict(
        source=path_video,
        conf=0.10,
        iou=0.2,
        save_txt=True,
        save=True,
        show_labels=False,
        show_conf=False,
        line_width=1,
    )

    last_folder = sorted(os.listdir("./runs/detect/"), key=get_key_detect_folder)[-1]
    folder_path = ".\\runs\\detect\\" + last_folder + "\\labels"
    cells = []

    # Tracking
    tracker = CellTracker(folder_path=folder_path, cells=cells)
    tracker.initialize_cells()
    tracker.track()
    # tracker.fill_gap_positions()
    tracker.interpolate_missing_coordinates()
    tracker.get_pickle()

    # Motility
    calculator = MotilityCalculator(cells=cells)
    parameters = calculator.get_heteromotility_parameters()
    calculator.motility_compute(parameters=parameters)

    # Visualization
    visualizer = Visualizer(cells=cells, filename=last_folder, path_video=path_video)
    visualizer.create_folder()
    visualizer.cut_video_into_frames()
    visualizer.draw_cells_trajectory()

    l4 = [66, 70, 85, 25, 39]
    l3 = [33, 12, 47, 19, 56]
    l2 = [50, 7, 15, 5, 32]
    l1 = [84, 27, 78, 109, 52]
    for l in [l4, l3, l2, l1]:
        for cell in cells:
            if cell.number_id in l:
                print(cell.number_id, cell.total_distance, cell.linearity, cell.avg_speed)

        print("\n")


 