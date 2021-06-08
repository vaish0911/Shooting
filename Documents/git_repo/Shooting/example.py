from PyQt5.QtWidgets import QWidget, QGridLayout
import pyqtgraph as pg
from utils import TimeAxisItem, timestamp

from PyQt5 import QtGui
from PyQt5.QtCore import QDate, QTime, QDateTime, Qt
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QTimer, QDate, QTime, Qt, QDateTime
from pyqtgraph import PlotWidget, PlotDataItem
from datetime import datetime, date, time, timedelta
import pyqtgraph as pg
from pyqtgraph import AxisItem
import sys  # We need sys so that we can pass argv to QApplication
import numpy as np
import os
from random import randint
from utils import TimeAxisItem, timestamp
from time import mktime


class ExampleWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.plot = pg.PlotWidget(
            title="Example plot",
            labels={'left': 'Reading / mV'},
            axisItems={'bottom': TimeAxisItem(orientation='bottom')}
        )
        self.plot.setYRange(0, 5000)
        self.plot.setXRange(timestamp(), timestamp() + 100)
        self.plot.showGrid(x=True, y=True)
        import pdb;pdb.set_trace()
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.plot, 0, 0)

        self.plotCurve = self.plot.plot(pen='y')

        self.plotData = {'x': [], 'y': []}

    def updatePlot(self, newValue):
        self.plotData['y'].append(newValue)
        self.plotData['x'].append(timestamp())

        self.plotCurve.setData(self.plotData['x'], self.plotData['y'])


app = QtWidgets.QApplication(sys.argv)
main = ExampleWidget()
main.show()
sys.exit(app.exec_())