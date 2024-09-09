import glob
import json
import os

import cv2
from imantics import Dataset, Image, Mask, Category

dataset = Dataset("pores")
category = Category("pore")
category.id = 1

origin_files = []
mask_files = []

folder_path = "D:\\0\\test\images"


for file_path in glob.glob(os.path.join(folder_path, "*")):
    if os.path.isfile(file_path):
        _, file_extension = os.path.splitext(file_path)
        if file_extension.lower() == ".png":
            origin_files.append(file_path)
        elif file_extension.lower() == ".jpg" or file_extension.lower() == ".jpeg":
            mask_files.append(file_path)


def get_file(path):
    filename = os.path.basename(path)
    filename = os.path.splitext(filename)[0]
    filename = filename.split('.')[0]
    filename = filename + '_mask.jpg'
    directory = os.path.dirname(path)
    return directory+"\\"+filename


for index,img_file in enumerate(origin_files):
    path_mask = get_file(img_file)

    image = cv2.imread(img_file)[:, :, ::-1]
    image = Image(image,id=index+1,path = img_file)

    mask = cv2.imread(path_mask, 0)
    mask = Mask(mask)
    image.add(mask, category)
    dataset.add(image)

data = dataset.coco()
with open(folder_path + '\\Tone.json', 'w') as output_json_file:
    json.dump(data, output_json_file)



