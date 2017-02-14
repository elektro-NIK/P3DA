#!/usr/bin/env python3

import sys
import serial
import serial.tools.list_ports
import mainwindow_ui
from PyQt5.QtWidgets import QMainWindow, QApplication, QColorDialog


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
        # initializing
        self.rgb = [0, 0, 0]
        self.con = Connection(baud=38400)
        if len(self.con.devicesonline()) == 0:
            self.ui.statusbar.showMessage('No serial adapter found!', msecs=3000)
        self.ui.pushButton_color.setStyleSheet(self.getstyle('#000000'))
        # connect palette buttons
        for i in range(20):
            exec('self.ui.pushButton_last{:02}.clicked.connect(self.palettebutton)'.format(i + 1))
        # other connections
        self.ui.pushButton_color.clicked.connect(self.colorselector)
        self.connectsliders()
        self.connectdial()
        self.updatepalette()

    def connectsliders(self):
        self.ui.horizontalSlider_r.valueChanged.connect(self.slidercolor)
        self.ui.horizontalSlider_g.valueChanged.connect(self.slidercolor)
        self.ui.horizontalSlider_b.valueChanged.connect(self.slidercolor)

    def disconnectsliders(self):
        self.ui.horizontalSlider_r.valueChanged.disconnect(self.slidercolor)
        self.ui.horizontalSlider_g.valueChanged.disconnect(self.slidercolor)
        self.ui.horizontalSlider_b.valueChanged.disconnect(self.slidercolor)

    def connectdial(self):
        self.ui.dial_bright.sliderPressed.connect(self.savergb)
        self.ui.dial_bright.sliderMoved.connect(self.dialbright)
        self.ui.dial_bright.valueChanged.connect(self.dialbright)

    def disconnectdial(self):
        self.ui.dial_bright.sliderPressed.disconnect(self.savergb)
        self.ui.dial_bright.sliderMoved.disconnect(self.dialbright)
        self.ui.dial_bright.valueChanged.disconnect(self.dialbright)

    def palettebutton(self):
        color = self.sender().text()
        r, g, b = self.hex2rgb(color)
        self.rgb = [r, g, b]
        bright = int((r + g + b) / 3)
        self.disconnectsliders()
        self.ui.horizontalSlider_r.setValue(r)
        self.ui.horizontalSlider_g.setValue(g)
        self.ui.horizontalSlider_b.setValue(b)
        self.connectsliders()
        self.ui.pushButton_color.setText(color)
        self.ui.pushButton_color.setStyleSheet(self.getstyle(color))
        self.disconnectdial()
        self.ui.dial_bright.setSliderPosition(bright)
        self.ui.dial_bright.setValue(bright)
        self.connectdial()
        self.ui.lcdNumber_bright.display(bright)
        for i in range(6):
            self.setcolor(r, g, b, i)

    def savergb(self):
        r = self.ui.horizontalSlider_r.value()
        g = self.ui.horizontalSlider_g.value()
        b = self.ui.horizontalSlider_b.value()
        self.rgb = [r, g, b]

    def dialbright(self, value):
        r = self.rgb[0]
        g = self.rgb[1]
        b = self.rgb[2]
        avr = (r+g+b) / 3 if any([r, g, b]) else 1
        add = value - avr
        if add > 0:
            r += add * (255 - r) / (255 - avr)
            g += add * (255 - g) / (255 - avr)
            b += add * (255 - b) / (255 - avr)
        else:
            r += add * r / avr
            g += add * g / avr
            b += add * b / avr
        r = int(r)
        g = int(g)
        b = int(b)
        self.disconnectsliders()
        self.ui.horizontalSlider_r.setValue(r)
        self.ui.horizontalSlider_g.setValue(g)
        self.ui.horizontalSlider_b.setValue(b)
        self.connectsliders()
        self.ui.lcdNumber_bright.display(value)
        self.ui.pushButton_color.setText(self.rgb2hex(r, g, b))
        self.ui.pushButton_color.setStyleSheet(self.getstyle(self.rgb2hex(r, g, b)))
        for i in range(6):
            self.setcolor(r, g, b, i)

    def slidercolor(self):
        r = self.ui.horizontalSlider_r.value()
        g = self.ui.horizontalSlider_g.value()
        b = self.ui.horizontalSlider_b.value()
        color = self.rgb2hex(r, g, b)
        bright = int((r + g + b) / 3)
        self.ui.pushButton_color.setText(color)
        self.ui.pushButton_color.setStyleSheet(self.getstyle(color))
        self.disconnectdial()
        self.ui.dial_bright.setSliderPosition(bright)
        self.ui.dial_bright.setValue(bright)
        self.connectdial()
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
        if ch == 0:
            print(msg)
        self.con.write(msg)

    def updatepalette(self):
        colors = list()                                                               # in exec don't work '=' with self
        for i in range(20):
            exec('colors.append(self.ui.pushButton_last{:02}.text())'.format(i+1))
            exec('self.ui.pushButton_last{:02}.setStyleSheet("{}")'.format(i+1, self.getstyle(colors[-1])))

    def getstyle(self, background):
        r, g, b = self.hex2rgb(background)
        textcolor = '#000000' if (r + 2.4*g + b)/4.4 > 127 else '#ffffff'
        return 'border: 0px; background-color: {}; color: {};'.format(background, textcolor)

    def colorselector(self):
        # noinspection PyArgumentList
        dialog = QColorDialog().getColor()
        temp = '{:x}'.format(dialog.rgb())
        color = '#{}'.format(temp[2:])
        r, g, b = self.hex2rgb(color)
        bright = int((r + g + b) / 3)
        self.disconnectsliders()
        self.ui.horizontalSlider_r.setValue(r)
        self.ui.horizontalSlider_g.setValue(g)
        self.ui.horizontalSlider_b.setValue(b)
        self.connectsliders()
        self.ui.pushButton_color.setText(color)
        self.ui.pushButton_color.setStyleSheet(self.getstyle(color))
        self.disconnectdial()
        self.ui.dial_bright.setSliderPosition(bright)
        self.ui.dial_bright.setValue(bright)
        self.connectdial()
        self.ui.lcdNumber_bright.display(bright)
        for i in range(6):
            self.setcolor(r, g, b, i)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = MainWin()
    myapp.show()
    sys.exit(app.exec_())
