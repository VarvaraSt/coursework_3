# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'drawNet.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DrawDialog(object):
    def setupUi(self, DrawDialog):
        DrawDialog.setObjectName("DrawDialog")
        DrawDialog.resize(558, 367)
        self.gridLayout = QtWidgets.QGridLayout(DrawDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.graphicsView = QtWidgets.QGraphicsView(DrawDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy)
        self.graphicsView.setObjectName("graphicsView")
        self.gridLayout.addWidget(self.graphicsView, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit = QtWidgets.QLineEdit(DrawDialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lineEdit.setFont(font)
        self.lineEdit.setInputMask("")
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.pushButton = QtWidgets.QPushButton(DrawDialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.retranslateUi(DrawDialog)
        QtCore.QMetaObject.connectSlotsByName(DrawDialog)

    def retranslateUi(self, DrawDialog):
        _translate = QtCore.QCoreApplication.translate
        DrawDialog.setWindowTitle(_translate("DrawDialog", "Draw net"))
        self.lineEdit.setText(_translate("DrawDialog", "Имя сети"))
        self.pushButton.setText(_translate("DrawDialog", "Сохранить"))

