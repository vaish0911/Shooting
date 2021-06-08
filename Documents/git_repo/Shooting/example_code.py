import sys


from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSlider, QStyle, QSizePolicy, QFileDialog
import sys
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon, QPalette                                                                                                  
from PyQt5.QtCore import Qt, QUrl, QFileInfo, QDateTime, QTime, QThreadPool, QObject, QRunnable, pyqtSignal

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThreadPool, QObject, QRunnable, pyqtSignal

class WorkerSignals(QObject):
    result = pyqtSignal(int)

class Worker(QWidget):

    def __init__ (self, task):
        super().__init__()

        self.setWindowTitle("PyQt5 Media Player")
        self.setGeometry(350, 100, 700, 500)
        self.setWindowIcon(QIcon('player.png'))
        #self.position = position
        self.signals = WorkerSignals()
        self.task = task
        p = self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)


        self.init_ui()


        self.show()


    def init_ui(self):

        # create media player object
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)


        # create  videowidget object
        videowidget = QVideoWidget()

        # Get video file info object
        self.video_info = QFileInfo()
        self.time_ = QDateTime()
        

        # create open button
        openBtn = QPushButton('Open Video')
        openBtn.clicked.connect(self.open_file)

        # create button for playing
        self.playBtn = QPushButton()
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.clicked.connect(self.play_video)

        # create slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0,0)
        self.slider.sliderMoved.connect(self.set_position)
       
        
        # create label
        self.label = QLabel()
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)


        # create hbox layout
        hboxLayout = QHBoxLayout()
        hboxLayout.setContentsMargins(0, 0, 0, 0)

        # set widgets to the hbox layout
        hboxLayout.addWidget(openBtn)
        hboxLayout.addWidget(self.playBtn)
        hboxLayout.addWidget(self.slider)


        # create vbox layout
        vboxLayout = QVBoxLayout()
        vboxLayout.addWidget(videowidget)
        vboxLayout.addLayout(hboxLayout)
        vboxLayout.addWidget(self.label)

        self.setLayout(vboxLayout)

        self.mediaPlayer.setVideoOutput(videowidget)

        # media_player signals

        self.mediaPlayer.stateChanged.connect(self.mediastate_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

    def open_file(self):

        filename,_ = QFileDialog.getOpenFileName(self, "Open Video")
        self.video_info.setFile(filename)
        start_time =  self.video_info.birthTime()
        print(start_time.toString())
        
        if filename != '':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            
            #qdebug()
            
            self.playBtn.setEnabled(True)
            self.setWindowTitle(filename)
    #import pdb; pdb.set_trace()



    #import pdb;pdb.set_trace()
    #print(filename)



    def play_video(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()


    def mediastate_changed(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playBtn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause)
                )
        else:
            self.playBtn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay)
                )

    def position_changed(self, position):
        self.slider.setValue(position)
        print("Slider_Position is ", position)
        self.task = position
        print ('Sending', self.task)
        self.signals.result.emit(self.task)
        
     

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)
        

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)


    def handle_errors(self):
        self.playBtn.setEnabled(False)
        self.label.setText('Error:' +mediaPlayer.errorStrin)


    #def run(self):
        

class Tasks(QObject):
    def __init__(self):
        super(Tasks, self).__init__()
        
        #self.pool = QThreadPool()
        #self.pool.setMaxThreadCount(1)

    def process_result(self, task):
        print ('Receiving', task )
        

    
            
            

        #self.pool.start(worker)

        #self.pool.waitForDone()
        


if __name__ == "__main__":
    import  sys

    app = QApplication(sys.argv)
    task = 1
    print("Before Value", task)
    worker = Worker(task)
    main = Tasks()
    worker.signals.result.connect(main.process_result)
    
    
    

    sys.exit(app.exec_())
