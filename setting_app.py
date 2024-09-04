import os
import sys

from PyQt6 import QtCore, QtWidgets
# from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QBrush, QColor, QPen

from design_setting import Ui_Form


def resource_path(relative_path) -> str:
    # Получаем абсолютный путь к ресурсам.
    try:
        # PyInstaller создает временную папку в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class SettingWindow(QtWidgets.QWidget, Ui_Form):
    # class MainWindow(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        # uic.loadUi("app.ui", self)

        self.thread = None
        self.meth = None
        self.auto_shift = False
        self.auto_run = False

        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        # self.over_windows = False

        self.set_btns()

        self.load_settings()

    def load_settings(self):
        settings = QtCore.QSettings(resource_path("settings.ini"), QtCore.QSettings.Format.IniFormat)

        self.secret_key_input.setText(settings.value('secret_key', ''))
        self.auto_shift_key_btn.setText(settings.value('auto_shift_key', 'shift'))
        self.auto_run_key_btn.setText(settings.value('auto_run_key', 'w'))

    def save_settings(self):
        settings = QtCore.QSettings(resource_path("settings.ini"), QtCore.QSettings.Format.IniFormat)

        settings.setValue("secret_key", self.secret_key_input.text())
        settings.setValue("auto_shift_key", self.auto_shift_key_btn.text())
        settings.setValue("auto_run_key", self.auto_run_key_btn.text())

        if not self.parent.license.decode_secret(self.secret_key_input.text()):
            self.parent.license.create_file()
            self.parent.license.get_data()

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
        self.auto_shift_key_btn.clicked.connect(self.auto_shift_key)
        self.auto_run_key_btn.clicked.connect(self.auto_run_key)
        self.save_btn.clicked.connect(self.save)
        self.cancel_btn.clicked.connect(lambda: self.close())

    def save(self):
        self.save_settings()
        self.close()

    def auto_shift_key(self):
        from press_app import PressWindow
        self.win = PressWindow(type_key='auto_shift_key', parent=self)
        self.setWindowOpacity(0)
        self.win.show()

    def auto_run_key(self):
        from press_app import PressWindow
        self.window = PressWindow(type_key='auto_run_key', parent=self)
        self.setWindowOpacity(0)
        self.window.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = SettingWindow()
    window.show()
    app.exec()
