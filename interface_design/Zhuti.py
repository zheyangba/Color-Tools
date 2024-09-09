import os

import cv2
import numpy as np
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QAction, QMessageBox

from Common import All
from Common.Canshu import Canshu
from interface_design.CustomGraphicsView import DorA
from interface_design.colorAdj import Color_adj
from interface_design.zhutibopian import Ui_zhutibopianClass


# @UnresolvedImport
# 本类的功能只是作为一个功能类，保存参数


class Zhuti(QMainWindow, Ui_zhutibopianClass):
    # 信号
    signal_file_change = pyqtSignal(str)  # 文件修改信号
    signal_calculate_mask = pyqtSignal()
    signal_cal_percentage = pyqtSignal()  # 计算掩膜的信号

    plusPressed = pyqtSignal()  # 调节透明度信号
    minusPressed = pyqtSignal()  # 调节透明度信号

    def __init__(self, *args, **kwargs):
        super(Zhuti, self).__init__(*args, **kwargs)
        self.bool_flash = True
        self.setupUi(self)
        # 画面调节参数
        self.color_adj_widget = None
        self._init_color_adj(0)
        self.colorManager.clicked.connect(self.color_param_show)

        self.img = None  # 用BGR来存储,用opencv的默认方式存储（BGR）
        self.paths = []  # 当打开文件夹的时候，保存该文件夹下所有的文件名字
        self.path = ""  # 当前正在处理的文件
        self.add = False  # 添加mask标记
        self.remove = False  # 删除mask标记
        self.index = 0


        # 按钮连接
        # 设置按键连接，当点击的时候，设置为添加区域
        self.add_area.clicked.connect(self.on_add_area)
        self.del_area.clicked.connect(self.on_del_area)
        self.save_file.clicked.connect(self.on_save_file)
        self.auto_threshold_seg.clicked.connect(lambda: self.signal_calculate_mask.emit())
        self.slider_squre_size.valueChanged.connect(self.on_slider_squre_size)
        self.next_pic.clicked.connect(self.on_next_pic)
        self.pre_pic.clicked.connect(self.on_pre_pic)
        self.next_ten.clicked.connect(self.on_next_ten)

        self.increased_transparency.clicked.connect(self.handler_increased_transparency)
        self.decreased_transparency.clicked.connect(self.handler_decreased_transparency)
        # 信号连接
        self.color_adj_widget._signal_para_change.connect(self.canshu_change)  # 当全局参数发生变化的时候

        self.signal_file_change.connect(self.handler_file_change)  # 当文件发生改变的时候，
        self.signal_calculate_mask.connect(self.handler_calculate_mask)  # 按键连接主要用于计算

        self.signal_cal_percentage.connect(self.handler_cal_percentage)
        # 连接当mask发生变化时
        self.pic_show.signal_mask_change.connect(self.handler_mask_change)

        self.plusPressed.connect(self.handler_increased_transparency)
        self.minusPressed.connect(self.handler_decreased_transparency)

        # 连接配置
        # 创建一个QAction
        open_single_file = QAction("打开文件", self)
        open_single_file.triggered.connect(self.open_single_file)

        open_mul_file = QAction("打开文件夹", self)
        open_mul_file.triggered.connect(self.open_mul_file)

        # 将QAction添加到菜单栏
        file_menu = self.menuBar.addMenu("文件")
        file_menu.addAction(open_single_file)
        file_menu.addAction(open_mul_file)

        #self.test()

    def _init_color_adj(self, type):
        param = self.return_re_param(type)
        self.color_adj_widget = Color_adj(param)
        self.color_adj_widget.setVisible(False)
        self.color_adj_widget.value2page()

    def return_re_param(self, type):
        color_param = Canshu()
        if type == 0:
            # 蓝色的标准配置
            color_param.h_min = 90
            color_param.h_max = 120
            color_param.con_thread = 30
            color_param.ostu_thread = 50
            return color_param
        if type == 1:
            # 红色的标准配置
            color_param.h_min = 90
            color_param.h_max = 120
            color_param.con_thread = 30
            color_param.ostu_thread = 50
            return color_param

    def test(self):
        self.color_adj_widget.param.h_min = 90
        self.color_adj_widget.param.h_max = 120
        self.color_adj_widget.param.con_thread = 30
        self.color_adj_widget.param.ostu_thread = 50
        # test用的，平时关闭

        # self.paths = All.get_all_files("D:\\0\shujuji\\bp_0524")
        self.paths = All.get_all_files("D:\\0\shujuji\\bp_0524")
        self.signal_file_change.emit(self.paths[0])
        # self.signal_calculate_mask.emit()

    def open_single_file(self):
        # 打开文件对话框
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        if file_dialog.exec_() == QFileDialog.Accepted:
            # 获取所选文件的路径
            file_path = file_dialog.selectedFiles()[0]
            self.path = file_path
            self.signal_file_change.emit(self.path)

    def open_mul_file(self):
        folder_dialog = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_dialog:
            self.paths = All.get_all_files(folder_dialog)
            self.signal_file_change.emit(self.paths[0])

    def color_param_show(self):
        self.color_adj_widget.show()

    # 这个功能是让子页面的数据能够传输到我主页面
    def canshu_change(self):
        # 参数传来以后，我需要让重新计算
        self.signal_calculate_mask.emit()

    # def get_file_name(self, path):
    #     return os.path.basename(path)

    def handler_file_change(self, path):
        self.file_name.setText(os.path.basename(path))
        self.path = path
        # 1.把界面的文字修改
        # 2.显示的图像重置了
        self.img = All.open_image_file(path)
        # c30_1_mask.jpg
        if self.img is None:
            # 创建一个 QMessageBox 对象
            msg_box = QMessageBox()

            # 设置提示框的标题和内容
            msg_box.setWindowTitle("提示")
            msg_box.setText("选择的文件夹有误")

            # 设置提示框的图标
            msg_box.setIcon(QMessageBox.Warning)

            # 显示提示框
            msg_box.exec()
        mask = All.open_mask_with_name(path)
        if mask is not None:
            self.pic_show.mask = mask
            img = self.pic_show.overlay_mask_on_image(self.img, self.pic_show.mask)
            self.pic_show.imshow(img)
            return
        self.pic_show.imshow(self.img)
        # 显示的mask应该清零

    def handler_mask_change(self):
        image = self.pic_show.overlay_mask_on_image(self.img, self.pic_show.mask)

        self.pic_show.imshow(image)
        self.signal_cal_percentage.emit()

    def handler_calculate_mask(self):

        mask = All.calculate_mask(self.img, self.color_adj_widget.param.h_min, self.color_adj_widget.param.h_max,
                                  self.color_adj_widget.param.con_thread,
                                  self.color_adj_widget.param.ostu_thread,
                                  self.color_adj_widget.fill_bool)
        self.pic_show.mask = mask
        image = self.pic_show.overlay_mask_on_image(self.img, mask)

        self.pic_show.imshow(image)
        self.signal_cal_percentage.emit()

    def on_add_area(self):
        self.pic_show.clear_items()
        if self.pic_show.state.value == DorA.Add.value:
            self.pic_show.state = DorA.Wu
            self.add_area.setStyleSheet("background-color: white")
            return
        if self.pic_show.state.value == DorA.Wu.value:
            self.pic_show.state = DorA.Add
            self.add_area.setStyleSheet("background-color: red")
            return
        if self.pic_show.state.value == DorA.Del.value:
            self.pic_show.state = DorA.Add
            self.add_area.setStyleSheet("background-color: red")
            self.del_area.setStyleSheet("background-color: white")
            self.pic_show.clear_items()
            return

    def on_del_area(self):
        self.pic_show.clear_items()
        if self.pic_show.state.value == DorA.Add.value:
            self.pic_show.state = DorA.Del
            self.add_area.setStyleSheet("background-color: white")
            self.del_area.setStyleSheet("background-color: red")
            self.pic_show.clear_items()
            return
        if self.pic_show.state.value == DorA.Wu.value:
            self.pic_show.state = DorA.Del
            self.del_area.setStyleSheet("background-color: red")
            return
        if self.pic_show.state.value == DorA.Del.value:
            self.pic_show.state = DorA.Wu
            self.del_area.setStyleSheet("background-color: white")
            return

            #
        # if self.add == True:
        #     self.pic_show.clear_items()
        # self.pic_show.add = False

    def on_slider_squre_size(self):
        self.pic_show.brush_size = self.slider_squre_size.value()

    def on_next_pic(self):
        # 最大为5  index最大为4
        size = len(self.paths)
        if size == 0:
            return
        elif self.index >= size - 1:
            return
        else:
            self.index = self.index + 1
        self.path = self.paths[self.index]
        self.signal_file_change.emit(self.path)

    def on_pre_pic(self):
        # 最大为5  index最大为4
        size = len(self.paths)
        if size == 0:
            return
        elif self.index < 0:
            return
        else:
            self.index = self.index - 1
        self.path = self.paths[self.index]
        self.signal_file_change.emit(self.path)

    def handler_cal_percentage(self):
        mask = self.pic_show.mask
        counts = np.count_nonzero(mask)

        tot_pixel = self.img.size / 3
        percentage = round(counts * 100 / tot_pixel, 2)
        sentence = str(percentage) + "%"
        self.show_area.setText(sentence)

    def on_save_file(self):
        name = self.path
        file_name = os.path.splitext(os.path.basename(name))[0]
        print("文件名:", file_name)

        # 获取文件路径
        directory = os.path.dirname(name)
        print("文件路径:", directory)
        save_path = directory + "\\" + file_name + "_mask.png"
        # All.imshow("1",self.pic_show.mask)

        try:
            # 尝试打开图像文件
            cv2.imwrite(save_path, self.pic_show.mask)
            print("Error: Invalid image file.")
        except Exception as e:
            # 路径错误或其他异常
            print("Error:", str(e))

    def handler_increased_transparency(self):
        self.pic_show.transparency = self.pic_show.transparency - 0.4
        if self.pic_show.transparency <= 0:
            self.pic_show.transparency = 0
        self.pic_show.signal_mask_change.emit()

    def handler_decreased_transparency(self):
        self.pic_show.transparency = self.pic_show.transparency + 0.4
        if self.pic_show.transparency >= 1:
            self.pic_show.transparency = 1
        self.pic_show.signal_mask_change.emit()

    def keyPressEvent(self, event):
        # 检查按下的键是否为 "+" 键
        if event.key() == Qt.Key_Plus or event.key() == Qt.Key_BraceRight:
            self.plusPressed.emit()

        # 检查按下的键是否为 "-" 键
        if event.key() == Qt.Key_Minus or event.key() == Qt.Key_BraceLeft:
            self.minusPressed.emit()
        if event.key() == Qt.Key_A:
            self.pic_show.brush_size += 10
        elif event.key() == Qt.Key_S:
            if self.pic_show.brush_size > 10:
                self.pic_show.brush_size -= 10
            else:
                self.pic_show.brush_size =5

        # Q功能是保证图片闪烁
        if event.key() == Qt.Key_Q:
            self.bool_flash = True
            self.fun_a()
        if event.key() == Qt.Key_W:
            self.bool_flash = False
        # if event.key() == Qt.Key_Z:
        #     self.on_add_area()
        # if event.key() == Qt.Key_X:
        #     self.on_del_area()

        # 调用父类的 keyPressEvent() 方法
        super().keyPressEvent(event)

    def fun_a(self):
        if self.bool_flash:
            self.minusPressed.emit()
            self.minusPressed.emit()
            QTimer.singleShot(500, self.fun_b)
    def fun_b(self):
        if self.bool_flash:
            self.plusPressed.emit()
            self.plusPressed.emit()
            QTimer.singleShot(500, self.fun_a)

    def on_next_ten(self):
        # 最大为5  index最大为4
        size = len(self.paths)
        if size == 0:
            return
        elif self.index >= size - 10:
            return
        else:
            self.index = self.index + 10
        self.path = self.paths[self.index]
        self.signal_file_change.emit(self.path)
