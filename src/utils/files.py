def get_key_labels_files(filename):
    return int(filename.split("_")[3][:-4])

def get_key_detect_folder(filename):
    key = filename.split("predict")[1]
    if key == "":
        return 0
    return int(key)

def get_key_img_files(filename):
    return int(filename.split("_")[-1][:-4])