# -*- coding: utf-8 -*-

import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QTableWidget, QTableWidgetItem, QFileDialog, QDialog, QGraphicsScene, QGraphicsView, QCheckBox, QHBoxLayout, QHeaderView
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QPointF, QTimer
from configparser import ConfigParser
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QBrush, QPen, QPainter, QPixmap, QColor

#import pandas
import pyomo
import pyomo.opt
import pyomo.environ as pe
import logging

import networkx as nx
import draw_graph

import main_ui
import createNet_ui
import drawNet_ui
import exception_ui

IMAGE_PATH = "filename.png"
NET_PATH = ""
RESULT_IMAGE_PATH = "result.png"

class ExceptWindow(QtWidgets.QDialog, exception_ui.Ui_Dialog):
    def __init__(self, parent=None, txt = ""):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super(ExceptWindow, self).__init__(parent)
        parent.setEnabled(False)
        self.setEnabled(True)
        self.Parent = parent
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        
        self.label.setText(txt)
            
    def closeEvent(self, event):
        self.Parent.setEnabled(True)

class DrawNetWindow(QtWidgets.QDialog, drawNet_ui.Ui_DrawDialog):
    def __init__(self, parent=None):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super(DrawNetWindow, self).__init__(parent)
        parent.setEnabled(False)
        self.setEnabled(True)
        self.Parent = parent
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        
        self.scene = QGraphicsScene()
        color2 = QColor()
        color2.setNamedColor("#fdd03b")      
        self.brush = QBrush(color2)
        color = QColor()
        color.setNamedColor("#4a9396")
        self.pen = QPen(color)
        self.pen.setWidth(3)
        self.graphicsView.setScene(self.scene)
        
        self.prevPoint = QPointF()
        self.circles = []
        self.line = 0
        self.begin = 0
        self.V = set()
        self.E = set()
        self.VNum = 0
        self.pushButton.clicked.connect(self.saveNet)
        
        #self.pix = QPixmap(self.rect().size())
        #self.scene.addPixmap(self.pix)
        #self.begin, self.destination = QPointF(), QPointF()
        
        self.timer = QTimer()
        self.timer.start(100)
        self.timer.timeout.connect(self.slotTimer)       
	
        #self.setMouseTracking(True)
        self.graphicsView.viewport().installEventFilter(self)
        
        #self.scene.setSceneRect(0, 0, self.graphicsView.width(), self.graphicsView.height())
        
    def saveNet(self):
        with open(NET_PATH + str(self.lineEdit.text()) + ".txt", 'w') as file:
            file.write(str(self.VNum))
            file.write("\n")
            for v in self.V:
                file.write(str(v))
                file.write("\n")
            file.write(str(len(self.E)))
            file.write("\n")
            for e in self.E:
                file.write(str(e))
                file.write("\n")    
        self.lineEdit.setText("Готово")
        
    def slotTimer(self):
        self.timer.stop()
        self.scene.setSceneRect(0, 0, self.graphicsView.width(), self.graphicsView.height())
        
    def resizeEvent(self, event):
        self.timer.start(100)
        QtWidgets.QDialog.resizeEvent(self, event)
        
    def isInCircle(self, point):
        for circle in self.circles:
            if ((circle[0] - point.x())**2 + (circle[1] - point.y())**2)**0.5 <= circle[2]:
                return circle
        return False
        
    def mousePressEvent(self, event):
        x = event.x() - 15
        y = event.y() - 15
        if event.buttons() == QtCore.Qt.LeftButton:
            diam = 30
            delt = diam//2
            if not self.isInCircle(QPointF(x, y)):
                self.scene.addEllipse(x-delt, y-delt, diam, diam, self.pen, self.brush)
                self.VNum += 1
                self.V.add(self.VNum)
                self.begin = 0
                self.circles += [(x, y, diam//2, self.VNum)]
            else:
                self.begin = self.isInCircle(QPointF(x, y))
            
    def eventFilter(self, source, event):
        #print(event.type(), QtCore.QEvent.MouseButtonRelease)
        if event.type() == QtCore.QEvent.MouseMove:
            if event.buttons() == QtCore.Qt.LeftButton:
                if self.line:
                    self.scene.removeItem(self.line)
                if self.begin:
                    self.line = self.scene.addLine(self.begin[0], self.begin[1], event.x(), event.y(), self.pen)
                pass
        elif event.type() == QtCore.QEvent.MouseButtonRelease:
            if self.line:
                self.scene.removeItem(self.line)
            finish = self.isInCircle(QPointF(event.x(), event.y()))
            begin = self.begin
            if finish and begin and begin != finish:
                self.scene.addLine(begin[0], begin[1], finish[0], finish[1], self.pen)
                self.E.add((begin[-1], finish[-1]))
                self.E.add((finish[-1], begin[-1]))
        return QtWidgets.QDialog.eventFilter(self, source, event)    
            
    def closeEvent(self, event):
        self.Parent.setEnabled(True)     

class CreateNetWindow(QtWidgets.QDialog, createNet_ui.Ui_Create_new_net):
    def __init__(self, parent=None):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super(CreateNetWindow, self).__init__(parent)
        parent.setEnabled(False)
        self.setEnabled(True)
        self.Parent = parent
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        
        self.spinBox.valueChanged.connect(self.changeVNum)
        
        self.VNum = 0
        self.V = set()
        self.E = set()
        self.types = dict()
        self.updateTable1()
        self.updateTable2()
        
        #self.web_view = QWebEngineView()
        #self.web_view.setHtml(open("test.html").read())
        #self.horizontalLayout_6.removeWidget(self.scrollArea)
        #self.horizontalLayout_6.addWidget(self.web_view)
        
        #print(draw_graph.get_html_for_graph(self.G))
        self.label.setPixmap(QtGui.QPixmap(""))
        
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.tableWidget_2.cellChanged.connect(self.onTableChanged)
        
        self.pushButton.clicked.connect(self.saveNet)
        self.openBtn.clicked.connect(self.onOpenBtn)
        
    def onOpenBtn(self):
        path = self.FileDialog(fmt = "txt")
        if path != "":
            self.openFile(path)
        
    def openFile(self, path):
        with open(path) as f:
            v_num = int(f.readline())
            self.VNum = v_num
            for i in range (v_num):
                numbers = f.readline().split()
                v = int(numbers[0])
                self.V.add(v)
                self.types[v] = list()
                int(numbers[0])
                for j in range(1, len(numbers)):
                    num = int(numbers[j])
                    self.types[v] += [num]
            e_num = int(f.readline())
            for i in range (e_num):
                line = f.readline()
                dots = line.replace("(", "").replace(")", "").split(", ")
                self.E.add((int(dots[0]), int(dots[1])))    
        self.updateTable1()
        self.updateTable2()
        self.updateImage()
        self.spinBox.setValue(self.VNum)
        
    def saveNet(self):
        with open(NET_PATH + str(self.lineEdit.text()) + ".txt", 'w') as file:
            file.write(str(self.VNum))
            file.write("\n")
            for v in self.V:
                file.write(str(v) + " ")
                for i in range(5):
                    if self.getCheckBoxVal(v-1, i):
                        file.write(str(i + 1) + " ")
                file.write("\n")
            file.write(str(len(self.E)))
            file.write("\n")
            for e in self.E:
                file.write(str(e))
                file.write("\n")
        self.lineEdit.setText("Готово")
        
    def onTableChanged(self, row, column):
        if row != column:
            if len(self.tableWidget_2.item(row, column).text()) > 0:
                #self.E.add((min(row+1, column+1), max(row+1, column+1)))
                self.E.add((row+1, column+1))
                self.E.add((column+1, row+1))
                self.updateImage()
            else:
                #self.E.discard((min(row+1, column+1), max(row+1, column+1)))
                self.E.discard((row+1, column+1))
                self.E.discard((column+1, row+1))            
                self.updateImage()
            if self.tableWidget_2.item(column, row):
                self.tableWidget_2.item(column, row).setText(self.tableWidget_2.item(row, column).text())
            else:
                self.tableWidget_2.setItem(column, row, QTableWidgetItem(self.tableWidget_2.item(row, column).text()))
        
    def updateImage(self):
        draw_graph.save_as_png(self.V, self.E, IMAGE_PATH)
        self.label.setPixmap(QtGui.QPixmap(IMAGE_PATH))
    
    def hideTable1(self, is_checked):
        if not is_checked:
            self.verticalLayout.removeWidget(self.tableWidget)
        else:
            self.verticalLayout.insertWidget(3, self.tableWidget)
    
    def changeVNum(self, i):
        if i > self.VNum:
            for ver in range(self.VNum + 1, i + 1):
                self.V.add(ver) 
        elif i < self.VNum:
            for ver in range(self.VNum, i, -1):
                self.V.discard(ver)
        self.VNum = i
        self.updateImage()
        self.updateTable1()
        self.updateTable2()
            
    def addCheckBoxAt(self, row_number, column_number, state):
        if not self.tableWidget.cellWidget(row_number, column_number):
            checkBoxWidget = QWidget()
            checkBox = QCheckBox()
            layoutCheckBox = QHBoxLayout(checkBoxWidget)
            layoutCheckBox.addWidget(checkBox)
            layoutCheckBox.setAlignment(Qt.AlignCenter)
            layoutCheckBox.setContentsMargins(0,0,0,0)
       
            if (state == 1):
                checkBox.setChecked(True)
            else:
                checkBox.setChecked(False)
            self.tableWidget.setCellWidget(row_number,column_number, checkBoxWidget)   
            
    def getCheckBoxVal(self, row, column):
        item = self.tableWidget.cellWidget(row,column)
        checkB = item.layout().itemAt(0).widget()
        if checkB.isChecked():
            return True
        return False
        
    def updateTable1(self):
        self.tableWidget.setRowCount(self.VNum)
        for i in range(self.VNum):
            for j in range(5):
                if self.types.get(i+1) and j+1 in self.types.get(i+1):
                    self.addCheckBoxAt(i, j, 1)
                else:
                    self.addCheckBoxAt(i, j, 0)
    
    def updateTable2(self):
        self.tableWidget_2.setRowCount(self.VNum)
        self.tableWidget_2.setColumnCount(self.VNum)
        if len(self.E) > 0:
            for e in self.E:
                self.tableWidget_2.setItem(e[0]-1, e[1]-1, QTableWidgetItem("+"))
        
    def openExceptWindow(self, txt = ""):
        window = ExceptWindow(self, txt = txt)
        window.show()     
        
    def closeEvent(self, event):
        self.Parent.setEnabled(True)   
        
    def FileDialog(directory='', forOpen=True, fmt='', isFolder=False):
        #options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        #options |= QFileDialog.DontUseCustomDirectoryIcons
        dialog = QFileDialog()
        #dialog.setOptions(options)
    
        dialog.setFilter(dialog.filter() | QtCore.QDir.Hidden)
    
        # ARE WE TALKING ABOUT FILES OR FOLDERS
        if isFolder:
            dialog.setFileMode(QFileDialog.DirectoryOnly)
        else:
            dialog.setFileMode(QFileDialog.AnyFile)
        # OPENING OR SAVING
        dialog.setAcceptMode(QFileDialog.AcceptOpen) if forOpen else dialog.setAcceptMode(QFileDialog.AcceptSave)
    
        # SET FORMAT, IF SPECIFIED
        if fmt != '' and isFolder is False:
            dialog.setDefaultSuffix(fmt)
            dialog.setNameFilters([f'{fmt} (*.{fmt})'])
    
        # SET THE STARTING DIRECTORY
        if directory != '':
            dialog.setDirectory(str(directory))
        #else:
        #    dialog.setDirectory(str(ROOT_DIR))
    
        if dialog.exec_() == QDialog.Accepted:
            
            path = dialog.selectedFiles()[0]  # returns a list
            return path
        else:
            return ''        

class mainWindow(QtWidgets.QMainWindow, main_ui.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна 
        self.pushButton_3.clicked.connect(self.editNet)
        self.pushButton_2.clicked.connect(self.count)
        self.pushButton.clicked.connect(self.save)
        self.actionCreate_new.triggered.connect(self.openNetWindow)
        self.actionOpen.triggered.connect(self.openFile)
        self.actionDraw_new.triggered.connect(self.openDrawWindow)
        
        self.tableWidget.cellChanged.connect(self.onTable1Changed)
        self.tableWidget_2.cellChanged.connect(self.onTable2Changed)
        
        self.res_picture.setPixmap(QtGui.QPixmap(""))
        
        self.V = set()
        self.E = set()
        self.path = ""
        
        self.alpha = dict()
        self.beta = dict()
        self.demand = dict()
        self.limit = dict()
        
        self.losses = dict()
        self.bandwidth = dict()
        
        self.y = dict()
        
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.res_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
    def updateImage(self):
        draw_graph.save_as_png_flows(self.V, self.E, self.y, RESULT_IMAGE_PATH)
        self.res_picture.setPixmap(QtGui.QPixmap(RESULT_IMAGE_PATH))    
        
    def save(self):
        with open(self.path[:-4]+"_2.txt", 'w') as f:
            f.write(str(self.alpha))
            f.write("\n")
            f.write(str(self.beta))
            f.write("\n")
            f.write(str(self.demand))
            f.write("\n")
            f.write(str(self.limit))
            f.write("\n")
            f.write(str(self.losses))
            f.write("\n") 
            f.write(str(self.bandwidth))
            f.write("\n")  
        
    def count(self):
        model = pe.ConcreteModel()
        
        model.N = pe.Set(initialize = sorted(list(self.V)))
        model.A = pe.Set(initialize = list(self.E),
                 within=model.N*model.N)
        
        model.a = pe.Param(model.N, initialize=self.alpha, doc='Alpha cost')
        model.b = pe.Param(model.N, initialize=self.beta, doc='Beta cost')
        model.maxX = pe.Param(model.N, initialize=self.limit, doc='Max production')
        model.d = pe.Param(model.N, initialize=self.demand, doc='Demand')
        
        #def delta_init(model, i, j):
        #    return 0.02
        model.delta = pe.Param(model.A, initialize=self.losses, doc="Loss")
        model.maxY = pe.Param(model.A, initialize=self.bandwidth, doc="MaxY")
        
        def x_bounds(model, i):
            return (0, model.maxX[i])
        model.x = pe.Var(model.N, bounds=x_bounds, doc='Production')
        
        def y_bounds(model, i, j):
            if  model.maxY[(i, j)] == 0: 
                return (0, None)
            return (0, model.maxY[(i, j)])        
        model.y = pe.Var(model.A, bounds=y_bounds, doc='Flow')
        
        def total_rule(model):
            return sum(model.a[i]*model.x[i] + model.b[i] for i in model.N)
        model.total_cost = pe.Objective(rule=total_rule, sense=pe.minimize, doc="Total cost")
        
        def balance_rule(model, i):
            inFlow = model.x[i] + sum(model.y[j, i]*(1 - model.delta[j, i]) for j in model.N if (j, i) in model.A)
            outFlow = model.d[i] + sum(model.y[i, j] for j in model.N if (i, j) in model.A)
            return inFlow == outFlow
        model.balance = pe.Constraint(model.N, rule=balance_rule)
        
        opt = pe.SolverFactory('glpk', executable = "C:\winglpk-4.65\glpk-4.65\w64\glpsol")
        results = opt.solve(model, tee = True)
        
        #self.plainTextEdit.setPlainText(results)
        
        #for v in model.component_objects(pe.Var, active=True):
         #   print("Variable",v)  
          #  for index in v:
           #     print ("   ",index, pe.value(v[index]))
           
        for edge in model.y:
            flow = pe.value(model.y[edge])
            if flow > 0:
                self.y[edge] = flow
        
        self.res_table.setRowCount(len(self.V))
        for v in model.x:
            self.res_table.setItem(v-1, 0, QTableWidgetItem(str(pe.value(model.x[v]))))            
        
        self.label_2.setText(str(pe.value(model.total_cost.expr)))
        print(pe.value(model.total_cost.expr))
        self.updateImage()
        
        
    def onTable1Changed(self, row, column):
        num = float(self.tableWidget.item(row, column).text())
        if column == 0:
            self.alpha[row+1] = num
        elif column == 1:
            self.beta[row+1] = num
        elif column == 2:
            self.demand[row+1] = num
        elif column == 3:
            self.limit[row+1] = num
            
    def onTable2Changed(self, row, column):
        num = float(self.tableWidget_2.item(row, column).text())
        pairTxt = self.tableWidget_2.verticalHeaderItem(row).text()
        dots = pairTxt.replace("(", "").replace(")", "").split(", ")
        pair = (int(dots[0]), int(dots[1]))
        pair2 = (int(dots[1]), int(dots[0]))
        if column == 0:
            self.losses[pair] = num
            self.losses[pair2] = num
        elif column == 1:
            self.bandwidth[pair] = num
            self.bandwidth[pair2] = num
            
    def fillTable1(self):
        column = 0
        for row in range(self.tableWidget.rowCount()):
            key = int(self.tableWidget.verticalHeaderItem(row).text())
            self.tableWidget.setItem(row, column, QTableWidgetItem(str(self.alpha[key])))
        column = 1
        for row in range(self.tableWidget.rowCount()):
            key = int(self.tableWidget.verticalHeaderItem(row).text())
            self.tableWidget.setItem(row, column, QTableWidgetItem(str(self.beta[key])))
        column = 2
        for row in range(self.tableWidget.rowCount()):
            key = int(self.tableWidget.verticalHeaderItem(row).text())
            self.tableWidget.setItem(row, column, QTableWidgetItem(str(self.demand[key]))) 
        column = 3
        for row in range(self.tableWidget.rowCount()):
            key = int(self.tableWidget.verticalHeaderItem(row).text())
            self.tableWidget.setItem(row, column, QTableWidgetItem(str(self.limit[key])))          
            
    def fillTable2(self):
        column = 0
        for row in range(self.tableWidget_2.rowCount()):
            keyTxt = self.tableWidget_2.verticalHeaderItem(row).text()
            dots = keyTxt.replace("(", "").replace(")", "").split(", ")
            pair = (int(dots[0]), int(dots[1]))
            self.tableWidget_2.setItem(row, column, QTableWidgetItem(str(self.losses[pair])))
    
    def openFile(self):
        self.path = self.FileDialog(fmt = 'txt')
        if self.path != "":
            try:
                path = self.path
                path2 = path[:-4] + "_2.txt"
                with open(path) as f:
                    v_num = int(f.readline())
                    for i in range (v_num):
                        self.V.add(int(f.readline()))
                        self.alpha[i+1] = 0
                        self.beta[i+1] = 0
                        self.demand[i+1] = 0
                        self.limit[i+1] = 0
                    e_num = int(f.readline())
                    for i in range (e_num):
                        line = f.readline()
                        dots = line.replace("(", "").replace(")", "").split(", ")
                        pair = (int(dots[0]), int(dots[1]))
                        pair2 = (int(dots[1]), int(dots[0]))
                        self.E.add(pair)
                        self.losses[pair] = 0
                        self.losses[pair2] = 0
                        self.bandwidth[pair] = 0
                        self.bandwidth[pair2] = 0
                try:
                    with open(path2) as f:
                        alpha_line = f.readline().replace("{", "").replace("}", "").replace(" ", "")
                        for pair in alpha_line.split(","):
                            key = int(pair.split(":")[0])
                            val = float(pair.split(":")[1])
                            self.alpha[key] = val
                            
                        alpha_line = f.readline().replace("{", "").replace("}", "").replace(" ", "")
                        for pair in alpha_line.split(","):
                            key = int(pair.split(":")[0])
                            val = float(pair.split(":")[1])
                            self.beta[key] = val
                            
                        alpha_line = f.readline().replace("{", "").replace("}", "").replace(" ", "")
                        for pair in alpha_line.split(","):
                            key = int(pair.split(":")[0])
                            val = float(pair.split(":")[1])
                            self.demand[key] = val
                        
                        alpha_line = f.readline().replace("{", "").replace("}", "").replace(" ", "")
                        for pair in alpha_line.split(","):
                            key = int(pair.split(":")[0])
                            val = float(pair.split(":")[1])
                            self.limit[key] = val
                            
                        alpha_line = f.readline().replace("{", "").replace("}", "").replace(" ", "")
                        alpha_line = alpha_line.replace("(", "").replace(")", "").replace("\n", "")
                        lst = alpha_line.split(",")
                        for i in range(0, len(lst), 2):
                            s1 = lst[i]
                            s2 = lst[i+1]
                            pair = (int(s1), int(s2.split(":")[0]))
                            val = float(s2.split(":")[1])
                            self.losses[pair] = val
                            
                        alpha_line = f.readline().replace("{", "").replace("}", "").replace(" ", "")
                        alpha_line = alpha_line.replace("(", "").replace(")", "").replace("\n", "")
                        if len(alpha_line) > 0:
                            lst = alpha_line.split(",")
                            for i in range(0, len(lst), 2):
                                s1 = lst[i]
                                s2 = lst[i+1]
                                pair = (int(s1), int(s2.split(":")[0]))
                                val = float(s2.split(":")[1])
                                self.bandwidth[pair] = val
                except Exception as ex:
                    print("There is no second file yet")
                self.updateTables()
                self.fillTable2()
                self.fillTable1()
            except Exception as ex:
                print(ex)
                self.openExceptWindow("Неверный формат файла")
        
    def updateTables(self):
        self.tableWidget.setRowCount(len(self.V))
        self.tableWidget_2.setRowCount(len(self.E) // 2)
        self.tableWidget_2.setVerticalHeaderLabels(map(str, [connection for connection in self.E if connection[0] < connection[1]]))
    
    def openNetWindow(self):
        window = CreateNetWindow(self)
        window.show()
        
    def openExceptWindow(self, txt = ""):
        window = ExceptWindow(self, txt = txt)
        window.show()    
        
    def openDrawWindow(self):
        window = DrawNetWindow(self)
        window.show()
        #self.installEventFilter(window)
        
    def editNet(self):
        window = CreateNetWindow(self)
        window.show()    
        window.openFile(self.path)
        
    def FileDialog(directory='', forOpen=True, fmt='', isFolder=False):
        #options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        #options |= QFileDialog.DontUseCustomDirectoryIcons
        dialog = QFileDialog()
        #dialog.setOptions(options)
    
        dialog.setFilter(dialog.filter() | QtCore.QDir.Hidden)
    
        # ARE WE TALKING ABOUT FILES OR FOLDERS
        if isFolder:
            dialog.setFileMode(QFileDialog.DirectoryOnly)
        else:
            dialog.setFileMode(QFileDialog.AnyFile)
        # OPENING OR SAVING
        dialog.setAcceptMode(QFileDialog.AcceptOpen) if forOpen else dialog.setAcceptMode(QFileDialog.AcceptSave)
    
        # SET FORMAT, IF SPECIFIED
        if fmt != '' and isFolder is False:
            dialog.setDefaultSuffix(fmt)
            dialog.setNameFilters([f'{fmt} (*.{fmt})'])
    
        # SET THE STARTING DIRECTORY
        if directory != '':
            dialog.setDirectory(str(directory))
        #else:
        #    dialog.setDirectory(str(ROOT_DIR))
    
        if dialog.exec_() == QDialog.Accepted:
            
            path = dialog.selectedFiles()[0]  # returns a list
            return path
        else:
            return ''        
            
def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = mainWindow()  # Создаём объект класса MyApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение
            
if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()