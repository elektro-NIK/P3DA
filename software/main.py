#!/usr/bin/env python3

import sys
import serial
import serial.tools.list_ports
import mainwindow_ui
from PyQt5.QtWidgets import QMainWindow, QApplication


def gamma(x): return round((x / 255) ** 2.8 * 511)


class Connection:
    def __init__(self, dev=None, baud=9600, timeout=0.1):
        if not dev:
            devs = list(self.devicesonline().keys())
            dev = devs[0] if devs else None
        self.con = self.createconnection(dev, baud, timeout)

    @staticmethod
    def devicesonline():
        coms = serial.tools.list_ports.comports()
        return {i.device: i.description for i in coms[::-1]}

    @staticmethod
    def createconnection(dev, baud, timeout):
        return serial.Serial(port=dev, baudrate=baud, timeout=timeout) if dev else None

    def write(self, msg):
        self.con.write(msg.encode())

    def read(self, size=1):
        return self.con.read(size=size).decode('utf-8')

    def readline(self):
        return self.con.readline().decode('utf-8')

    def close(self):
        self.con.close()
        self.con = None


class MainWin(QMainWindow):
    # noinspection PyArgumentList
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = mainwindow_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.con = Connection(baud=38400)
        if len(self.con.devicesonline()) == 0:
            self.ui.statusbar.showMessage('No serial adapter found!', msecs=3000)
        self.ui.pushButton_last01.clicked.connect(lambda: self.palettebutton(self.ui.pushButton_last01))
        self.ui.pushButton_last02.clicked.connect(lambda: self.palettebutton(self.ui.pushButton_last02))
        self.ui.pushButton_last03.clicked.connect(lambda: self.palettebutton(self.ui.pushButton_last03))
        self.ui.pushButton_last04.clicked.connect(lambda: self.palettebutton(self.ui.pushButton_last04))
        self.ui.pushButton_last05.clicked.connect(lambda: self.palettebutton(self.ui.pushButton_last05))
        self.ui.pushButton_last06.clicked.connect(lambda: self.palettebutton(self.ui.pushButton_last06))
        self.ui.pushButton_last07.clicked.connect(lambda: self.palettebutton(self.ui.pushButton_last07))
        self.ui.pushButton_last08.clicked.connect(lambda: self.palettebutton(self.ui.pushButton_last08))
        self.ui.pushButton_last09.clicked.connect(lambda: self.palettebutton(self.ui.pushButton_last09))
        self.ui.pushButton_last10.clicked.connect(lambda: self.palettebutton(self.ui.pushButton_last10))
        self.ui.pushButton_last11.clicked.connect(lambda: self.palettebutton(self.ui.pushButton_last11))
        self.ui.pushButton_last12.clicked.connect(lambda: self.palettebutton(self.ui.pushButton_last12))
        self.ui.pushButton_last13.clicked.connect(lambda: self.palettebutton(self.ui.pushButton_last13))
        self.ui.pushButton_last14.clicked.connect(lambda: self.palettebutton(self.ui.pushButton_last14))
        self.ui.pushButton_last15.clicked.connect(lambda: self.palettebutton(self.ui.pushButton_last15))
        self.ui.pushButton_last16.clicked.connect(lambda: self.palettebutton(self.ui.pushButton_last16))
        self.ui.pushButton_last17.clicked.connect(lambda: self.palettebutton(self.ui.pushButton_last17))
        self.ui.pushButton_last18.clicked.connect(lambda: self.palettebutton(self.ui.pushButton_last18))
        self.ui.pushButton_last19.clicked.connect(lambda: self.palettebutton(self.ui.pushButton_last19))
        self.ui.pushButton_last20.clicked.connect(lambda: self.palettebutton(self.ui.pushButton_last20))
        self.ui.dial_bright.sliderReleased.connect(self.dialbright)
        self.ui.horizontalSlider_r.valueChanged.connect(self.slidercolor)
        self.ui.horizontalSlider_g.valueChanged.connect(self.slidercolor)
        self.ui.horizontalSlider_b.valueChanged.connect(self.slidercolor)
        # self.updatemainpage()

    def palettebutton(self, button):
        color = button.text()
        r, g, b = self.hex2rgb(color)
        self.ui.horizontalSlider_r.setValue(r)
        self.ui.horizontalSlider_g.setValue(g)
        self.ui.horizontalSlider_b.setValue(b)

    def dialbright(self):
        value = self.ui.dial_bright.value()
        r = self.ui.horizontalSlider_r.value()
        g = self.ui.horizontalSlider_g.value()
        b = self.ui.horizontalSlider_b.value()
        avr = (r+g+b) / 3
        add = value - avr
        if add > 0:
            r += add * (255 - r) / (255 - avr)
            g += add * (255 - g) / (255 - avr)
            b += add * (255 - b) / (255 - avr)
        else:
            r += add * r / avr
            g += add * g / avr
            b += add * b / avr
        self.ui.horizontalSlider_r.setValue(int(r))
        self.ui.horizontalSlider_g.setValue(int(g))
        self.ui.horizontalSlider_b.setValue(int(b))

    def slidercolor(self):
        r = self.ui.horizontalSlider_r.value()
        g = self.ui.horizontalSlider_g.value()
        b = self.ui.horizontalSlider_b.value()
        color = self.rgb2hex(r, g, b)
        bright = int((r + g + b) / 3)
        self.ui.pushButton_color.setText(color)
        self.ui.pushButton_color.setStyleSheet('background-color: {0}'.format(color))
        self.ui.dial_bright.setSliderPosition(bright)
        self.ui.lcdNumber_bright.display(bright)
        for i in range(6):
            self.setcolor(r, g, b, i)

    @staticmethod
    def hex2rgb(color):
        return int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)

    @staticmethod
    def rgb2hex(r, g, b):
        return '#{:02x}{:02x}{:02x}'.format(r, g, b)

    def setcolor(self, r, g, b, ch):
        msg = '#S{:1}{:03x}{:03x}{:03x}'.format(ch, gamma(r), gamma(g), gamma(b))
        if ch == 0: print(msg)
        self.con.write(msg)

    def updatemainpage(self):
        color = self.ui.pushButton_last01.text()
        self.ui.pushButton_last01.setStyleSheet('background-color: {0}'.format(color))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = MainWin()
    myapp.show()
    sys.exit(app.exec_())
