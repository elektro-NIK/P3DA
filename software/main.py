#!/usr/bin/env python3

import sys
import serial
import serial.tools.list_ports
import mainwindow_ui
from PyQt5.QtWidgets import QMainWindow, QApplication, QColorDialog, QWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtMultimedia import QAudio, QAudioInput, QAudioFormat, QAudioDeviceInfo
from pyqtgraph import setConfigOptions, mkPen


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
    def flash(colors, interval):
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
    def strob(colors, interval):
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
        rgb = Color.hex2rgb(color)
        self.rgb = [*rgb]
        bright = int(sum(rgb) / 3)
        self.disconnectsliders()
        self.main.ui.horizontalSlider_r.setValue(rgb[0])
        self.main.ui.horizontalSlider_g.setValue(rgb[1])
        self.main.ui.horizontalSlider_b.setValue(rgb[2])
        self.connectsliders()
        self.main.ui.pushButton_color.setText(color)
        self.main.ui.pushButton_color.setStyleSheet(Color.plainbuttonstyle(color))
        self.disconnectdial()
        self.main.ui.dial_bright.setSliderPosition(bright)
        self.main.ui.dial_bright.setValue(bright)
        self.connectdial()
        self.main.ui.lcdNumber_bright.display(bright)
        for i in range(6):
            self.main.setcolor(*rgb, i)

    def savergb(self):
        r = self.main.ui.horizontalSlider_r.value()
        g = self.main.ui.horizontalSlider_g.value()
        b = self.main.ui.horizontalSlider_b.value()
        self.rgb = [r, g, b]

    def dialbright(self, value):
        r, g, b = self.rgb
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
        r, g, b = int(r), int(g), int(b)
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
        rgb = Color.hex2rgb(color)
        bright = int(sum(rgb) / 3)
        self.disconnectsliders()
        self.main.ui.horizontalSlider_r.setValue(rgb[0])
        self.main.ui.horizontalSlider_g.setValue(rgb[1])
        self.main.ui.horizontalSlider_b.setValue(rgb[2])
        self.connectsliders()
        self.main.ui.pushButton_color.setText(color)
        self.main.ui.pushButton_color.setStyleSheet(Color.plainbuttonstyle(color))
        self.disconnectdial()
        self.main.ui.dial_bright.setSliderPosition(bright)
        self.main.ui.dial_bright.setValue(bright)
        self.connectdial()
        self.main.ui.lcdNumber_bright.display(bright)
        for i in range(6):
            self.main.setcolor(*rgb, i)


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
            exec('self.main.ui.plainTextEdit_input{}.textChanged.connect(self.checkinput)'.format(i + 1))
            exec('self.main.ui.pushButton_effect{}.toggled.connect(self.effectbutton)'.format(i + 1))
        # update styles
        _ = ["Change", "Fade black", "Fade white", "Smooth", "Flash", "Strob"]
        for i in range(4):
            exec('self.main.ui.comboBox_effect{}.addItems(_)'.format(i + 1))

    def enabletab(self, flag):
        for i in range(4):
            exec('self.main.ui.groupBox_effect{}.setEnabled(flag)'.format(i + 1))

    def effectbutton(self, flag):
        for i in range(4):
            exec('self.main.ui.pushButton_effect{}.setEnabled(not flag)'.format(i + 1))
        self.main.sender().setEnabled(True)
        num = int(self.main.sender().objectName()[17])  # read num of effect field
        self.main.settabsenable(not flag)
        if flag:
            exec('self.effectstart(num = self.main.ui.comboBox_effect{}.currentIndex(),\
                                   colors = self.main.ui.plainTextEdit_input{}.toPlainText().split(),\
                                   interval = self.main.ui.spinBox_time{}.value())'.format(num, num, num))
        else:
            self.timer.stop()

    def checkinput(self):
        text = self.main.sender().toPlainText()
        style = 'background-color: #ff0000' if not self.main.checktext(text) else ''
        self.main.sender().setStyleSheet(style)

    def effectstart(self, num, colors, interval):
        switch = {0: Effect.change,
                  1: Effect.fadeblack,
                  2: Effect.fadewhite,
                  3: Effect.smooth,
                  4: Effect.flash,
                  5: Effect.strob}
        if self.main.checktext('\n'.join(colors)):
            time, self.colorlist = switch[num](colors, interval)
            self.cursor = 0
            self.timer.start(time)
        else:
            self.main.sender().setChecked(False)

    def setcolorinterrupt(self):
        rgb = Color.hex2rgb(self.colorlist[self.cursor])
        for i in range(6):
            self.main.setcolor(*rgb, i)
        self.cursor = self.cursor + 1 if self.cursor < len(self.colorlist) - 1 else 0


class TabSound(Tab):
    def __init__(self, obj):
        super().__init__(obj)
        self.mode = None
        self.colors = None
        self.count = 0
        # noinspection PyArgumentList
        self.inputdevices = QAudioDeviceInfo.availableDevices(QAudio.AudioInput)
        self.input = None
        if self.inputdevices:
            self.changeinput(0)
        self.stream = None
        self.timer = QTimer()
        # connections
        # noinspection PyUnresolvedReferences
        self.timer.timeout.connect(self.setcolorinterrupt)
        self.main.ui.plainTextEdit_bitdetector.textChanged.connect(self.checkinput)
        self.main.ui.comboBox_input.currentIndexChanged.connect(self.changeinput)
        self.main.ui.comboBox_effect_music.currentIndexChanged.connect(self.changetextedit)
        self.main.ui.pushButton_color_low.clicked.connect(self.colorselector)
        self.main.ui.pushButton_color_mid.clicked.connect(self.colorselector)
        self.main.ui.pushButton_color_high.clicked.connect(self.colorselector)
        self.main.ui.verticalSlider_lower_low.valueChanged.connect(self.changeslider)
        self.main.ui.verticalSlider_lower_mid.valueChanged.connect(self.changeslider)
        self.main.ui.verticalSlider_lower_high.valueChanged.connect(self.changeslider)
        self.main.ui.verticalSlider_higher_low.valueChanged.connect(self.changeslider)
        self.main.ui.verticalSlider_higher_mid.valueChanged.connect(self.changeslider)
        self.main.ui.verticalSlider_higher_high.valueChanged.connect(self.changeslider)
        self.main.ui.pushButton_sound_onoff.toggled.connect(self.soundbuttononoff)
        # update styles
        effects = ['Smooth', 'Change', 'Flash', 'Strob']
        self.main.ui.comboBox_effect_music.addItems(effects)
        inputs = [i.deviceName() for i in self.inputdevices]
        self.main.ui.comboBox_input.addItems(inputs)
        self.updatebuttons()

    def enabletab(self, flag):
        self.main.ui.comboBox_input.setEnabled(flag)
        self.main.ui.comboBox_effect_music.setEnabled(flag)
        self.main.ui.groupBox_freq.setEnabled(flag)
        self.main.ui.groupBox_bit_detect.setEnabled(flag)
        self.main.ui.pushButton_sound_onoff.setEnabled(flag)

    def updatebuttons(self):
        color = self.main.ui.pushButton_color_low.text()
        self.main.ui.pushButton_color_low.setStyleSheet(Color.plainbuttonstyle(color))
        color = self.main.ui.pushButton_color_mid.text()
        self.main.ui.pushButton_color_mid.setStyleSheet(Color.plainbuttonstyle(color))
        color = self.main.ui.pushButton_color_high.text()
        self.main.ui.pushButton_color_high.setStyleSheet(Color.plainbuttonstyle(color))

    def checkinput(self):
        text = self.main.ui.plainTextEdit_bitdetector.toPlainText()
        style = 'background-color: #ff0000' if not self.main.checktext(text) else ''
        self.main.ui.plainTextEdit_bitdetector.setStyleSheet(style)

    def changeinput(self, val):
        audio = QAudioFormat()
        audio.setSampleRate(44100)
        audio.setSampleType(QAudioFormat.UnSignedInt)
        audio.setSampleSize(8)
        audio.setCodec('audio/pcm')
        audio.setChannelCount(1)
        self.input = QAudioInput(self.inputdevices[val], audio)

    def changetextedit(self, val):
        self.main.ui.plainTextEdit_bitdetector.setEnabled(bool(val))

    def changeslider(self, val):  # 1 <= 2 <= 3 <= 4 <= 5 <= 6 (sliders)
        if self.main.sender() == self.main.ui.verticalSlider_lower_low:
            if val+10 > self.main.ui.verticalSlider_higher_low.value():
                self.main.ui.verticalSlider_higher_low.setValue(val+10)
        elif self.main.sender() == self.main.ui.verticalSlider_higher_low:
            if val > self.main.ui.verticalSlider_lower_mid.value():
                self.main.ui.verticalSlider_lower_mid.setValue(val)
            if val-10 < self.main.ui.verticalSlider_lower_low.value():
                self.main.ui.verticalSlider_lower_low.setValue(val-10)
        elif self.main.sender() == self.main.ui.verticalSlider_lower_mid:
            if val+10 > self.main.ui.verticalSlider_higher_mid.value():
                self.main.ui.verticalSlider_higher_mid.setValue(val+10)
            if val < self.main.ui.verticalSlider_higher_low.value():
                self.main.ui.verticalSlider_higher_low.setValue(val)
        elif self.main.sender() == self.main.ui.verticalSlider_higher_mid:
            if val > self.main.ui.verticalSlider_lower_high.value():
                self.main.ui.verticalSlider_lower_high.setValue(val)
            if val-10 < self.main.ui.verticalSlider_lower_mid.value():
                self.main.ui.verticalSlider_lower_mid.setValue(val-10)
        elif self.main.sender() == self.main.ui.verticalSlider_lower_high:
            if val+10 > self.main.ui.verticalSlider_higher_high.value():
                self.main.ui.verticalSlider_higher_high.setValue(val+10)
            if val < self.main.ui.verticalSlider_higher_mid.value():
                self.main.ui.verticalSlider_higher_mid.setValue(val)
        elif self.main.sender() == self.main.ui.verticalSlider_higher_high:
            if val-10 < self.main.ui.verticalSlider_lower_high.value():
                self.main.ui.verticalSlider_lower_high.setValue(val-10)

    def colorselector(self):
        # noinspection PyArgumentList
        dialog = QColorDialog().getColor()
        temp = '{:x}'.format(dialog.rgb())
        color = '#{}'.format(temp[2:])
        self.main.sender().setText(color)
        self.main.sender().setStyleSheet(Color.plainbuttonstyle(color))

    def soundbuttononoff(self, flag):
        self.main.settabsenable(not flag)
        if flag:
            self.mode = self.main.ui.comboBox_effect_music.currentText()
            text = self.main.ui.plainTextEdit_bitdetector.toPlainText()
            if self.main.checktext(text):
                self.colors = text.split()
                self.count = 0
                self.stream = self.input.start()
                timeout = 50 if self.mode == 'Smooth' else 200
                self.timer.start(timeout)
            else:
                self.main.ui.pushButton_sound_onoff.setChecked(False)
        else:
            self.input.stop()
            self.timer.stop()
            self.stream = None

    def setcolorinterrupt(self):
        val = self.stream.readAll().data()
        self.timer.stop()
        if val:
            from numpy import fft
            from numpy.ma import absolute
            val = [i - 128 for i in val]
            fur = absolute(fft.fft(val))
            freq = fft.fftfreq(len(val), d=1 / 44100)
            fur = fur[1:int(len(fur) / 2)]
            freq = freq[1:int(len(freq) / 2)]
            switch = {'Smooth': self.smooth,
                      'Change': self.change,
                      'Flash': self.flash,
                      'Strob': self.strob}
            switch[self.mode](fur, freq)
        timeout = 50 if self.mode == 'Smooth' else 200
        self.timer.start(timeout)

    def smooth(self, val, freq):
        lowcolor = Color.hex2rgb(self.main.ui.pushButton_color_low.text())
        midcolor = Color.hex2rgb(self.main.ui.pushButton_color_mid.text())
        highcolor = Color.hex2rgb(self.main.ui.pushButton_color_high.text())
        lowlimits = [self.main.ui.verticalSlider_lower_low.value(), self.main.ui.verticalSlider_higher_low.value()]
        midlimits = [self.main.ui.verticalSlider_lower_mid.value(), self.main.ui.verticalSlider_higher_mid.value()]
        highlimits = [self.main.ui.verticalSlider_lower_high.value(), self.main.ui.verticalSlider_higher_high.value()]
        lowval, midval, highval = [], [], []
        for i in range(len(freq)):
            if lowlimits[0] < freq[i] < lowlimits[1]:
                lowval.append(val[i])
        for i in range(len(freq)):
            if midlimits[0] < freq[i] < midlimits[1]:
                midval.append(val[i])
        for i in range(len(freq)):
            if highlimits[0] < freq[i] < highlimits[1]:
                highval.append(val[i])
        lowval = max(lowval) if lowval else 0
        midval = max(midval) if midval else 0
        highval = max(highval) if highval else 0
        mult = [self.main.ui.doubleSpinBox_mult_low.value(),
                self.main.ui.doubleSpinBox_mult_mid.value(),
                self.main.ui.doubleSpinBox_mult_high.value()]
        noise = self.main.ui.horizontalSlider_noise.value()
        limiter = max(val) if max(val) > 4000 else 4000
        if limiter > noise:
            multval = [(lowval-noise)/(limiter-noise) if lowval > noise else 0,
                       (midval-noise)/(limiter-noise) if midval > noise else 0,
                       (highval-noise)/(limiter-noise) if highval > noise else 0]
            r = (lowcolor[0]+midcolor[0]+highcolor[0]) * mult[0] * multval[0]
            g = (lowcolor[1]+midcolor[1]+highcolor[1]) * mult[1] * multval[1]
            b = (lowcolor[2]+midcolor[2]+highcolor[2]) * mult[2] * multval[2]
            for i in range(6):
                self.main.setcolor(int(r), int(g), int(b), i)
        else:
            for i in range(6):
                self.main.setcolor(0, 0, 0, i)

    def change(self, val, freq):
        freqlow = self.main.ui.verticalSlider_lower_low.value()
        freqhigh = self.main.ui.verticalSlider_higher_low.value()
        limit = self.main.ui.horizontalSlider_noise.value()
        lvl = []
        for i in range(len(freq)):
            if freqlow < freq[i] < freqhigh:
                lvl.append(val[i])
        lvl = sum(lvl) / len(lvl)
        if lvl > limit:
            for i in range(6):
                self.main.setcolor(*Color.hex2rgb(self.colors[self.count]), i)
            self.count = self.count+1 if self.count < len(self.colors)-1 else 0

    def flash(self, val, freq):
        freqlow = self.main.ui.verticalSlider_lower_low.value()
        freqhigh = self.main.ui.verticalSlider_higher_low.value()
        limit = self.main.ui.horizontalSlider_noise.value()
        lvl = []
        for i in range(len(freq)):
            if freqlow < freq[i] < freqhigh:
                lvl.append(val[i])
        lvl = sum(lvl) / len(lvl)
        if lvl > limit:
            for i in range(6):
                self.main.setcolor(*Color.hex2rgb(self.colors[self.count]), i)
            for i in range(6):
                self.main.setcolor(0, 0, 0, i)
            self.count = self.count + 1 if self.count < len(self.colors) - 1 else 0

    def strob(self, val, freq):
        freqlow = self.main.ui.verticalSlider_lower_low.value()
        freqhigh = self.main.ui.verticalSlider_higher_low.value()
        limit = self.main.ui.horizontalSlider_noise.value()
        lvl = []
        for i in range(len(freq)):
            if freqlow < freq[i] < freqhigh:
                lvl.append(val[i])
        lvl = sum(lvl) / len(lvl)
        if lvl > limit:
            for _ in range(2):
                for i in range(6):
                    self.main.setcolor(*Color.hex2rgb(self.colors[self.count]), i)
                for __ in range(3):
                    for i in range(6):
                        self.main.setcolor(0, 0, 0, i)
            self.count = self.count + 1 if self.count < len(self.colors) - 1 else 0


class TabExtBacklight(Tab):
    def __init__(self, obj):
        super().__init__(obj)
        self.zones = []
        self.geometry = None
        self.timer = QTimer()
        # connections
        # noinspection PyUnresolvedReferences
        self.timer.timeout.connect(self.newprintscreen)
        self.main.ui.pushButton_zones.toggled.connect(self.setzones)
        self.main.ui.pushButton_ext_on_off.toggled.connect(self.extonoff)
        # TODO: combobox

    def enabletab(self, flag):
        # Fixme: True -> flag
        self.main.ui.groupBox_setup_ext.setEnabled(True)

    def setzones(self, flag):
        self.main.ui.pushButton_ext_on_off.setEnabled(not flag)
        if flag:
            self.zones = [ZoneRect(i+1) for i in range(self.main.ui.spinBox_count_zones.value())]
            for rect in self.zones:
                rect.show()
        else:
            self.geometry = [rect.geometry() for rect in self.zones]
            self.zones = []

    def extonoff(self, flag):
        self.main.ui.pushButton_zones.setEnabled(not (flag and self.geometry))
        if flag and self.geometry:
            self.timer.start(self.main.ui.spinBox_update.value())
        else:
            self.main.ui.pushButton_ext_on_off.setChecked(False)
            self.timer.stop()
            # TODO: delete me!
            from PyQt5.QtGui import QPixmap
            self.main.ui.label_img.setPixmap(QPixmap())

    def newprintscreen(self):
        from PyQt5.QtGui import QGuiApplication
        # noinspection PyArgumentList
        screen = QGuiApplication.primaryScreen()
        # noinspection PyArgumentList
        shot = screen.grabWindow(QApplication.desktop().winId())
        shot = shot.scaledToHeight(self.main.ui.label_img.height())
        # TODO: crop
        self.main.ui.label_img.setPixmap(shot)
        print('!'*len(self.geometry), shot)


class TabSetup(Tab):
    def __init__(self, obj):
        super().__init__(obj)
        # connections
        self.main.ui.comboBox_device.currentIndexChanged.connect(self.newconnection)
        self.main.ui.pushButton_update.clicked.connect(self.updatedevs)
        self.main.ui.horizontalSlider_wb_r.valueChanged.connect(self.updatewb)
        self.main.ui.horizontalSlider_wb_g.valueChanged.connect(self.updatewb)
        self.main.ui.horizontalSlider_wb_b.valueChanged.connect(self.updatewb)
        self.main.ui.doubleSpinBox_gamma.valueChanged.connect(self.updategamma)
        # update styles
        devs = self.main.con.devicesonline()
        self.main.ui.comboBox_device.addItems(self.main.devs)
        if self.main.devs:
            self.main.ui.label_device.setText(devs[self.main.devs[0]])
        setConfigOptions(antialias=True)
        self.main.ui.graphicsView_gamma.setRange(xRange=[0, 255], yRange=[0, 511])
        self.main.ui.graphicsView_gamma.setMenuEnabled(False)
        self.updategraphics()

    def enabletab(self, flag):
        self.main.ui.comboBox_device.setEnabled(flag)
        self.main.ui.groupBox_wb.setEnabled(flag)
        self.main.ui.groupBox_gamma.setEnabled(flag)

    def newconnection(self, val):
        try:
            self.main.con.close()
        except AttributeError:
            pass
        devs = self.main.con.devicesonline()
        self.main.ui.label_device.setText(devs[self.main.devs[val]])
        self.main.con.createconnection(self.main.devs[val])
        self.enabletab(True)
        self.main.ui.statusbar.showMessage('Connected to {}'.format(self.main.devs[val]))

    def updatedevs(self):
        self.main.devs = self.main.detectdevices()
        self.main.ui.comboBox_device.clear()
        self.main.ui.comboBox_device.addItems(self.main.devs)

    def updatewb(self):
        r = self.main.ui.horizontalSlider_wb_r.value()
        g = self.main.ui.horizontalSlider_wb_g.value()
        b = self.main.ui.horizontalSlider_wb_b.value()
        self.main.wb = {'R': r, 'G': g, 'B': b}
        self.updategraphics()
        for ch in range(6):
            self.main.con.write('#S{:1}{:03x}{:03x}{:03x}'.format(ch, r, g, b))

    def updategamma(self, val):
        self.main.gamma = val
        self.updategraphics()

    def updategraphics(self):
        self.main.ui.graphicsView_gamma.clear()
        main = [(x / 255) ** self.main.gamma * 511 for x in range(255)]
        red = [(x/255) ** self.main.gamma * self.main.wb['R'] for x in range(255)]
        green = [(x/255) ** self.main.gamma * self.main.wb['G'] for x in range(255)]
        blue = [(x/255) ** self.main.gamma * self.main.wb['B'] for x in range(255)]
        self.main.ui.graphicsView_gamma.plot(red, pen='#ff0000')
        self.main.ui.graphicsView_gamma.plot(green, pen='#00ff00')
        self.main.ui.graphicsView_gamma.plot(blue, pen='#0000ff')
        self.main.ui.graphicsView_gamma.plot(main, pen=mkPen('#ffffff', width=2))


class ZoneRect(QWidget):
    def __init__(self, num, x=0, y=0, width=100, height=100):
        from PyQt5.QtWidgets import QLabel, QVBoxLayout, QStatusBar
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        super().__init__(parent=None, flags=Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # var
        self.mpos = 0
        # setup
        layout, label, font, statusbar = QVBoxLayout(), QLabel(), QFont(), QStatusBar()
        font.setFamily("Arial");
        font.setPointSize(40)
        label.setFont(font)
        label.setText(str(num))
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(label, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        layout.addWidget(statusbar)
        self.setLayout(layout)
        self.setWindowTitle('Zone {}'.format(num))
        self.setWindowOpacity(0.5)
        self.setGeometry(x, y, width, height)

    def mousePressEvent(self, event):
        self.mpos = event.pos()

    def mouseMoveEvent(self, event):
        diff = event.pos() - self.mpos
        newpos = self.pos() + diff
        self.move(newpos)


class MainWin(QMainWindow):
    # noinspection PyArgumentList
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = mainwindow_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        # self.ui.comboBox_device.currentIndexChanged()
        # try connection
        self.con = Connection(baud=38400)
        self.devs = self.detectdevices()
        if self.devs:
            self.con.createconnection(self.devs[0])
        msg = 'Connected to {}'.format(self.con.dev) if self.con.con else 'No serial adapter found!'
        self.ui.statusbar.showMessage(msg)
        # corrections
        self.gamma = self.ui.doubleSpinBox_gamma.value()
        r = self.ui.horizontalSlider_wb_r.value()
        g = self.ui.horizontalSlider_wb_g.value()
        b = self.ui.horizontalSlider_wb_b.value()
        self.wb = {'R': r, 'G': g, 'B': b}
        # initializing classes
        self.tablight = TabLight(self)
        self.tabilumination = TabIlumination(self)
        self.tabsound = TabSound(self)
        self.tabextbacklight = TabExtBacklight(self)
        self.tabsetup = TabSetup(self)
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

    def settabsenable(self, flag):
        count = list(range(self.ui.tabWidget.count()))
        count.remove(self.ui.tabWidget.currentIndex())
        for i in count:
            self.ui.tabWidget.setTabEnabled(i, flag)

    def detectdevices(self):
        baddevices = ['Android Platform', 'AndroidNet']                        # bug with write on 38400 baud (Windows?)
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

    @staticmethod
    def checktext(text):
        for i in text.split():
            if len(i) == 6 + 1:
                try:
                    int(i[1:], 16)
                except ValueError:
                    return False
            else:
                return False
        return True


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = MainWin()
    myapp.show()
    sys.exit(app.exec_())
