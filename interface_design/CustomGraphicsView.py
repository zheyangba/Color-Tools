from enum import Enum

import cv2
import numpy as np
from PyQt5 import QtCore
from PyQt5.Qt import Qt  # 导入Qt对象
from PyQt5.QtCore import QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QPixmap, QWheelEvent, QImage, QPen, QBrush
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem

# 这是干嘛的？我一点印象都没得呢
class React:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

# 当前掩码的编辑状态，分为三种，Wu表示什么都不做，Add表示对将鼠标经过的节点添加进掩码，Del表示将鼠标经过的节点都删除
class DorA(Enum):
    Wu = 0
    Add = 1
    Del = 2


class CustomGraphicsView(QGraphicsView):
    # 当掩码发生改变的时候，发送的信号
    signal_mask_change = pyqtSignal()

    def __init__(self, editor):
        super(CustomGraphicsView, self).__init__()

        # self.editor = editor
        # 这里面很多的功能都可以忽略掉，因为我也不知道他是干嘛的
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setRenderHint(QPainter.TextAntialiasing)

        self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing, True)
        self.setOptimizationFlag(QGraphicsView.DontSavePainterState, True)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setInteractive(True)
        # 参数设置完毕

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.transparency = 0.5
        # 用来保存当前处理的图像
        self.image_item = None

        # 自己的mask属性
        self.mask = None

        # 鼠标移动相关属性
        self.setMouseTracking(True)

        # 这个是什么我也不知道
        self.pre_mask = None
        self.points = []
        self.erase_mode = False
        self.move_counter = 0
        self.move_threshold = 5  # 降低鼠标移动事件的灵敏度
        # 当前图像的状态是不修改。
        self.state = DorA.Wu

        # self.remove = False
        # self.add =False

        self.brush_size = 50

    def set_image(self, q_img):
        pixmap = QPixmap.fromImage(q_img)
        if self.image_item:
            self.image_item.setPixmap(pixmap)
        else:
            self.image_item = self.scene.addPixmap(pixmap)
            self.setSceneRect(QRectF(pixmap.rect()))

    def wheelEvent(self, event: QWheelEvent):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        old_pos = self.mapToScene(event.pos())
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        self.scale(zoom_factor, zoom_factor)
        new_pos = self.mapToScene(event.pos())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

    # 函数功能，将opencv返回的
    def imshow(self, img):
        height, width, channel = img.shape
        bytes_per_line = 3 * width
        q_img = QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        self.set_image(q_img)

    # 这个函数的功能只是把掩膜和图像融合，并且把融合成为的图像进行展示
    def overlay_mask_on_image(self, image, mask, color=(0, 255, 0)):
        # gray_mask = mask.astype(np.uint8) * 255
        gray_mask = mask
        gray_mask = cv2.merge([gray_mask, gray_mask, gray_mask])
        color_mask = cv2.bitwise_and(gray_mask, color)
        masked_image = cv2.bitwise_and(image.copy(), color_mask)
        overlay_on_masked_image = cv2.addWeighted(
            masked_image, self.transparency, color_mask, 1 - self.transparency, 0
        )
        background = cv2.bitwise_and(image.copy(), cv2.bitwise_not(color_mask))
        image = cv2.add(background, overlay_on_masked_image)
        return image

    """新版本,这个版本能够实现扫过的时候对颜色展示，但是问题是，我没有对掩膜进行一个收集"""



    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:  # 检查是否是鼠标右键按下
            self.setInteractive(False)  # 关闭交互，禁止绘图操作
            self.setDragMode(QGraphicsView.ScrollHandDrag)  # 切换为滚动拖动模式
            self.dragStartPosition = event.pos()  # 记录鼠标按下的初始位置

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.RightButton:  # 检查是否是鼠标右键拖动
            delta = event.pos() - self.dragStartPosition  # 计算鼠标移动的距离
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())  # 水平滚动条移动
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())  # 垂直滚动条移动
            self.dragStartPosition = event.pos()  # 更新初始位置

        if event.buttons() & Qt.LeftButton:
            if self.state is DorA.Wu:
                super().mouseMoveEvent(event)
                return
            self.move_counter += 1
            if self.move_counter >= self.move_threshold:
                pos = self.mapToScene(event.pos())
                self.draw_front(pos)
                self.move_counter = 0

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pre_mask = self.mask.copy()
            self.save_to_mask()
            # All.imshow("tete",self.mask)
        if event.button() == Qt.RightButton:
            self.setInteractive(True)  # 恢复交互，允许绘图操作
            self.setDragMode(QGraphicsView.NoDrag)  # 切换为无拖动模式

        super().mouseReleaseEvent(event)
        # center_coordinates = []
        # for item in self.scene.items():
        #     item_center = item.sceneBoundingRect().center()
        #     item_center_pos = item.mapToScene(item_center)
        #     center_coordinates.append((item_center_pos.x(), item_center_pos.y()))
        #
        # for i in center_coordinates:
        #     print(i)
        # super().mouseMoveEvent(event)
        # self.traverse_pixels()

    def save_to_mask(self):
        if self.state.value == DorA.Wu.value:
            return
        # self.calculate()
        pixel_positions = self.get_rect_pixel_positions()
        pixel_positions = list(set(pixel_positions))
        height = 1920
        width = 2560
        blank_image = np.zeros((height, width), dtype=np.uint8)
        """real代码"""
        for (x, y) in pixel_positions:
            if y > 1919 or x > 2559:
                continue
            blank_image[y, x] = 255
        # """测试代码"""
        # for x in range(100,1800):
        #     for y in range(200,1800):
        #         blank_image[x, y] = 255
        if self.state.value == DorA.Add.value:
            masked_image = cv2.bitwise_or(self.mask, blank_image)
        if self.state.value == DorA.Del.value:
            mask2_inv = cv2.bitwise_not(blank_image)

            # 掩码1扣去掩码2的区域
            masked_image = cv2.bitwise_and(self.mask, mask2_inv)

        # masked_image = cv2.bitwise_not(self.mask, blank_image)

        # merged_image = cv2.merge([self.mask, blank_image])
        self.mask = masked_image.copy()

        self.signal_mask_change.emit()
        # 清除所有的item，

        self.clear_items()

        self.points.clear()

    # def highlight_area(self, position):
    #     rect = self.scene.addRect(position.x(), position.y(),  self.brush_size,  self.brush_size)
    #     pen = QPen(Qt.red)
    #     brush = QBrush(Qt.red)
    #     rect.setPen(pen)
    #     rect.setBrush(brush)
    #     self.points.append(React(position.x(), position.y(),  self.brush_size,  self.brush_size))

    def draw_front(self, position):
        size = self.brush_size / 2
        if (position.x() - size) < 0:
            x = 0
        else:
            x = position.x() - size

        if (position.y() - size) < 0:
            y = 0
        else:
            y = position.y() - size
        rect = self.scene.addRect(x, y, self.brush_size, self.brush_size)
        if self.state.value == DorA.Add.value:
            pen = QPen(Qt.red)
            brush = QBrush(Qt.red)
        if self.state.value == DorA.Del.value:
            pen = QPen(Qt.black)
            brush = QBrush(Qt.black)
        rect.setPen(pen)
        rect.setBrush(brush)
        self.points.append(React(x, y, self.brush_size, self.brush_size))
        # test

    # def erase_area(self, position):
    #     items = self.scene.items(position.x() - 2, position.y() - 2, 5, 5, Qt.IntersectsItemShape)
    #     for item in items:
    #         self.scene.removeItem(item)

    """"""

    # def calculate(self):
    #     image = QImage(2560, 1920, QImage.Format_ARGB32)
    #     image.fill(Qt.white)  # 使用白色填充图像
    #
    #     painter = QPainter(image)
    #     for item in self.scene.items():
    #         if isinstance(item, QGraphicsRectItem):
    #             # item.mapToScene()
    #             rect = item.boundingRect().toRect()
    #             painter.fillRect(rect, QColor(Qt.black))
    #     image.save("./test.png")
    #     black_pixel_positions = self.get_black_pixel_positions(image)

    def get_rect_pixel_positions(self):
        rect_pixel_positions = []
        for react in self.points:

            # 计算矩形的像素位置
            x = int(react.x)
            y = int(react.y)
            width = int(react.width)
            height = int(react.height)

            # 获取矩形对应的像素点位置
            for px in range(x, x + width):
                for py in range(y, y + height):
                    rect_pixel_positions.append((px, py))

        return rect_pixel_positions

    # def traverse_pixels(self):
    #     scene_rect = self.scene.sceneRect()
    #     view_rect = self.viewport().rect()
    #
    #     # 遍历视图中的像素点
    #     for x in range(view_rect.left(), view_rect.right() + 1):
    #         for y in range(view_rect.top(), view_rect.bottom() + 1):
    #             # 将视图坐标映射到场景坐标
    #             scene_pos = self.mapToScene(x, y)
    #
    #             # 判断映射后的场景坐标是否在场景范围内
    #             if scene_rect.contains(scene_pos):
    #                 # 处理像素点的操作
    #
    #                 # 示例：打印像素点的场景坐标和颜色
    #                 pixel_color = self.image.toImage().pixelColor(x, y)
    #                 print(f"Pixel ({scene_pos.x()}, {scene_pos.y()}): {pixel_color}")

    # 返回真实的地址
    def return_pose(self, pos):

        pos_in_item = self.mapToScene(pos) - self.image_item.pos()
        return pos_in_item

    # def get_black_pixel_positions(self, image):
    #     black_pixel_positions = []
    #
    #     for y in range(image.height()):
    #         for x in range(image.width()):
    #             pixel_color = QColor(image.pixel(x, y))
    #             if pixel_color == QColor(Qt.black):
    #                 black_pixel_positions.append((x, y))
    #
    #     return black_pixel_positions

    def clear_items(self):
        for item in self.scene.items():
            if isinstance(item, QGraphicsRectItem):
                self.scene.removeItem(item)

    def revoke(self):
        if self.pre_mask is not None:
            self.mask = self.pre_mask.copy()
            self.pre_mask = None
        # 清除所有的item，

    def keyPressEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Z:
            self.revoke()
            # 检查按下的键是否为 "+" 键

        # 调用父类的 keyPressEvent() 方法
        super().keyPressEvent(event)
