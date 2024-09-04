import os
import sys

import keyboard
from PyQt6 import QtCore, QtWidgets
# from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QBrush, QColor, QPen

from design_press import Ui_Form


def resource_path(relative_path) -> str:
    # Получаем абсолютный путь к ресурсам.
    try:
        # PyInstaller создает временную папку в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class PressWindow(QtWidgets.QWidget, Ui_Form):
    # class MainWindow(QtWidgets.QWidget):

    def __init__(self, type_key, parent):
        super().__init__()
        self.setupUi(self)
        # uic.loadUi("app.ui", self)

        self.type_key = type_key
        self.parent = parent

        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.set_btns()

        self.load_settings()

    def load_settings(self):
        settings = QtCore.QSettings(resource_path("settings.ini"), QtCore.QSettings.Format.IniFormat)

        self.press_btn.setText(settings.value(self.type_key, ''))

    def save_settings(self):
        settings = QtCore.QSettings(resource_path("settings.ini"), QtCore.QSettings.Format.IniFormat)

        settings.setValue(self.type_key, self.press_btn.text())

    def closeEvent(self, event):
        # self.save_settings()
        self.parent.setWindowOpacity(1)
        event.accept()

    # \/рисуем окно\/#
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rounded_rect = self.rect().adjusted(0, 0, 0, 0)
        painter.setBrush(QBrush(QColor("#1e1d23")))
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawRoundedRect(rounded_rect, 15, 15)

    # /\рисуем окно/\

    # вызывается при нажатии кнопки мыши
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.pos()

    # вызывается при отпускании кнопки мыши
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None

    # вызывается всякий раз, когда мышь перемещается
    def mouseMoveEvent(self, event):
        cor = [[range(0, 16), range(self.size().height() - 16, self.size().height())],
               [range(self.size().width() - 16, self.width()),
                range(self.size().height() - 16, self.size().height())]]
        if not any([all([event.pos().x() in _[0], event.pos().y() in _[1]]) for _ in cor]):
            if not self.old_pos:
                return
            delta = event.pos() - self.old_pos
            self.move(self.pos() + delta)

    def set_btns(self):
        self.press_btn.clicked.connect(self.setGrabbing)
        self.save_btn.clicked.connect(self.save)
        self.cancel_btn.clicked.connect(lambda: self.close())

    def save(self):
        match self.type_key:
            case "auto_shift_key":
                self.parent.auto_shift_key_btn.setText(self.press_btn.text())
            case "auto_run_key":
                self.parent.auto_run_key_btn.setText(self.press_btn.text())

        # self.save_settings()
        self.close()

    def keyboardEventReceived(self, event):
        if event.event_type == 'down':
            self.press_btn.setText(event.name)

            self.label.setText('Нажми на кнопку')
            keyboard.unhook(self.hook)

    # тест 1
    def setGrabbing(self):
        self.label.setText('Нажми на клавишу')
        self.hook = keyboard.on_press(self.keyboardEventReceived)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = PressWindow()
    window.show()
    app.exec()
