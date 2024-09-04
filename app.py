import os
import sys
import time
from datetime import datetime, timedelta

import cv2
import keyboard
import numpy as np
import pyautogui
from PIL import ImageFile
from PyQt6 import QtCore, QtWidgets
# from PyQt6 import uic
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtGui import QFont, QPainter, QBrush, QColor, QPen, QFontDatabase
from PyQt6.QtWidgets import QPushButton, QLabel, QApplication

from design_app import Ui_Form
from license import License


def resource_path(relative_path) -> str:
    # Получаем абсолютный путь к ресурсам.
    try:
        # PyInstaller создает временную папку в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class MainWindow(QtWidgets.QWidget, Ui_Form):
    # class MainWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # uic.loadUi("app.ui", self)

        self.license = License(resource_path('rageraid.dll'))

        self.thread = None
        self.meth = None
        self.auto_shift = False
        self.auto_run = False

        self.set_font()

        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.top_panel()
        # self.resizede()

        self.over_windows = False

        self.set_btns()

        self.auto_shift_key, self.auto_run_key = None, None

        self.load_settings()

    def set_font(self) -> QFont:
        for title in ['FeatureMono-Bold.ttf', 'FeatureMono-Hairline.ttf', 'FeatureMono-Light.ttf',
                      'FeatureMono-Medium.ttf', 'FeatureMono-Regular.ttf', 'FeatureMono-Thin.ttf']:
            font_path = resource_path(f'fonts/{title}')
            QFontDatabase.addApplicationFont(font_path)

    def load_settings(self):
        settings = QtCore.QSettings(resource_path("settings.ini"), QtCore.QSettings.Format.IniFormat)

        self.over_windows_btn.setChecked(
            True if settings.value('over_windows', 'false') == 'true' else False)
        if self.over_windows_btn.isChecked(): self.set_over_windows()

        match settings.value("type", None):
            case 'building':
                self.building_btn.setChecked(True)
            case "mine":
                self.mine_btn.setChecked(True)
            case "port":
                self.port_btn.setChecked(True)

        self.auto_run_btn.setChecked(
            True if settings.value('auto_run', 'false') == 'true' else False)
        self.auto_run = self.auto_run_btn.isChecked()
        self.auto_shift_btn.setChecked(
            True if settings.value('auto_shift', 'false') == 'true' else False)
        self.auto_shift = self.auto_shift_btn.isChecked()

        self.auto_shift_key = settings.value('auto_shift_key', 'shift')
        self.auto_run_key = settings.value('auto_run_key', 'w')

    def save_settings(self):
        settings = QtCore.QSettings(resource_path("settings.ini"), QtCore.QSettings.Format.IniFormat)

        settings.setValue("over_windows", self.over_windows_btn.isChecked())

        if self.building_btn.isChecked():
            settings.setValue("type", "building")
        elif self.port_btn.isChecked():
            settings.setValue("type", "port")
        elif self.mine_btn.isChecked():
            settings.setValue("type", "mine")

        settings.setValue("auto_shift", self.auto_shift_btn.isChecked())
        settings.setValue("auto_run", self.auto_run_btn.isChecked())

    def closeEvent(self, event):
        keyboard.release(self.auto_run_key)
        keyboard.release(self.auto_shift_key)

        self.save_settings()
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

    def top_panel(self):
        self.hide = QPushButton("─")
        self.hide.setStyleSheet('background-color:#18171c')
        self.hide.setFont(QFont('Feature Mono Thin', 10))
        self.hide.clicked.connect(lambda x: self.showMinimized())

        self.exit = QPushButton("✕")
        self.exit.setStyleSheet('background-color:#18171c')
        self.exit.setFont(QFont('Feature Mono Thin', 10))
        self.exit.clicked.connect(lambda x: self.close())

        self.flex = QLabel("RAGERAID")
        self.flex.setStyleSheet('background-color:#18171c;padding:3px')
        self.flex.setFont(QFont('Feature Mono Thin', 10))

        self.pn.addWidget(self.flex)
        self.pn.addStretch()
        self.pn.addWidget(self.hide)
        self.pn.addWidget(self.exit)

        self.panel.addLayout(self.pn)
        self.panel.addStretch()

    # def resizede(self):
    #     self.gripSize = 16
    #     self.grips = []
    #     for i in range(2):
    #         grip = QSizeGrip(self)
    #         grip.resize(self.gripSize, self.gripSize)
    #         self.grips.append(grip)
    #
    # def resizeEvent(self, event):
    #     self.move(self.pos())
    #     QWidget.resizeEvent(self, event)
    #     rect = self.rect()
    #     # self.grips.pop(self.grips[1])
    #     self.grips[0].move(rect.right() - self.gripSize, rect.bottom() - self.gripSize)
    #     self.grips[1].move(0, rect.bottom() - self.gripSize)

    def set_btns(self):
        self.over_windows_btn.clicked.connect(self.set_over_windows)

        self.auto_shift_btn.clicked.connect(self.set_auto_shift)
        self.auto_run_btn.clicked.connect(self.set_auto_run)

        self.run_btn.clicked.connect(self.run)

        self.settings_btn.clicked.connect(self.set_settings)

        self.port_btn.clicked.connect(self.set_type)
        self.mine_btn.clicked.connect(self.set_type)
        self.building_btn.clicked.connect(self.set_type)

        self.set_radio()

    def set_type(self):
        settings = QtCore.QSettings(resource_path("settings.ini"), QtCore.QSettings.Format.IniFormat)

        match QApplication.instance().sender().text():
            case "Порт":
                settings.setValue("type", 'port')
            case "Стройка":
                settings.setValue("type", 'building')
            case 'Шахта':
                settings.setValue("type", 'mine')

    def set_settings(self):
        from setting_app import SettingWindow
        self.child = SettingWindow(parent=self)
        self.setWindowOpacity(0)
        self.child.show()

    def set_auto_shift(self):
        self.auto_shift = self.auto_shift_btn.isChecked()

        if self.auto_shift: self.auto_run_btn.setChecked(False)
        self.auto_run = self.auto_run_btn.isChecked()

        settings = QtCore.QSettings(resource_path("settings.ini"), QtCore.QSettings.Format.IniFormat)
        settings.setValue("auto_shift", self.auto_shift_btn.isChecked())
        settings.setValue("auto_run", self.auto_run_btn.isChecked())

    def set_auto_run(self):
        self.auto_run = self.auto_run_btn.isChecked()

        if self.auto_run: self.auto_shift_btn.setChecked(False)
        self.auto_shift = self.auto_shift_btn.isChecked()

        settings = QtCore.QSettings(resource_path("settings.ini"), QtCore.QSettings.Format.IniFormat)
        settings.setValue("auto_shift", self.auto_shift_btn.isChecked())
        settings.setValue("auto_run", self.auto_run_btn.isChecked())

    def set_radio(self):
        group_type = QtWidgets.QButtonGroup(self)
        group_type.addButton(self.mine_btn)
        group_type.addButton(self.port_btn)
        group_type.addButton(self.building_btn)

    def set_over_windows(self):
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, self.over_windows_btn.isChecked())
        self.show()

    def run(self):
        if self.run_btn.text() == 'Запустить':
            if not self.license.check_file():
                self.close()
                return

            if any([self.port_btn.isChecked(), self.mine_btn.isChecked(), self.building_btn.isChecked()]):
                self.run_btn.setText('Отключить')

                self.mine_btn.setEnabled(False)
                self.port_btn.setEnabled(False)
                self.building_btn.setEnabled(False)
                self.auto_shift_btn.setEnabled(False)
                self.auto_run_btn.setEnabled(False)
                self.settings_btn.setEnabled(False)

                self.thread = Starty()
                self.thread.updateSignal.connect(self.update_thread)
                self.thread.set_data(self)
                self.thread.start()
        else:
            self.run_btn.setText('Запустить')

            self.mine_btn.setEnabled(True)
            self.port_btn.setEnabled(True)
            self.building_btn.setEnabled(True)
            self.auto_shift_btn.setEnabled(True)
            self.auto_run_btn.setEnabled(True)
            self.settings_btn.setEnabled(True)

            self.thread.thread_key.terminate()
            self.thread.terminate()

            self.label.setText('RAGERAID')
            self.label.repaint()

    def update_thread(self, text):
        self.label.setText(text)
        self.label.repaint()


class Keyb(QThread):
    def run(self):
        ...

    def press_key(self, key):
        keyboard.press(key)

    def release_key(self, key):
        keyboard.release(key)


class Starty(QThread):
    updateSignal = QtCore.pyqtSignal(str)
    thread_key = Keyb()
    thread_key.start()
    key_build = None

    def active_window(self):
        import psutil
        import ctypes
        from ctypes import wintypes

        pid = wintypes.DWORD()
        active = ctypes.windll.user32.GetForegroundWindow()
        active_window = ctypes.windll.user32.GetWindowThreadProcessId(active, ctypes.byref(pid))

        pid = pid.value
        for item in psutil.process_iter():
            if pid == item.pid:
                return item.name()

    def screenshot(self, window_title, region: tuple[int, int, int, int]):
        if self.active_window() == window_title:
            im = pyautogui.screenshot(region=region)
            return im

    def set_data(self, parent):
        self.parent = parent

    def rec_image(self, image_path: str, screen_path: ImageFile, precision=0.9):
        img_rgb = np.array(screen_path)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(resource_path(image_path), 0)

        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val < precision:
            return False
        return True

    def run(self):
        count_plus = [datetime.now(), 0]
        count_emz = [datetime.now(), 0]
        while True:
            if self.parent.license.get_data():
                break
            if self.parent.license.check_license():
                break

            if self.active_window() == 'GTA5.exe':

                if count_plus[1]:
                    # self.updateSignal.emit(f'RAGERAID <span style="color: green;">[{count_plus}]</span>')
                    self.updateSignal.emit(
                        f'RAGERAID <span style="color: #01FF1E;">{count_plus[1]}'
                        f"""{f'</span><spam style="color: #00F4FF;">+{count_emz[1]}</span>' if count_emz[1] else ''}"""
                    )
                elif self.parent.label.text() != 'RAGERAID <span style="color: #01FF1E;">✓</span>':
                    self.updateSignal.emit('RAGERAID <span style="color: #01FF1E;">✓</span>')

                if self.parent.auto_run:
                    self.thread_key.press_key(self.parent.auto_run_key)
                    self.thread_key.press_key(self.parent.auto_shift_key)
                elif self.parent.auto_shift:
                    self.thread_key.press_key(self.parent.auto_shift_key)

                if self.parent.port_btn.isChecked():
                    image = self.screenshot('GTA5.exe', (895, 490, 1024, 491))
                    px = image.load()
                    if px[5, 0] == (126, 211, 33) or px[123, 0] == (126, 211, 33):
                        self.updateSignal.emit('RAGERAID <span style="color: #01FF1E;">+</span>')
                        self.thread_key.press_key('e')
                        time.sleep(0.2)
                        self.thread_key.release_key('e')

                    image_plus = self.screenshot('GTA5.exe', (666, 1020, 667, 1021)).load()

                    if image_plus[0, 0] == (0, 242, 255) and datetime.now() - count_emz[0] > timedelta(seconds=15):
                        count_emz[0] = datetime.now()
                        count_emz[1] += 1
                    if image_plus[0, 0] == (143, 245, 9) and datetime.now() - count_plus[0] > timedelta(seconds=8):
                        count_plus[0] = datetime.now()
                        count_plus[1] += 1
                        self.updateSignal.emit(
                            f'RAGERAID <span style="color: #01FF1E;">{count_plus[1]}'
                            f"""{f'</span><spam style="color: #00F4FF;">+{count_emz[1]}</span>' if count_emz[1] else ''}"""
                        )
                    elif image_plus[0, 0] == (150, 0, 78):
                        self.updateSignal.emit(f'RAGERAID <span style="color: #FF3300;">-</span>')
                        time.sleep(0.5)
                        self.updateSignal.emit(
                            f'RAGERAID <span style="color: #01FF1E;">{count_plus[1]}'
                            f"""{f'</span><spam style="color: #00F4FF;">+{count_emz[1]}</span>' if count_emz[1] else ''}"""
                        )
                elif self.parent.mine_btn.isChecked():
                    image = self.screenshot('GTA5.exe', (862, 495, 960, 496)).load()
                    if image[97, 0] == (126, 211, 33):
                        keyboard.send('e')
                elif self.parent.building_btn.isChecked():
                    image = self.screenshot('GTA5.exe', (761, 495, 1, 1)).load()
                    if image[0, 0] == (126, 211, 33):
                        img_key = self.screenshot('GTA5.exe', (949, 557, 23, 27))
                        if self.rec_image('e.png', img_key):
                            keyboard.send('e')
                        elif self.rec_image('f.png', img_key):
                            keyboard.send('f')
                        elif self.rec_image('y.png', img_key):
                            keyboard.send('y')

                    image_plus = self.screenshot('GTA5.exe', (666, 1020, 667, 1021)).load()

                    if image_plus[0, 0] == (143, 245, 9) and datetime.now() - count_plus[0] > timedelta(seconds=8):
                        count_plus[0] = datetime.now()
                        count_plus[1] += 1
                        self.updateSignal.emit(f'RAGERAID <span style="color: #01FF1E;">{count_plus[1]}</span>')
            else:
                if self.parent.label.text() != 'RAGERAID <span style="color: #FF3300;">×</span>':
                    self.updateSignal.emit('RAGERAID <span style="color: #FF3300;">×</span>')
                time.sleep(1)

        self.thread_key.release_key(self.auto_run_key)
        self.thread_key.release_key(self.auto_shift_key)
        self.thread_key.terminate()
        self.terminate()


def main():
    try:
        import subprocess
        subprocess.check_call(["attrib", "+H", "_internal"])
    except Exception: ...

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
