from pymongo import MongoClient
import time
import os
from GFS import *
from bson.objectid import ObjectId


Mongo_Addr = '127.0.0.1' #数据库所在ip地址，目前不使用站库分离
Mongo_Port = 27017
client = MongoClient(host=Mongo_Addr, port=Mongo_Port)
threshold=1000   # 阈值设为1000


def check_model():
    '''
    written by 胡煜宗
    检查预约的模型中的标签训练数据是否达到阈值
    :return:
    '''
    db = client.web
    model_list = db.users.find_one()
    for model in model_list:
        labels=model['labels']
        exist_models=db.models.files.find({'labels':labels})
        if exist_models!=[]:    # 说明模型已有，删除预约模型
            db.models.remove({'_id':model['_id']})
        else:
            satisfied_flag=check_emotion_label(labels)
            if satisfied_flag==True:
                train_model(labels)



def check_emotion_label(emotion_list):
    '''
    written by 胡煜宗
    判断各个emotion是否达到阈值
    :param emotion_list: 标签列表
    :return: true为达到阈值，false为不满足
    '''
    db=client.web
    flag=True  # 默认为True，如果有一个不满足，则flag置为False
    for emo in emotion_list:
        count=db.labels.find_one({'emo':emo})['count']
        if count < threshold:
            flag=False
    return flag

def train_model(labels):
    '''
    written by 胡煜宗
    开始迁移学习
    :return:
    '''
    db = client.web
    # 先将迁移学习需要的默认模型保存到临时文件夹
    default_model_id='5cee6b9f53fbf62c37e49576'
    selected_json_id = db.models.files.find_one({'modelId': default_model_id, 'type': 'json'})['_id']
    selected_xml_id = db.models.files.find_one({'modelId': default_model_id, 'type': 'xml'})['_id']
    gfs_model = GFS('web', 'models', client)  # gridfs initialize
    db, _ = gfs_model.createDB()
    tmp_path='transfer_learning_tmpdir'
    tmp_save_model = os.path.join(tmp_path,'model', 'tmp.h5')
    tmp_save_json  = os.path.join(tmp_path,'model', 'tmp.json')
    tmp_save_xml   = os.path.join(tmp_path,'model', 'tmp.xml')
    (bdata, attri) = gfs_model.getFile(db, ObjectId(default_model_id))
    tmp_out_model = open(tmp_save_model, 'wb')
    tmp_out_model.write(bdata)
    tmp_out_model.close()
    (bdata, attri) = gfs_model.getFile(db, ObjectId(selected_json_id))
    tmp_out_model = open(tmp_save_json, 'wb')
    tmp_out_model.write(bdata)
    tmp_out_model.close()
    (bdata, attri) = gfs_model.getFile(db, ObjectId(selected_xml_id))
    tmp_out_model = open(tmp_save_xml, 'wb')
    tmp_out_model.write(bdata)
    tmp_out_model.close()

    gfs_model = GFS('web', 'pictures.files', client)  # gridfs initialize
    db, _ = gfs_model.createDB()
    for label in labels:
        tmp_label_dir=os.path.join(tmp_path,'pictures',label)
        os.makedirs(tmp_label_dir)
        pic_id_list=db.pictures.files.find({'label':label}).limit(100)
        for index,pic_id in enumerate(pic_id_list): # 暂存100张该标签的图片到临时目录
            (bdata, attri) = gfs_model.getFile(db, ObjectId(default_model_id))
            tmp_out_model = open(os.path.join(tmp_label_dir,"{:d}".format(index)), 'wb')
            tmp_out_model.write(bdata)
            tmp_out_model.close()
    os.system('python3 transfer_learning_source/image_preprocessing.py transfer_learning_tmpdir')
    os.system('python3 transfer_learning_source/transfer_learning.py')
    os.system('rm -r transfer_learning_tmpdir/model/*')
    os.system('rm -r transfer_learning_tmpdir/pictures/*')

if __name__=='__main__':
    while(1):
        check_model()
        time.sleep(3600)    # 每一个小时检查一次