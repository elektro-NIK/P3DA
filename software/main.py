#!/usr/bin/env python3

import sys
import serial
import serial.tools.list_ports
import mainwindow_ui
from PyQt5.QtWidgets import QMainWindow, QApplication, QColorDialog
from PyQt5.QtCore import QTimer


class Connection:
    def __init__(self, dev=None, baud=9600, timeout=1):
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


# TODO: smoots, strobs refactor
class Effect:
    @staticmethod
    def change(colors, interval):
        return interval, colors

    @staticmethod
    def fadeblack(colors, interval):
        for i in range(len(colors)):
            colors.insert(i * 2 + 1, '#000000')
        return Effect.smooth(colors, interval / 2)

    @staticmethod
    def fadewhite(colors, interval):
        for i in range(len(colors)):
            colors.insert(i * 2 + 1, '#ffffff')
        return Effect.smooth(colors, interval / 2)

    @staticmethod
    def smooth(colors, interval):
        colors = [Color.hex2rgb(i) for i in colors]
        step = interval / 11 if interval / 11 < 255 else 255
        res = []
        for i in range(len(colors)):
            start, finish = colors[i - 1], colors[i]
            steps = {'R': (finish[0] - start[0]) / step,
                     'G': (finish[1] - start[1]) / step,
                     'B': (finish[2] - start[2]) / step}
            r, g, b = start
            for j in range(int(step)):
                res.append(Color.rgb2hex(int(r), int(g), int(b)))
                r, g, b = r + steps['R'], g + steps['G'], b + steps['B']
        return interval / step, res

    @staticmethod
    def strob(colors, interval):
        res = []
        for i in colors:
            flash = [i]
            time = 20
            while time < interval:
                flash.append('#000000')
                time += 20
            res += flash
        return 20, res

    @staticmethod
    def strob2(colors, interval):
        res = []
        for i in colors:
            flash = [i, '#000000', '#000000', '#000000', i]
            time = 20 * 5
            while time < interval:
                flash.append('#000000')
                time += 20
            res += flash
        return 20, res


class Tab:
    def __init__(self, obj):
        self.main = obj

    def enabletab(self, flag):
        pass


class TabLight(Tab):
    def __init__(self, obj):
        super().__init__(obj)
        self.rgb = [0, 0, 0]
        # connections
        self.main.ui.pushButton_color.clicked.connect(self.colorselector)
        for i in range(20):
            exec('self.main.ui.pushButton_last{:02}.clicked.connect(self.palettebutton)'.format(i + 1))
        self.connectsliders()
        self.connectdial()
        # update styles
        color = self.main.ui.pushButton_color.text()
        self.main.ui.pushButton_color.setStyleSheet(Color.plainbuttonstyle(color))
        self.updatepalette()

    def enabletab(self, flag):
        self.main.ui.groupBox_last_colors.setEnabled(flag)
        self.main.ui.groupBox_color_bright.setEnabled(flag)

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
        self.colorlist = []
        self.cursor = 0
        self.timer = QTimer()
        # noinspection PyUnresolvedReferences
        self.timer.timeout.connect(self.setcolorinterrupt)
        # connections
        for i in range(4):
            exec('self.main.ui.plainTextEdit_input{}.textChanged.connect(self.checkinput)'.format(i+1))
            exec('self.main.ui.pushButton_effect{}.toggled.connect(self.effectbutton)'.format(i+1))
        # update styles
        for i in range(4):
            _ = ["Change", "Fade black", "Fade white", "Smooth", "Strob", "Double stob"]
            exec('self.main.ui.comboBox_effect{}.addItems(_)'.format(i+1))

    def enabletab(self, flag):
        for i in range(4):
            exec('self.main.ui.groupBox_effect{}.setEnabled(flag)'.format(i+1))

    def effectbutton(self, flag):
        for i in range(4):
            exec('self.main.ui.pushButton_effect{}.setEnabled(not flag)'.format(i + 1))
        self.main.sender().setEnabled(True)
        num = int(self.main.sender().objectName()[17])  # read num of effect field
        if flag:
            exec('self.effectstart(num = self.main.ui.comboBox_effect{}.currentIndex(),\
                                   colors = self.main.ui.plainTextEdit_input{}.toPlainText().split(),\
                                   interval = self.main.ui.spinBox_time{}.value())'.format(num, num, num))
        else:
            self.timer.stop()

    def checkinput(self):
        text = self.main.sender().toPlainText()
        style = 'background-color: #ff0000' if not self.checktext(text) else ''
        self.main.sender().setStyleSheet(style)

    def effectstart(self, num, colors, interval):
        switch = {0: Effect.change,
                  1: Effect.fadeblack,
                  2: Effect.fadewhite,
                  3: Effect.smooth,
                  4: Effect.strob,
                  5: Effect.strob2}
        if self.checktext('\n'.join(colors)):
            time, self.colorlist = switch[num](colors, interval)
            self.cursor = 0
            self.timer.start(time)
        else:
            self.main.sender().setChecked(False)

    def setcolorinterrupt(self):
        r, g, b = Color.hex2rgb(self.colorlist[self.cursor])
        self.main.setcolor(r, g, b, 0)
        self.cursor = self.cursor + 1 if self.cursor < len(self.colorlist)-1 else 0

    @staticmethod
    def checktext(text):
        for i in text.split():
            if len(i) == 6+1:
                try:
                    int(i[1:], 16)
                except ValueError:
                    return False
            else:
                return False
        return True


class TabSound(Tab):
    def __init__(self, obj):
        super().__init__(obj)
        # TODO: connections
        # TODO: update styles

    def enabletab(self, flag):
        self.main.ui.comboBox_player.setEnabled(flag)
        self.main.ui.comboBox_effect_music.setEnabled(flag)
        self.main.ui.groupBox_low.setEnabled(flag)
        self.main.ui.groupBox_medium.setEnabled(flag)
        self.main.ui.groupBox_high.setEnabled(flag)


class TabExtBacklight(Tab):
    def __init__(self, obj):
        super().__init__(obj)
        # TODO: connections
        # TODO: update styles

    def enabletab(self, flag):
        self.main.ui.groupBox_setup_ext.setEnabled(flag)


class TabSetup(Tab):
    def __init__(self, obj):
        super().__init__(obj)
        # TODO: connections
        # TODO: update styles

    def enabletab(self, flag):
        self.main.ui.comboBox_device.setEnabled(flag)
        self.main.ui.groupBox_wb.setEnabled(flag)
        self.main.ui.groupBox_gamma.setEnabled(flag)


class MainWin(QMainWindow):
    # noinspection PyArgumentList
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = mainwindow_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        # try connection
        self.con = Connection(baud=38400)
        try:
            self.con.createconnection(self.detectdevices()[0])
        except IndexError:
            pass
        msg = 'Connected to {}'.format(self.con.dev) if self.con.con else 'No serial adapter found!'
        self.ui.statusbar.showMessage(msg)
        # initializing classes
        self.tablight = TabLight(self)
        self.tabilumination = TabIlumination(self)
        self.tabsound = TabSound(self)
        self.tabextbacklight = TabExtBacklight(self)
        self.tabsetup = TabSetup(self)
        # corrections
        self.gamma = self.ui.doubleSpinBox_gamma.value()
        r = self.ui.horizontalSlider_wb_r.value()
        g = self.ui.horizontalSlider_wb_g.value()
        b = self.ui.horizontalSlider_wb_b.value()
        self.wb = {'R': r, 'G': g, 'B': b}
        # init
        self.ui.tabWidget.currentChanged.connect(self.updatetab)
        self.updatetab(0)

    def updatetab(self, val):
        switch = {0: self.tablight.enabletab,
                  1: self.tabilumination.enabletab,
                  2: self.tabsound.enabletab,
                  3: self.tabextbacklight.enabletab,
                  4: self.tabsetup.enabletab}
        switch[val](flag=self.con.connectionisopen())

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
                self.con.createconnection(i)
                serial.time.sleep(1.5)
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
