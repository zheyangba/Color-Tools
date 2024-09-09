import os

import cv2
import numpy as np

from Common import Suanfa


def get_all_files(folder_path):
    image_extensions = (".gif", ".bmp", ".tif")
    file_paths = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(image_extensions):
                name = os.path.basename(file)+"_mask.png"
                file_path = os.path.join(root, file)
                file_paths.append(os.path.abspath(file_path))

    return file_paths


def open_image_file(file_path):
    try:

        img = cv2.imread(file_path)

        if img is not None:

            return img
        else:

            print("Error: Invalid image file.")
    except Exception as e:
        #
        print("Error:", str(e))


def calculate_mask(img, h_min, h_max, con_thread, ostu_thread=50,is_check=False):
    hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv_image)

    low_hsv = np.array(h_min, dtype="uint8")
    high_hsv = np.array(h_max, dtype="uint8")


    mask = cv2.inRange(h, low_hsv, high_hsv)
    s[mask != 255] = 0
    v[mask != 255] = 0

    s = s.astype(np.int32)
    v = v.astype(np.int32)

    quchu = Suanfa.wavelet_domain_denoise(0.8 * s + 0.2 * v)

    mask = cv2.adaptiveThreshold(quchu, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 501, -ostu_thread)

    mask = Suanfa.baweraopen(mask, con_thread)


    if is_check:
        mask = Suanfa.get_contour(mask)
    return mask


def bgr2rgb(bgr_image):
    rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
    return rgb_image

def open_mask_with_name(path):
    dir_path = os.path.dirname(path)
    # 获取文件名（包括扩展名）
    file_name = os.path.basename(path)

    # 分离文件名和扩展名
    file_name_no_ext = os.path.splitext(file_name)[0]

    real_file_name = dir_path+"\\"+file_name_no_ext+"_mask.png"
    try:

        img = cv2.imread(real_file_name,cv2.IMREAD_GRAYSCALE)

        if img is not None:

            return img
        else:

            print("Error: Invalid image file.")
    except Exception as e:

        print("Error:", str(e))

def imshow(name,img):
    cv2.imshow(name, img)
    cv2.waitKey(0)


    cv2.destroyAllWindows()



