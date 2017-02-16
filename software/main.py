#!/usr/bin/env python3

import sys
import serial
import serial.tools.list_ports
import mainwindow_ui
from PyQt5.QtWidgets import QMainWindow, QApplication, QColorDialog


class Connection:
    def __init__(self, dev=None, baud=9600, timeout=0.1):
        self.dev, self.baud, self.timeout = dev, baud, timeout
        self.con = None

    def createconnection(self, dev=None):
        self.dev = dev if dev else self.dev
        try:
            self.con = serial.Serial(port=self.dev, baudrate=self.baud, timeout=self.timeout)
        except serial.serialutil.SerialException:
            pass

    def write(self, msg):
        self.con.write(msg.encode())

    def read(self, size=1):
        return self.con.read(size=size).decode('utf-8')

    def readline(self):
        return self.con.readline().decode('utf-8')

    def close(self):
        self.con.close()
        self.con = None

    @staticmethod
    def devicesonline():
        coms = serial.tools.list_ports.comports()
        return {i.device: i.description for i in coms[::-1]}

    def connectionisopen(self):
        return bool(self.con)


class Color:
    @staticmethod
    def hex2rgb(color):
        return int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)

    @staticmethod
    def rgb2hex(r, g, b):
        return '#{:02x}{:02x}{:02x}'.format(r, g, b)

    @staticmethod
    def plainbuttonstyle(background):
        r, g, b = Color.hex2rgb(background)
        textcolor = '#000000' if (r + 2.4 * g + b) / 4.4 > 127 else '#ffffff'
        return 'border: 0px; background-color: {}; color: {};'.format(background, textcolor)


class Tab:
    def __init__(self, obj):
        self.main = obj

    def updatetab(self, connect):
        pass


class TabLight(Tab):
    def __init__(self, obj):
        super().__init__(obj)
        self.main = obj
        self.rgb = [0, 0, 0]

    def updatetab(self, connect):
        color = self.main.ui.pushButton_color.text()
        self.main.ui.pushButton_color.setStyleSheet(Color.plainbuttonstyle(color))
        if connect:
            self.main.ui.pushButton_color.clicked.connect(self.colorselector)
            for i in range(20):
                exec('self.main.ui.pushButton_last{:02}.clicked.connect(self.palettebutton)'.format(i + 1))
            self.connectsliders()
            self.connectdial()
        self.updatepalette()

    def updatepalette(self):
        colors, _ = list(), self  # in exec don't work '=' with self
        for i in range(20):
            exec('colors.append(self.main.ui.pushButton_last{:02}.text())'.format(i + 1))
            style = Color.plainbuttonstyle(colors[-1])
            exec('self.main.ui.pushButton_last{:02}.setStyleSheet("{}")'.format(i + 1, style))

    def connectsliders(self):
        self.main.ui.horizontalSlider_r.valueChanged.connect(self.slidercolor)
        self.main.ui.horizontalSlider_g.valueChanged.connect(self.slidercolor)
        self.main.ui.horizontalSlider_b.valueChanged.connect(self.slidercolor)

    def disconnectsliders(self):
        self.main.ui.horizontalSlider_r.valueChanged.disconnect(self.slidercolor)
        self.main.ui.horizontalSlider_g.valueChanged.disconnect(self.slidercolor)
        self.main.ui.horizontalSlider_b.valueChanged.disconnect(self.slidercolor)

    def connectdial(self):
        self.main.ui.dial_bright.sliderPressed.connect(self.savergb)
        self.main.ui.dial_bright.sliderMoved.connect(self.dialbright)
        self.main.ui.dial_bright.valueChanged.connect(self.dialbright)

    def disconnectdial(self):
        self.main.ui.dial_bright.sliderPressed.disconnect(self.savergb)
        self.main.ui.dial_bright.sliderMoved.disconnect(self.dialbright)
        self.main.ui.dial_bright.valueChanged.disconnect(self.dialbright)

    def palettebutton(self):
        color = self.main.sender().text()
        r, g, b = Color.hex2rgb(color)
        self.rgb = [r, g, b]
        bright = int((r + g + b) / 3)
        self.disconnectsliders()
        self.main.ui.horizontalSlider_r.setValue(r)
        self.main.ui.horizontalSlider_g.setValue(g)
        self.main.ui.horizontalSlider_b.setValue(b)
        self.connectsliders()
        self.main.ui.pushButton_color.setText(color)
        self.main.ui.pushButton_color.setStyleSheet(Color.plainbuttonstyle(color))
        self.disconnectdial()
        self.main.ui.dial_bright.setSliderPosition(bright)
        self.main.ui.dial_bright.setValue(bright)
        self.connectdial()
        self.main.ui.lcdNumber_bright.display(bright)
        for i in range(6):
            self.main.setcolor(r, g, b, i)

    def savergb(self):
        r = self.main.ui.horizontalSlider_r.value()
        g = self.main.ui.horizontalSlider_g.value()
        b = self.main.ui.horizontalSlider_b.value()
        self.rgb = [r, g, b]

    def dialbright(self, value):
        r = self.rgb[0]
        g = self.rgb[1]
        b = self.rgb[2]
        avr = (r + g + b) / 3 if any([r, g, b]) else 1
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
        self.main.ui.horizontalSlider_r.setValue(r)
        self.main.ui.horizontalSlider_g.setValue(g)
        self.main.ui.horizontalSlider_b.setValue(b)
        self.connectsliders()
        self.main.ui.lcdNumber_bright.display(value)
        self.main.ui.pushButton_color.setText(Color.rgb2hex(r, g, b))
        self.main.ui.pushButton_color.setStyleSheet(Color.plainbuttonstyle(Color.rgb2hex(r, g, b)))
        for i in range(6):
            self.main.setcolor(r, g, b, i)

    def slidercolor(self):
        r = self.main.ui.horizontalSlider_r.value()
        g = self.main.ui.horizontalSlider_g.value()
        b = self.main.ui.horizontalSlider_b.value()
        color = Color.rgb2hex(r, g, b)
        bright = int((r + g + b) / 3)
        self.main.ui.pushButton_color.setText(color)
        self.main.ui.pushButton_color.setStyleSheet(Color.plainbuttonstyle(color))
        self.disconnectdial()
        self.main.ui.dial_bright.setSliderPosition(bright)
        self.main.ui.dial_bright.setValue(bright)
        self.connectdial()
        self.main.ui.lcdNumber_bright.display(bright)
        for i in range(6):
            self.main.setcolor(r, g, b, i)

    def colorselector(self):
        # noinspection PyArgumentList
        dialog = QColorDialog().getColor()
        temp = '{:x}'.format(dialog.rgb())
        color = '#{}'.format(temp[2:])
        r, g, b = Color.hex2rgb(color)
        bright = int((r + g + b) / 3)
        self.disconnectsliders()
        self.main.ui.horizontalSlider_r.setValue(r)
        self.main.ui.horizontalSlider_g.setValue(g)
        self.main.ui.horizontalSlider_b.setValue(b)
        self.connectsliders()
        self.main.ui.pushButton_color.setText(color)
        self.main.ui.pushButton_color.setStyleSheet(Color.plainbuttonstyle(color))
        self.disconnectdial()
        self.main.ui.dial_bright.setSliderPosition(bright)
        self.main.ui.dial_bright.setValue(bright)
        self.connectdial()
        self.main.ui.lcdNumber_bright.display(bright)
        for i in range(6):
            self.main.setcolor(r, g, b, i)


class TabIlumination(Tab):
    def __init__(self, obj):
        super().__init__(obj)
        self.main = obj

    def updatetab(self, connect):  # TODO: all tab update
        pass


class TabSound(Tab):  # TODO: this tab
    def __init__(self, obj):
        super().__init__(obj)
        self.main = obj


class TabExtBacklight(Tab):  # TODO: this tab
    def __init__(self, obj):
        super().__init__(obj)
        self.main = obj


class TabSetup(Tab):  # TODO: this tab
    def __init__(self, obj):
        super().__init__(obj)
        self.main = obj


class MainWin(QMainWindow):
    # noinspection PyArgumentList
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = mainwindow_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        # initializing classes
        self.con = Connection(baud=38400)
        self.tablight = TabLight(self)
        self.tabilumination = TabIlumination(self)
        self.tabsound = TabSound(self)
        self.tabextbacklight = TabExtBacklight(self)
        self.tabsetup = TabSetup(self)
        self.gamma = self.ui.doubleSpinBox_gamma.value()
        r = self.ui.horizontalSlider_wb_r.value()
        g = self.ui.horizontalSlider_wb_g.value()
        b = self.ui.horizontalSlider_wb_b.value()
        self.wb = {'R': r, 'G': g, 'B': b}
        # try connection
        try:
            self.con.createconnection(self.detectdevices()[0])
        except IndexError:
            pass
        msg = 'Connected to {}'.format(self.con.dev) if self.con.con else 'No serial adapter found!'
        self.ui.statusbar.showMessage(msg)
        # init
        self.ui.tabWidget.currentChanged.connect(self.updatetab)
        self.updatetab(0)

    def updatetab(self, val):
        switch = {0: self.tablight.updatetab,
                  1: self.tabilumination.updatetab,
                  2: self.tabsound.updatetab,
                  3: self.tabextbacklight.updatetab,
                  4: self.tabsetup.updatetab}
        switch[val](connect=self.con.connectionisopen())

    def detectdevices(self):
        baddevices = ['Android Platform']  # bug with write on 38400 baud
        res = []
        devs = self.con.devicesonline()
        coms = list(devs.keys())
        for i in coms:
            bad = False
            for j in baddevices:
                if j in devs[i]:
                    bad = True
            if not bad:
                self.con.dev = i
                self.con.createconnection()
                self.con.write('#T')
                answ = self.con.read(3)
                if answ == '#OK':
                    res.append(i)
                self.con.close()
        return res

    def setcolor(self, r, g, b, ch):
        msg = '#S{:1}{:03x}{:03x}{:03x}'.format(ch,
                                                self.gammacorrection(r, 'R'),
                                                self.gammacorrection(g, 'G'),
                                                self.gammacorrection(b, 'B'))
        if ch == 0:
            print(msg)
        self.con.write(msg)

    def gammacorrection(self, val, color):
        return round((val / 255) ** self.gamma * self.wb[color])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = MainWin()
    myapp.show()
    sys.exit(app.exec_())
