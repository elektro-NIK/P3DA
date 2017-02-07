# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(640, 480)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalSlider_red = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider_red.setMaximum(511)
        self.horizontalSlider_red.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_red.setObjectName("horizontalSlider_red")
        self.gridLayout.addWidget(self.horizontalSlider_red, 0, 0, 1, 1)
        self.spinBox_red = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox_red.setMaximum(511)
        self.spinBox_red.setObjectName("spinBox_red")
        self.gridLayout.addWidget(self.spinBox_red, 0, 1, 1, 1)
        self.horizontalSlider_green = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider_green.setMaximum(511)
        self.horizontalSlider_green.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_green.setObjectName("horizontalSlider_green")
        self.gridLayout.addWidget(self.horizontalSlider_green, 1, 0, 1, 1)
        self.spinBox_green = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox_green.setMaximum(511)
        self.spinBox_green.setObjectName("spinBox_green")
        self.gridLayout.addWidget(self.spinBox_green, 1, 1, 1, 1)
        self.horizontalSlider_blue = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider_blue.setMaximum(511)
        self.horizontalSlider_blue.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_blue.setObjectName("horizontalSlider_blue")
        self.gridLayout.addWidget(self.horizontalSlider_blue, 2, 0, 1, 1)
        self.spinBox_blue = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox_blue.setMaximum(511)
        self.spinBox_blue.setObjectName("spinBox_blue")
        self.gridLayout.addWidget(self.spinBox_blue, 2, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.horizontalSlider_red.valueChanged['int'].connect(self.spinBox_red.setValue)
        self.spinBox_red.valueChanged['int'].connect(self.horizontalSlider_red.setValue)
        self.horizontalSlider_green.valueChanged['int'].connect(self.spinBox_green.setValue)
        self.horizontalSlider_blue.valueChanged['int'].connect(self.spinBox_blue.setValue)
        self.spinBox_blue.valueChanged['int'].connect(self.horizontalSlider_blue.setValue)
        self.spinBox_green.valueChanged['int'].connect(self.horizontalSlider_green.setValue)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

