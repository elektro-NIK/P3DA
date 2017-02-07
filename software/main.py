#!/usr/bin/env python3

import sys
import serial
import untitled_ui
from PyQt5.QtWidgets import *


class MainWin(QMainWindow):
    # noinspection PyArgumentList
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = untitled_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.con = serial.Serial('/dev/ttyUSB0', 38400, timeout=0.1)
        self.ui.spinBox_red.valueChanged.connect(self.test)
        self.ui.spinBox_green.valueChanged.connect(self.test)
        self.ui.spinBox_blue.valueChanged.connect(self.test)

    def test(self):
        r = self.ui.spinBox_red.value()
        g = self.ui.spinBox_green.value()
        b = self.ui.spinBox_blue.value()
        self.con.write(('#S0' + '{:03x}{:03x}{:03x}'.format(r, g, b)).encode())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = MainWin()
    myapp.show()
    sys.exit(app.exec_())
