import os

from ultralytics import YOLO

from tracking.tracker import CellTracker

if __name__ == "__main__":
    # Replace with UI ? (Path to the video)
    ############################################################################################
    #                               MODIFY PATH TO THE VIDEO HERE                              #   
    path_video = r"C:\Users\Maximilien\Desktop\General\Niort\vid_24355_0.mpg"                  #
    ############################################################################################
    
    # model = YOLO(r"data\model\small_360_4_SGD\weights\last.pt")
    # model.predict(
    #     source=path_video,
    #     conf=0.15,
    #     iou=0.2,
    #     save_txt=True,
    #     save=True,
    #     show_labels=False,
    #     show_conf=False,
    #     line_width=1,
    # )

    # attention folders -1 est peut-être pas le dernier (1, 10, 11, 2, 21)
    folders = os.listdir("./runs/detect/")
    folder_path = ".\\runs\\detect\\" + folders[-1] + "\\labels"

    tracker = CellTracker(folder_path=folder_path)
    tracker.initialize_cells()
    tracker.track()
    tracker.fill_gap_positions()
    tracker.write_result()

