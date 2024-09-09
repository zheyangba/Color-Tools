from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QColorDialog

from Common import Canshu
from interface_design.coloradjust import Ui_ColorAdjustClass


# 在OpenCV中，HSV颜色空间中的H值的取值范围是[0, 180]，S和V的取值范围是[0, 255]。
class Color_adj(QDialog, Ui_ColorAdjustClass):
    _signal_para_change = QtCore.pyqtSignal()

    def __init__(self, param):
        super(Color_adj, self).__init__()
        self.setupUi(self)

        self.param: Canshu = param  # 类型参数
        self.fill_bool = False
        # 为了避免触发信号，我在这里就设置页面数值
        self.pick_color.clicked.connect(self.on_button_pick_color)
        self.is_fill.stateChanged.connect(self.handler_is_fill)
        self.connect_obj()
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    def handler_is_fill(self):
        self.fill_bool = self.is_fill.checkState()

    def connect_obj(self):
        self.slider_h_low.sliderReleased.connect(self.page2value)
        self.slider_h_high.sliderReleased.connect(self.page2value)
        self.slider_ostu_thread.sliderReleased.connect(self.page2value)
        self.slider_con_thread.sliderReleased.connect(self.page2value)

    def on_button_pick_color(self):
        color_dialog = QColorDialog()
        color_dialog.setOption(QColorDialog.ShowAlphaChannel)  # 可选：显示透明度通道
        if color_dialog.exec_():
            color = color_dialog.currentColor()
            hsv = color.toHsv()
            # print("Selected HSV:", hsv.hue(), hsv.saturation(), hsv.value())
            h = hsv.hue()
            h = h / 2
            if h * 1.3 > 180:
                h_max = 180
            else:
                h_max = h * 1.3

            h_min = h * 0.7

            self.param.h_max = int(h_max)
            self.param.h_min = int(h_min)
            self.value2page()
            # 第一個事，修改主界面中的
            self._signal_para_change.emit()

    def value2page(self):
        self.slider_h_low.setValue(self.param.h_min)
        self.slider_h_high.setValue(self.param.h_max)
        self.slider_ostu_thread.setValue(self.param.ostu_thread)
        self.slider_con_thread.setValue(self.param.con_thread)


        self.H_low.setText(str(self.param.h_min))
        self.H_high.setText(str(self.param.h_max))
        self.ostu_thread.setText(str(self.param.ostu_thread))
        self.con_thread.setText(str(self.param.con_thread))
    def page2value(self):
        h_min = self.slider_h_low.value()
        h_max = self.slider_h_high.value()
        if h_min>=h_max:
            # 这里表示的是你拖拽错误，我不需要进行更改
            self.slider_h_low.setValue(self.param.h_min)
            self.slider_h_high.setValue(self.param.h_max)
            return
        else:
            self.param.h_min = self.slider_h_low.value()
            self.param.h_max = self.slider_h_high.value()
            self.param.ostu_thread = self.slider_ostu_thread.value()
            self.param.con_thread = self.slider_con_thread.value()

            self.H_low.setText(str(self.param.h_min))
            self.H_high.setText(str(self.param.h_max))
            self.ostu_thread.setText(str(self.param.ostu_thread))
            self.con_thread.setText(str(self.param.con_thread))
        self._signal_para_change.emit()
