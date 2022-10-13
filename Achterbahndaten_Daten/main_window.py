

import os
import sys
import achterbahn
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QFileInfo
from PyQt5.QtWidgets import QFileDialog
import matplotlib as plt
plt.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


Ui_MainWindow, WindowBaseClass = uic.loadUiType("main_window.ui")

class MyDialog(WindowBaseClass, Ui_MainWindow):
    def __init__(self, parent=None):
        WindowBaseClass.__init__(self, parent)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("Analyse-Fenster")
        self.readFile.clicked.connect(self.getFile)
        self.calibrationButton.clicked.connect(self.plotAccs)
        self.interestingDataButton.clicked.connect(self.dataProperties)
        self.loopsFinderButton.clicked.connect(self.plotEllipse)

    def getFile(self):
        global path
        path = QFileDialog.getOpenFileName()[0]
        name = QFileInfo(path).fileName()
        self.filename.setText(name)
        self.getInterval()

    def getInterval(self):
        fileDir = QFileInfo(path).absolutePath()
        global  path_json
        path_json = os.path.join(fileDir, 'notes.json')
        interval = achterbahn.Achterbahn(path, path_json).getJsonFile()
        self.beginInterval_1.setText(str(interval[0][0]))
        self.beginInterval_2.setText(str(interval[0][1]))
        self.riseInterval_1.setText(str(interval[1][0]))
        self.riseInterval_2.setText(str(interval[1][1]))

    @pyqtSlot()
    def dataProperties(self):
        maximum = achterbahn.Achterbahn(path, path_json).maxAccs()[0]
        time = achterbahn.Achterbahn(path, path_json).maxAccs()[1:]
        frequency = achterbahn.Achterbahn(path, path_json).frequencyAccs()
        weightlessness = achterbahn.Achterbahn(path, path_json).weightlessness()
        angle = achterbahn.Achterbahn(path, path_json).angle()
        self.coasterInterestingData.setPlainText("***************************************************************************************" + '\n' +
                                                 "Maximale Beschleunigungen in alle Richtungen:" + '\n' +
                                                 "x Richtung: " + str(round(maximum[0], 2)) + "g  "+ "um " + str(round(time[0], 2)) + "s" +'\n' +
                                                 "y Richtung: " + str(round(maximum[1], 2)) + "g  " + "um " + str(round(time[1], 2)) + "s" + '\n' +
                                                 "z Richtung: " + str(round(maximum[2], 2)) + "g  "+ "um " + str(round(time[2], 2)) + "s"+ '\n' +
                                                 "***************************************************************************************" + '\n' +
                                                 "Häufigkeit besonders hoher Beschleunigungswerte: " + str(round(frequency, 4)*100) + "%" + '\n' +
                                                 "***************************************************************************************" + '\n'
                                                 "Anzahl der Zeitpunkte gefü̈hlter 'Schwerelosigkeit' wä̈hrend der Fahrt: " + str(round(weightlessness * 100, 2)) + "%" + '\n' +
                                                 "***************************************************************************************" + '\n'
                                                 "Winkel des Anstiegs am Lift Hill der Achterbahn: " + str(round(angle, 2)) + " Grad")

    @pyqtSlot()
    def plotAccs(self):
        data1 = achterbahn.Achterbahn(path, path_json)
        data2 = achterbahn.Achterbahn(path, path_json)
        x_axis = data1.filter()[:, 0]
        acc_x = data1.filter()[:, 1]
        acc_y = data1.filter()[:, 2]
        acc_z = data1.filter()[:, 3]
        acc_x_after = data2.afterCalibration()[0][:, 1]
        acc_y_after = data2.afterCalibration()[0][:, 2]
        acc_z_after = data2.afterCalibration()[0][:, 3]
        acc_abs = data2.afterCalibration()[1]
        fig = MyFigure1(width=20, height=10, dpi=100)
        fig.plotOriginal(x_axis, acc_x, acc_y, acc_z)
        fig.plotAfterCalibration(x_axis, acc_x_after, acc_y_after, acc_z_after, acc_abs)

    @pyqtSlot()
    def plotEllipse(self):
        self.interval_1 = float(self.interval1.text())
        self.interval_2 = float(self.interval2.text())
        self.minLoopLength = int(self.minLoop.text())
        self.maxLoopLength = int(self.maxLoop.text())
        self.tol = float(self.tolerence.text())
        self.minXAmp = float(self.minX.text())
        self.minZAmp = float(self.minZ.text())
        data = achterbahn.Achterbahn(path, path_json)
        x_axis = data.filter()[:, 0]
        acc_x_after = data.afterCalibration()[0][:, 1]
        acc_y_after = data.afterCalibration()[0][:, 2]
        acc_z_after = data.afterCalibration()[0][:, 3]
        fig = MyFigure2(width=20, height=10, dpi=100)
        fig.plotOriginal(x_axis, acc_x_after, acc_y_after, acc_z_after)
        ellipse = achterbahn.Achterbahn(path, path_json).Ellipse(self.interval_1, self.interval_2,
                                                                 self.minLoopLength, self.maxLoopLength,
                                                                 self.tol, self.minXAmp, self.minZAmp)
        if ellipse:
            for i in ellipse:
                interval_opt = i[0]
                ellipsen_x_opt = i[1]
                ellipsen_z_opt = i[2]
                fig.plotEllipse(interval_opt, ellipsen_x_opt, ellipsen_z_opt)



class MyFigure1(FigureCanvas):

    def __init__(self, width, height, dpi):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MyFigure1, self).__init__(self.fig)
        self.setWindowTitle("Achterbahn")
        self.axes1 = self.fig.add_subplot(211)
        self.axes2 = self.fig.add_subplot(212)
        self.axes1.set_xlabel("Times(s)")
        self.axes1.set_ylabel("Accs(g)")
        self.axes2.set_xlabel("Times(s)")
        self.axes2.set_ylabel("Accs(g)")
        self.axes1.set_title("Beschleunigungs- Zeit-Diagramme vor der Kalibrierung")
        self.axes2.set_title("Beschleunigungs- Zeit-Diagramme nach der Kalibrierung")

    def plotOriginal(self, t, x, y, z):
        self.axes1.plot(t, x, color='r', label='x')
        self.axes1.plot(t, y, color='g', label='y')
        self.axes1.plot(t, z, color='b', label='z')
        self.axes1.legend()
        self.draw()
        self.show()

    def plotAfterCalibration(self, t, x_after, y_after, z_after, abs):
        self.axes2.plot(t, x_after, color='r', label='rx')
        self.axes2.plot(t, y_after, color='g', label='ry')
        self.axes2.plot(t, z_after, color='b', label='rz')
        self.axes2.plot(t, abs, color='k', label='abs')
        self.axes2.legend()
        self.draw()
        self.show()

class MyFigure2(FigureCanvas):
    def __init__(self, width, height, dpi):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MyFigure2, self).__init__(self.fig)
        self.setWindowTitle("Achterbahn")

    def plotOriginal(self, t, x, y, z):
        self.axes = self.fig.add_subplot(111)
        self.axes.plot(t, x, color='r', label='rx', linewidth=0.5)
        self.axes.plot(t, y, color='g', label='ry', linewidth=0.5)
        self.axes.plot(t, z, color='b', label='rz', linewidth=0.5)
        self.axes.set_xlabel("Times(s)")
        self.axes.set_ylabel("Accs(g)")
        self.axes.set_title("Ellipse")
        self.axes.legend()
        self.draw()
        self.show()

    def plotEllipse(self, t_ellipse, x_ellipse, z_ellipse):
        self.axes.plot(t_ellipse, x_ellipse, color='c', linewidth=2)
        self.axes.plot(t_ellipse, z_ellipse, color='m', linewidth=2)
        self.draw()
        self.show()



if __name__ == "__main__":
    if QtCore.QCoreApplication.instance() is not None:
        app = QtCore.QCoreApplication.instance()
    else:
        app = QtWidgets.QApplication(sys.argv)

    dialog = MyDialog()
    dialog.show()
    sys.exit(app.exec_())

