import sys
import achterbahn
import os
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem

Ui_MainWindow, WindowBaseClass = uic.loadUiType("ranking_window.ui")

class MyDialog(WindowBaseClass, Ui_MainWindow):
    def __init__(self, parent=None):
        WindowBaseClass.__init__(self, parent)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle("Ranking-Fenster")
        self.readFile.clicked.connect(self.getFile)
        self.startButton.clicked.connect(self.order)
        self.table1.setColumnCount(5)
        self.table1.setRowCount(0)
        self.table1.setHorizontalHeaderLabels(
            ['Name', 'Maximale Beschleunigung (g)', 'Häufigkeit besonders hoher Beschleunigungswerte (%)',
             'Anzahl der Zeitpunkte gefü̈hlter "Schwerelosigkeit" (%)',
             'Winkel des Anstiegs am Lift Hill der Achterbahn (Grad)'])
        self.table1.horizontalHeader().resizeSection(0, 100)
        self.table1.horizontalHeader().resizeSection(1, 250)
        self.table1.horizontalHeader().resizeSection(2, 300)
        self.table1.horizontalHeader().resizeSection(3, 300)
        self.table1.horizontalHeader().resizeSection(4, 350)
        self.table2.setColumnCount(5)
        self.table2.setRowCount(0)
        self.table2.setHorizontalHeaderLabels(
            ['Name', 'Maximale Beschleunigung (g)', 'Häufigkeit besonders hoher Beschleunigungswerte (%)',
             'Anzahl der Zeitpunkte gefü̈hlter "Schwerelosigkeit" (%)',
             'Winkel des Anstiegs am Lift Hill der Achterbahn (Grad)'])
        self.table2.horizontalHeader().resizeSection(0, 100)
        self.table2.horizontalHeader().resizeSection(1, 250)
        self.table2.horizontalHeader().resizeSection(2, 300)
        self.table2.horizontalHeader().resizeSection(3, 300)
        self.table2.horizontalHeader().resizeSection(4, 350)

    @pyqtSlot()
    def getFile(self):
        rootPath = QFileDialog.getExistingDirectory(self)
        self.filename.setText(rootPath)
        self.coasterDataTable(rootPath)

    def coasterDataTable(self, rootPath):
        for root, dirs, files in os.walk(rootPath):
            i = 0
            for dir in dirs:
                self.table1.setRowCount(self.table1.rowCount() + 1)
                j = 0
                coasterName = dir
                dirPath = os.path.join(root, dir)
                accsPath = os.path.join(dirPath, 'accelerometer_log.txt')
                jsonPath = os.path.join(dirPath, 'notes.json')
                maxAccsAbs = achterbahn.Achterbahn(accsPath, jsonPath).maxAccsAbs()
                frequencyAccs = achterbahn.Achterbahn(accsPath, jsonPath).frequencyAccs()
                weightlessness = achterbahn.Achterbahn(accsPath, jsonPath).weightlessness()
                angle = achterbahn.Achterbahn(accsPath, jsonPath).angle()
                item1 = QTableWidgetItem(coasterName)
                item2 = QTableWidgetItem(str(round(maxAccsAbs, 2)))
                item3 = QTableWidgetItem(str(round(frequencyAccs, 4) * 100))
                item4 = QTableWidgetItem(str(round(weightlessness * 100, 2)))
                item5 = QTableWidgetItem(str(round(angle, 2)))
                item1.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                item2.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                item3.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                item4.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                item5.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.table1.setItem(i, j, item1)
                self.table1.setItem(i, j + 1, item2)
                self.table1.setItem(i, j + 2, item3)
                self.table1.setItem(i, j + 3, item4)
                self.table1.setItem(i, j + 4, item5)
                i += 1

    @pyqtSlot()
    def order(self):
        coaster = []
        for i in range(0, self.table1.rowCount()):
            data = []
            for j in range(0, 5):
                if j == 0:
                    item = self.table1.item(i, j).text()
                else:
                    item = float(self.table1.item(i, j).text())
                data.append(item)
            coaster.append(data)
        if self.comboBox.currentIndex() == 0:
            rankMaxAccsAbs = sorted(coaster, key=(lambda x:x[1]), reverse=True)
            self.table2.setRowCount(0)
            for i in range(0, self.table1.rowCount()):
                self.table2.setRowCount(self.table2.rowCount() + 1)
                for j in range(0, 5):
                    newItem = QTableWidgetItem(str(rankMaxAccsAbs[i][j]))
                    newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.table2.setItem(i, j, newItem)
        elif self.comboBox.currentIndex() == 1:
            rankFrequencyAccs = sorted(coaster, key=(lambda x:x[2]), reverse=True)
            self.table2.setRowCount(0)
            for i in range(0, self.table1.rowCount()):
                self.table2.setRowCount(self.table2.rowCount() + 1)
                for j in range(0, 5):
                    newItem = QTableWidgetItem(str(rankFrequencyAccs[i][j]))
                    newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.table2.setItem(i, j, newItem)
        elif self.comboBox.currentIndex() == 2:
            rankWeightlessness = sorted(coaster, key=(lambda x: x[3]), reverse=True)
            self.table2.setRowCount(0)
            for i in range(0, self.table1.rowCount()):
                self.table2.setRowCount(self.table2.rowCount() + 1)
                for j in range(0, 5):
                    newItem = QTableWidgetItem(str(rankWeightlessness[i][j]))
                    newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.table2.setItem(i, j, newItem)
        else:
            rankAngle = sorted(coaster, key=(lambda x: x[4]), reverse=True)
            self.table2.setRowCount(0)
            for i in range(0, self.table1.rowCount()):
                self.table2.setRowCount(self.table2.rowCount() + 1)
                for j in range(0, 5):
                    newItem = QTableWidgetItem(str(rankAngle[i][j]))
                    newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.table2.setItem(i, j, newItem)

if __name__ == "__main__":

    if QtCore.QCoreApplication.instance() is not None:
        app = QtCore.QCoreApplication.instance()
    else:
        app = QtWidgets.QApplication(sys.argv)

    dialog = MyDialog()
    dialog.show()
    sys.exit(app.exec_())


