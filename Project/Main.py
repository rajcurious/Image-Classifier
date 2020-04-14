import sys
from PyQt5.QtWidgets import*
from PyQt5 import QtGui
from PyQt5 import QtCore

import transfer_learning

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Image Classification'
        self.left = 200
        self.top = 200
        self.width = 786
        self.height = 580
        self.queryimg=None
        self.dir_path=None
        self.initUI()
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.threadpool = QtCore.QThreadPool()

    def initUI(self):
        self.central=QWidget()
        self.setCentralWidget(self.central)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.mainbox=QVBoxLayout()
        self.central.setLayout(self.mainbox)
        self.labelmain=QLabel()
        self.labelmain.setAlignment(QtCore.Qt.AlignHCenter)
        self.labelmain.setMaximumHeight(50)
        self.labelmain.setText("Image Classification")

        font=QtGui.QFont('SansSerif',20)
        self.labelmain.setFont(font)

        self.mainbox.addWidget(self.labelmain)
        self.createUI()

        self.show()


    def createUI(self):
        self.groupbox=QGroupBox()
        self.btn1 = QPushButton(self)
        self.btn1.setText('Select Directory')
        self.btn1.clicked.connect(self.openDirectoryNameDialog)
        self.btn2=QPushButton(self)
        self.btn2.setText('Start')
        self.btn2.setDisabled(True)
        self.btn2.clicked.connect(self.start)

        self.box1=QHBoxLayout()
        self.box1.addWidget(self.btn1)
        self.box1.addWidget(self.btn2)
        self.groupbox.setLayout(self.box1)
        self.groupbox.setMaximumHeight(60)

        self.groupbox2=QGroupBox()
        self.groupbox2.setMaximumWidth(2000)
        self.queryLayout = QHBoxLayout()
        self.groupbox2.setLayout(self.queryLayout)

        self.querybtn=QPushButton()
        self.querybtn.setText('Select Query Image')

        self.radiogroup=QGroupBox()
        self.radiobox=QHBoxLayout()
        self.styleradio=QRadioButton()
        self.styleradio.setChecked(True)
        self.styleradio.setText('Filter by style')
        self.style_content_radio=QRadioButton()
        self.style_content_radio.setText('Filter by style and Content')
        self.radiobox.addWidget(self.styleradio)
        self.radiobox.addWidget(self.style_content_radio)
        self.radiogroup.setMaximumHeight(50)
        self.radiogroup.setLayout(self.radiobox)

        self.progressbar = QProgressBar()
        self.progressbar.setValue(0)
        self.progressbar.setContentsMargins(10, 10, 10, 10)
        self.progressbar.hide()

        self.mainbox.addWidget(self.groupbox)
        self.mainbox.addWidget(self.querybtn)
        self.mainbox.addWidget(self.radiogroup)
        self.mainbox.addWidget(self.progressbar)
        self.mainbox.addWidget(self.groupbox2)
        self.querybtn.clicked.connect(self.openFileNameDialog)
        #self.setLayout(self.mainbox)



    def start(self):
        self.progressbar.setVisible(True)
        self.progressbar.setValue(0)

        if self.styleradio.isChecked():
            option='style'
        else:
            option='style-content'
        thread=Worker(self.dir_path,self.queryimg,option)
        thread.signals.finished.connect(self.openResult)
        thread.signals.progress.connect(self.progress_fn)
        self.threadpool.start(thread)


    def openDirectoryNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName= QFileDialog.getExistingDirectory(self,"Select Directory")
        if fileName:
            print(fileName)
            self.dir_path=fileName
        if self.queryimg!=None and self.dir_path != None:
            self.btn2.setEnabled(True)


    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Select Query Image", "","Image files (*.jpg *.gif *.png)")
        if fileName:
            self.queryimg = fileName
            self.im1 = QtGui.QPixmap(fileName).scaled(400, 300, QtCore.Qt.KeepAspectRatio)
            self.label1 = QLabel()
            self.label1.setAlignment(QtCore.Qt.AlignCenter)
            self.label1.setPixmap(self.im1)
            if self.queryLayout.count()==0:
                self.queryLayout.addWidget(self.label1)
            else:
                self.queryLayout.itemAt(0).widget().setParent(None)
                self.queryLayout.addWidget(self.label1)
            if self.queryimg!=None and self.dir_path != None:
                self.btn2.setEnabled(True)
                                           ## USE THIS TO GET PATH OF QUERY IMAGE...



    def progress_fn(self, n):
        print("%d%% done" % n)
        self.progressbar.setValue(n)

    def openResult(self,data):  ## To BE CALLED AFTER MATCHING IMAGES ARE FOUND (USE this function to pass result)
        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWindowIcon(QtGui.QIcon('icon.png'))
        self.scroll.setWindowTitle('Output')
        self.scroll.setGeometry(400,200,900,500)
        self.newbox = QGroupBox()
        self.sub = QHBoxLayout()
        self.grid = QGridLayout()

        for i in range(len(data)):
            self.im1 = QtGui.QPixmap(data[i]['path']).scaled(250, 250, QtCore.Qt.KeepAspectRatio)
            self.label1 = QLabel()
            self.label1.setPixmap(self.im1)
            self.grid.addWidget(self.label1, i / 4, i % 4)

        self.newbox.setLayout(self.grid)
        self.scroll.setWidget(self.newbox)
        self.scroll.show()


class Worker(QtCore.QRunnable):
    def __init__(self,dir_name,queryimg,option):
        super(Worker, self).__init__()
        self.dir_name=dir_name
        self.option=option
        self.queryimg = queryimg
        self.signals = WorkerSignals()
        self.progress_callback = self.signals.progress


    #@pyqtSlot()
    def run(self):
        print(self.dir_name,self.queryimg)
        if self.option=='style-content':
            print('checked')
            result=transfer_learning.sorted_paint_result_Json(SEARCH_PATH=self.queryimg,DIR_PATH=self.dir_name,progress_func=self.progress_callback)
        elif self.option=='style':
            print('checked style')
            result=transfer_learning.sorted_result_Json(SEARCH_PATH=self.queryimg,DIR_PATH=self.dir_name,progress_func=self.progress_callback)
        print(result)
        self.signals.finished.emit(result)




class WorkerSignals(QtCore.QObject):
    progress = QtCore.pyqtSignal(float)
    finished=QtCore.pyqtSignal(list)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())