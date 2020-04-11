import sys
from PyQt5.QtWidgets import*
from PyQt5 import QtGui
from PyQt5 import QtCore

import imghdr
import os
import transfer_learning

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Image Classification'
        self.left = 200
        self.top = 200
        self.width = 640
        self.height = 440
        self.queryimg=None
        self.dir_path=None
        self.initUI()
        self.threadpool = QtCore.QThreadPool()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.mainbox=QVBoxLayout()
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

        self.mainbox.addWidget(self.groupbox)
        self.mainbox.addWidget(self.querybtn)
        #self.mainbox.addWidget(self.progressbar)
        self.mainbox.addWidget(self.groupbox2)
        self.querybtn.clicked.connect(self.openFileNameDialog)
        self.setLayout(self.mainbox)


    def start(self):
        self.startProgress()
        thread=Worker(self.dir_path,self.queryimg)
        thread.signals.finished.connect(self.openResult)
        thread.signals.progress.connect(self.progress_fn)
        self.threadpool.start(thread)
        #result=transfer_learning.sorted_paint_result_Json(SEARCH_PATH=self.queryimg,DIR_PATH=self.dir_path)
        #result=transfer_learning.sorted_result_Json(SEARCH_PATH=self.queryimg,
         #                                    DIR_PATH=self.dir_path)
        #self.openResult(result)

    def startProgress(self):
        self.progressWindow=QMdiSubWindow()
        self.progressWindow.setWindowTitle('Loading ...')
        self.groupprogress=QGroupBox()
        self.vboxprog=QVBoxLayout()
        self.groupprogress.setLayout(self.vboxprog)
        self.labelprogress=QLabel()
        self.labelprogress.setText('Please wait, it may take few seconds')
        self.labelprogress.setContentsMargins(10,10,10,10)
        self.vboxprog.addWidget(self.labelprogress)
        self.progressWindow.setGeometry(300,300,400,100)
        self.progressbar=QProgressBar()
        self.progressbar.setValue(0)
        self.progressbar.setContentsMargins(10,10,10,10)
        self.vboxprog.addWidget(self.progressbar)
        self.progressWindow.setWidget(self.groupprogress)

        self.progressWindow.show()

    def openDirectoryNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName= QFileDialog.getExistingDirectory(self,"Select Directory")
        if fileName:
            print(fileName)
            self.dir_path=fileName
        if self.queryimg!=None and self.dir_path != None:
            self.btn2.setEnabled(True)
            #self.openResult(self.getListOfFiles(fileName))  ## THIS FUNCTION PROVIDES A LIST OF IMAGE FILES UNDER SELECTED DIRECTORY

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



    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)

    def progress_fn(self, n):
        print("%d%% done" % n)
        self.progressbar.setValue(n)

    def openResult(self,data):
        self.progressWindow.close()
        ## To BE CALLED AFTER MATCHING IMAGES ARE FOUND (USE this function to pass result)
        print(data)
        self.scroll=QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)

        self.newbox=QGroupBox()
        self.sub=QHBoxLayout()
        self.grid = QGridLayout()

        for i in range(len(data)):
            self.im1 = QtGui.QPixmap(data[i]['path']).scaled(250, 250,QtCore.Qt.KeepAspectRatio)
            self.label1 = QLabel()
            self.label1.setPixmap(self.im1)
            self.grid.addWidget(self.label1,i/6,i%6)

        self.newbox.setLayout(self.grid)
        self.scroll.setWidget(self.newbox)
        self.scroll.show()




class Worker(QtCore.QRunnable):
    def __init__(self,dir_name,queryimg):
        super(Worker, self).__init__()
        self.dir_name=dir_name
        self.queryimg = queryimg
        self.signals = WorkerSignals()
        self.progress_callback = self.signals.progress


    #@pyqtSlot()
    def run(self):
        print(self.dir_name,self.queryimg)
        result=transfer_learning.sorted_paint_result_Json(SEARCH_PATH=self.queryimg,DIR_PATH=self.dir_name,progress_func=self.progress_callback)
        print(result)
        self.signals.finished.emit(result)




class WorkerSignals(QtCore.QObject):
    #result = QtCore.pyqtSignal(dict)
    progress = QtCore.pyqtSignal(float)
    finished=QtCore.pyqtSignal(list)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())