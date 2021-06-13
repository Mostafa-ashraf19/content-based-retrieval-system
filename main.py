import sys
from PyQt5 import QtGui ,QtCore ,QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog,QMessageBox, \
    QApplication, QListWidget, QListView, QHBoxLayout, QListWidgetItem
from PyQt5.uic import loadUi
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap, QIcon
import os
import Module
import DataBase

from CBVR import  cbvr

class Mainwindow(QDialog):
    prepareImg_flag = 0
    prepareVid_flag = 0
    BrowseImg_flag = 0
    BrowseVid_flag = 0
    def __init__(self):

        super(Mainwindow,self).__init__()
        loadUi("project.ui",self)
        self.showFullScreen()
        self.setWindowState(QtCore.Qt.WindowMaximized)
        self.img_list.setViewMode(QListView.IconMode)
        self.img_list.setSpacing(20)
        self.img_list.setIconSize(QSize(200, 200))
        self.img_list.setMovement(False)
        self.img_list.setResizeMode(QListView.Adjust)
        self.mydb = DataBase.dbHandling()
        self.analy_img_btn.clicked.connect(self.analyzeImg)
        self.start_ved_b.clicked.connect(self.analyzeVid)
        self.browse_img_b.clicked.connect(self.browseimage)
        self.browse_ved_b.clicked.connect(self.browsevideo)
        self.prepare_img_b.clicked.connect(self.prepare_database_img)
        self.yolo_vid_b.clicked.connect(self.prepare_db_vid)
        self.cbvr_inst =  cbvr()


    def analyzeVid(self):
        if self.prepareVid_flag ==0:
            self.error("error message", "please click to Button prepare first ")
            return
        if self.BrowseVid_flag ==0:
            self.error("error message", "please choose a video first ")
            return
        pathVid=self.path_ved_line.text()
        result = self.mydb.get_videos(pathVid,self.cbvr_inst.nvs)
        if len(result)==0:
            self.feat_ved_line.setText("No matched video found")
        else:
            self.feat_ved_line.setText(', '.join(result))


     #   self.start_img_b.clicked.connect(self.getImageAlgorith)
    def analyzeImg(self):
        if self.prepareImg_flag ==0:
            self.error("error message", "please click to Button prepare first ")
            return
        if self.BrowseImg_flag ==0:
            self.error("error message", "please choose an image first ")
            return
        algtype=self.algo_img_Box.currentIndex()
        pathImg=self.path_img_line.text()

        if algtype==0 :
            similar_img=self.mydb.get_images(pathImg,
                                             Module.calcMeanImage ,
                                             algtype,
                                             Module.compareMean)
            fs=Module.calcMeanImage(pathImg)
            text=""
            for t in fs:
                text= text + "   "+ str(t)
            self.feat_img_line.setText(text)

        elif algtype==1 :
            similar_img=self.mydb.get_images(pathImg,
                                             Module.calcHistogram ,
                                             algtype,
                                             Module.comparehistogram)
            fs=Module.calcHistogram(pathImg)
            text = ""
            for t in fs:
                text = text +"  "+ str(t)
            self.feat_img_line.setText(text)

        elif algtype==2 :  #color_layout
            Module.imgcrop(pathImg,2,2,True)
            arr=os.listdir('.\images-layout-rt')
            similar_img =[]
            for img in arr:
                similar_img+= self.mydb.get_images('.\images-layout-rt\\'+img,
                                                   Module.calcHistogram,
                                                   algtype,
                                                   Module.comparehistogram)


        directory = '.\images\\' if algtype!=2 else '.\images-layout\\'
        self.img_list.clear()
        for f1 in similar_img:
            pix1 = QPixmap(directory+f1)
            item1 = QListWidgetItem(QIcon(pix1.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)),
                                    os.path.split(f1)[-1])

            self.img_list.addItem(item1)



    def browseimage(self):
        fname=QFileDialog.getOpenFileName(self, 'Open file','E:', 'Image files (*.jpg)')
        self.path_img_line.setText(fname[0])
        if len(fname[0])!=0 :
            self.BrowseImg_flag = 1

    def browsevideo(self):
        fname=QFileDialog.getOpenFileName(self, 'Open file','E:', 'video files (*.mp4)')
        self.path_ved_line.setText(fname[0])
        if len(fname[0])!=0 :
            self.BrowseVid_flag=1
    #prepare database for images


    def prepare_database_img(self):
        self.prepareImg_flag = 1
        self.mydb.prepareImages()
        self.prepare_img_b.setText("Done preparing")

    def prepare_db_vid(self):
        self.prepareVid_flag = 1

        self.mydb.prepareVideos(self.cbvr_inst.extract_key_histo)
        self.yolo_vid_b.setText("Done preparing")
    # Show Error Message Popup
    def error(self, title, text):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setWindowIcon(QtGui.QIcon("icon.ico"))
        msg.setText(text)
        msg.setIcon(QMessageBox.Warning)

        show_msg = msg.exec_()



if __name__=='__main__':
    app=QApplication(sys.argv)
    mainwindow = Mainwindow()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(mainwindow)
    widget.show()
    sys.exit(app.exec_())
