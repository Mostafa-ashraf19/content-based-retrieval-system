
import numpy as np
import psycopg2
import Module
import os
import CBVR
import shutil

class dbHandling:
    def __init__(self):
        self.connection = psycopg2.connect(database="mmdb", user="postgres", password="1234", host="127.0.0.1", port="5432")
        self.cursor = self.connection.cursor()
        self._create_img_t()
        self._video_t()
        self.names=['mean_color','histogram']
    def __del__(self):
        self.connection.close()
        self.cursor.close()

    def _commit(self):
        self.connection.commit()

    def _create_img_t(self):
        self.cursor.execute('''DROP TABLE IF EXISTS images;''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS images
                    (
                    paths TEXT NOT NULL,
                    mean_color           TEXT   NOT NULL,
                    histogram            TEXT     NOT NULL);''')
        self._commit()
        self.cursor.execute('''DROP TABLE IF EXISTS imageslayout;''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS imageslayout
                                    (
                                    paths TEXT NOT NULL,
                                    color_layout           TEXT     NOT NULL);''')
        self._commit()

    def _video_t(self):
        #self.cursor.execute('''DROP TABLE IF EXISTS videos;''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS videos
                                            (
                                            paths TEXT NOT NULL,
                                            nvs          TEXT     NOT NULL);''')
        self._commit()


    def _delete_t(self, t_name):
        self.cursor.execute(f"DROP TABLE IF EXISTS {t_name}")
        self._commit()

    def _insert_video(self,path, video_feature):

        self.cursor.execute(
            f'''INSERT INTO videos (paths,nvs) VALUES ('{path}','{video_feature}')''')
        self._commit()


    def _insert_image(self,path, algo1_feature="", algo2_feature="", algo3_feature=""):
        if len(algo3_feature) > 3:
            self.cursor.execute(
                f'''INSERT INTO imageslayout (paths,color_layout) VALUES ('{path}','{algo3_feature}')''')
            self._commit()
        else:
            self.cursor.execute(
                f'''INSERT INTO images (paths,mean_color,histogram) VALUES ('{path}','{algo1_feature}','{algo2_feature}')''')
            self._commit()

    def prepareImages(self,algorith_method1=Module.calcMeanImage,algorith_method2=Module.calcHistogram,algorith_method3=""): #delet old record before
        if os.path.isdir(".\images-layout"):
            shutil.rmtree("images-layout/", ignore_errors=True)
            os.mkdir("images-layout")

        if os.path.isdir("images-layout-rt/"):
            shutil.rmtree("images-layout-rt/", ignore_errors=True)
            os.mkdir("images-layout-rt/")

        arr = os.listdir('.\images')
        for name in arr:
            self._insert_image(path=name,
                               algo1_feature=self.tostring(algorith_method1('.\images\\' + name)),
                               algo2_feature=self.tostring(algorith_method2('.\images\\' + name)),
                               algo3_feature="")
            Module.imgcrop('.\images\\' + name, 2, 2, False)

        arr = os.listdir('.\images-layout')
        for name in arr:
            algo3= self.tostring(algorith_method2('.\images-layout\\' + name))
            self._insert_image(path= name, algo3_feature=algo3)


    def prepareVideos(self,algorithm):
        self.cursor.execute(f'''select paths from videos''')
        records = self.cursor.fetchall()
        if len(records) == 0:
            arr = os.listdir('.\\videos')
            for name in arr:
                algo3 = self.tostring_v(algorithm('.\\videos\\' + name))
                self._insert_video(name, algo3)


    def get_videos(self,v_path, compare_method):
        self.cursor.execute(f'''select * from videos''')
        records = self.cursor.fetchall()

        videos_lst=[]
        for record in records:
            var = self.tolist_v(record[1])

            result=compare_method(v_path,var)

            if result==1:
                videos_lst.append(record[0])
        return videos_lst


    def get_images(self,image,algorith_method,number, compare_method ):
        image_feature=algorith_method(image)
        records=''
        if number ==2 :
            self.cursor.execute(f'''select * from imageslayout''')
            records = self.cursor.fetchall()
        else:
            self.cursor.execute(f'''select paths, {self.names[number]} from images''')
            records = self.cursor.fetchall()

        if number==0: #mean
            results={}
            for path, feature in records:
                results[path] = self.tolist(feature)
            return compare_method(image_feature,results)
        else: #histogram
            results = {}
            for path, feature in records:
                temp = [np.float32(item) for item in self.tolist(feature)]
                results[path] =np.array(temp)
            return compare_method(image_feature, results)


    def _create_video_t(self):
        self.cursor.execute('''DROP TABLE IF EXISTS Videos;''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Videos
                    (
                    paths TEXT NOT NULL,
                    NAV    TEXT    NOT NULL);''')
        self._commit()

    def tostring(self,l,num_=True):
       return ','.join([ str(num) for num in l]) if num_ else ','.join(l)

    def tostring_v(self,l):
        return '|'.join([ ','.join([str(num) for num in histo]) for histo in l ])

    def tolist_v(self,string1):
        return [[np.float32(element) for element in l.split(',')] for l in string1.split('|')]

    def tolist(self,st ,num_=True):
        return  st.split(',') if not num_ else [ float(i) for i in st.split(',')]

    # def test(self,):
    #     self.cursor.execute('''CREATE TABLE  IF NOT EXISTS arr (
    #                         pkey  serial,
    #                         val   int[2][3] );''')
    #     self._commit()
    #
    #     x=( (1,2,3), (4,5,6) )
    #     self.cursor.execute(f'''INSERT INTO arr( val ) VALUES('{x}');''')
    #     self._commit()


if __name__=='__main__':
    mydb= dbHandling()
   # x,y,z,i='mary.png',mydb.tostring([1.4,2.3,3.2]),mydb.tostring([1,2.2,3,4,5,6,9,12,13]),mydb.tostring(["car","tree","dog"])
    #mydb.prepareImages()
   #mydb._insert_image(path, Module.calcMeanImage, Module.calcHistogram(), algo3_feature="")
   # mydb.get_images('histogram')
    #mydb.get_images("E:/final_mm_project/images/test.jpg",Module.calcHistogram ,1, Module.comparehistogram )
    # mydb.test()

