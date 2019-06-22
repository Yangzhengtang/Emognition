import unittest
import sys
sys.path.append('../')
from pymongo import MongoClient 	#	导入pymongo模块
from GFS import *

Mongo_Addr = '127.0.0.1' #数据库所在ip地址
Mongo_Port = 27017
Mongo_Database = 'web'
Mongo_User = ''
Mongo_Password = ''
Picture_Collection = 'pictures'

def recognize_func( model_json, model_h5, model_xml, labels, image):
    recog=Recognition( model_json, model_h5, model_xml, labels)
    target_image = 'marked' + image
    emo_list = recog.recognize(images, target_image)   # 保存识别结果
    return emo_list

class MyTest(unittest.TestCase):
	def setUp(self):
		self.client = MongoClient(host=Mongo_Addr, port=Mongo_Port)
		self.gfs=GFS(Mongo_Database, Picture_Collection, self.client)     #   gridfs initialize
		self.file_db_handler, self.file_table_handler = self.gfs.createDB()
        print ("Start mongodb test...")

    def tearDown(self):
        print ("Test done.")

    def test_001(self):	#	测试更新users表
    	test_result = False
    	insert_info = {'username':'test','password':'password','models':['5cee6b9f53fbf62c37e49576']}   
        db = self.client.web
        db.users.insert(insert_info)
        if(db.find_one(insert_info)):
        	test_result = True
        self.assertEqual(test_result,True)

    def test_002(self):	#	测试更新models表
    	selected_model_id = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral'];
        db = self.client.web
    	labels = db.models.files.find_one({'_id': ObjectId(selected_model_id)})['labels']
    	selected_json_id = db.models.files.find_one({'modelId': selected_model_id,'type':'json'})['_id']
    	selected_xml_id = db.models.files.find_one({'modelId': selected_model_id,'type':'xml'})['_id']
        gfs_model = GFS(Mongo_Database, 'models', self.client)  # gridfs initialize
    	db,_=gfs_model.createDB()
    	(bdata_1, attri_1) = gfs_model.getFile(db,ObjectId(selected_model_id))
	    (bdata_2, attri_2) = gfs_model.getFile(db, ObjectId(selected_json_id))
	    (bdata_3, attri_3) = gfs_model.getFile(db, ObjectId(selected_xml_id))
	    test_result = (bdata_1, attri_1) and (bdata_2, attri_2) and (bdata_3, attri_3)
        self.assertRaises(test_result, True)

if __name__=='__main__':
    unittest.main(verbosity=2)

