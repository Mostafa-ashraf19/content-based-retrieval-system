from skimage import io
import cv2
from PIL import Image
import os


def calcMeanImage(path):
    img = io.imread(path)[:, :, :]
    average = img.mean(axis=0).mean(axis=0)
    return list(average)
def compareMean( imgMean, index):  #image uploadedmean
    result=[]
    for (row, Mean) in index.items():
        if (Mean[0]>=0.9*imgMean[0] and Mean[0]<=1.1*imgMean[0]) \
            and (Mean[1]>=0.9*imgMean[1] and Mean[1]<=1.1*imgMean[1]) \
            and (Mean[2]>=0.9*imgMean[2] and Mean[2]<=1.1*imgMean[2]) :
                result.append(row)
    return result
def calcHistogram(path):
    image = cv2.imread(path)
    hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    return hist

def comparehistogram(img_hist, index): #index is a dictionary from database
    # index={}   we well get it from database,, histograms of the all the images "row": histo
    results={}     #"row": hist
    images_index=[]
    for (row, hist) in index.items():
        d = cv2.compareHist(img_hist, hist, cv2.HISTCMP_CORREL)
        results[row] = d
    # sorting and taking the most 2 similar images
    results = sorted({(v, k) for (k, v) in results.items()}, reverse=True)[:5]

    for (similarity_percent, row) in results:
        images_index.append(row)
    return images_index


def imgcrop(input, xPieces, yPieces, realtime=False):
    filename, file_extension = os.path.splitext(input)
    im = Image.open(input)
    imgwidth, imgheight = im.size
    height = imgheight // yPieces
    width = imgwidth // xPieces
    # direct= os.path.join(os.path.normpath(os.getcwd() + os.sep ),'images-layout\\')
    direct='.\images-layout\\'

    for i in range(0, yPieces):
        for j in range(0, xPieces):
            box = (j * width, i * height, (j + 1) * width, (i + 1) * height)
            a = im.crop(box)
            try:
                if realtime == False :
                    a.save(direct +filename.split("\\")[2] + "-" + str(i) + "-" + str(j) + file_extension)

                else:
                    a.save(".\images-layout-rt\\" + filename.split("/")[-1] + "-" + str(i) + "-" + str(j) + file_extension)
            except:
                pass


def color_layout(path):
    imgcrop(path, 2,2)
    arr = os.listdir('.\images-layout-rt')
    l =[]
    for img in arr :
        l.append(calcHistogram('.\images-layout-rt'+img))

    return l


