import pyqtgraph as pg
import datetime
import time


def timestamp():
    return int(time.mktime(datetime.datetime.now().timetuple()))

# This is to basically represent the epoch time values as timestamp (as specified by user)
class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLabel(text='Time', units=None)
        self.enableAutoSIPrefix(False)

    def tickStrings(self, values, scale, spacing):
        return [datetime.datetime.fromtimestamp(value).strftime("%H:%M:%S") for value in values]
