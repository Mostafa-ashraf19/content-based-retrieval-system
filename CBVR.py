from logging import NullHandler
import os
import cv2
import numpy as np

from numpy.lib.histograms import histogram

class cbvr:
    def __init__(self):
        self.list_dir=[]
        self.vedio_histos = []
        self.frame_shapes = []
    
    #--------------------------------------------------------------------------------
    def extract_key_histo(self,video_dir,threshold=9):
        cap = cv2.VideoCapture(video_dir)
        fps = int(cap.get(5))
        if(fps==0):
            raise "no vedio selected"
              
        # Read the first frame.
        ret, prev_frame = cap.read()
       
        i = 0
        count = 0
        while ret:
            ret, curr_frame = cap.read()
            if ret:
                hist_img1 = self.histo(prev_frame)
                hist_img2 = self.histo(curr_frame)
                metric_val = cv2.compareHist(hist_img1, hist_img2, cv2.HISTCMP_BHATTACHARYYA)   
                if metric_val > threshold/100:
                    # cv2.imwrite(str(i)+'.jpg',curr_frame)
                    self.vedio_histos.append(list(hist_img2.ravel()))
                    count += 1
                prev_frame = curr_frame
                i += 1
        return self.vedio_histos

    #--------------------------------------------------------------------------------
    def nvs(self,ref_video,one_histolist,threshold=9):

        cap = cv2.VideoCapture(ref_video)
        fps = int(cap.get(5))
        if(fps==0):
            raise "your video is not available"
         
        ret, prev_frame = cap.read()
        i = 0
        count = 0
        kf_count = 0
        while ret:
            ret, curr_frame = cap.read()
            if ret:
                hist_img1 = self.histo(prev_frame)
                hist_img2 = self.histo(curr_frame)
                metric_val = cv2.compareHist(hist_img1, hist_img2, cv2.HISTCMP_BHATTACHARYYA)   

                if metric_val > threshold/100: #kf of search video
                    kf_count+=1
                    j=0
                    for j in range(len(one_histolist)):
                        compare= cv2.compareHist(hist_img2, np.array(one_histolist[j]).reshape(180,256), cv2.HISTCMP_BHATTACHARYYA)
                        if compare < 0.5:
                            count += 1
                            break
                prev_frame = curr_frame
                i += 1
        if kf_count == 0:
            raise "threshold is too high,enter a value lower than "+ str(threshold)

        if (count/kf_count)> 0.7:
            return 1
        else:
            return 0
    #--------------------------------------------------------             
    # return normalized histogram of the image
    def histo(self,img):
        img1_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hist_img = cv2.calcHist([img1_hsv], [0,1], None, [180,256], [0,180,0,256])
        cv2.normalize(hist_img, hist_img, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX);
        return hist_img
  

    #------------------------------------------------------------------------------------------
    def framesNum(self,cap):
        return int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#----------------------------------------------------------------------------------------------
    def loop_vedios(self,dir):
        ved_histos_dic={}
        shapes_histo_dic={}
        for file in os.listdir(dir):
            if file.endswith(".mp4"):
                current_file_dir = dir+'/'+ file
                self.list_dir.append(current_file_dir)
        for j in range(len(self.list_dir)):
            ved_histos_dic[self.list_dir[j][self.list_dir[j].rfind('/')+1:self.list_dir[j].rfind('.')]]=self.extract_key_histo(self.list_dir[j])
        return (shapes_histo_dic,ved_histos_dic)
    

