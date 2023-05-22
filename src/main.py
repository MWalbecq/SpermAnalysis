import os

from ultralytics import YOLO

from tracking.tracker import CellTracker
from utils.files import get_key_detect_folder
from viz.visualize import Visualizer

if __name__ == "__main__":
    # Replace with UI ? (Path to the video)
    ############################################################################################
    #                               MODIFY PATH TO THE VIDEO HERE                              #   
    path_video = r"C:\Users\Maximilien\Desktop\General\Niort-2\vid_30779_0.mpg"                  #
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

    # Tracking
    tracker = CellTracker(folder_path=folder_path)
    tracker.initialize_cells()
    tracker.track()
    # tracker.fill_gap_positions()
    tracker.write_result()

    # Visualization
    visualizer = Visualizer(filename=last_folder, path_video=path_video)
    visualizer.create_folder()
    visualizer.cut_video_into_frames()
    visualizer.draw_cells_trajectory()

    # Motility
