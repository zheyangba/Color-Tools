import os
import argparse
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtWidgets, uic



from interface_design.Zhuti import Zhuti

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-path", type=str, default="dataset")
    parser.add_argument("--categories", type=str)
    args = parser.parse_args()

    dataset_path = args.dataset_path
    categories = None
    if args.categories is not None:
        categories = args.categories.split(",")
    coco_json_path = os.path.join(dataset_path, "annotations.json")

    # window =  Ui_zhutibopianClass()
    # app = QApplication(sys.argv)
    # editor = Editor(
    #     dataset_path,
    #     categories=categories,
    #     coco_json_path=coco_json_path
    # )
    #
    # app = QApplication(sys.argv)
    # window = ApplicationInterface(app, editor)
    # window.show()
    # sys.exit(app.exec_())

    app = QApplication(sys.argv)
    # app.setStyleSheet(open('Data/style.qss', 'rb').read().decode('utf-8'))
    w = Zhuti()
    w.show()
    sys.exit(app.exec_())

    # app = QApplication(sys.argv)
    # mainWindow = QMainWindow()
    # form = zhuti_fun(mainWindow)
    # mainWindow.show()
    # sys.exit(app.exec_())
