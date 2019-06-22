from flask import Flask,request,render_template,redirect,flash,session,get_flashed_messages,url_for
from pymongo import MongoClient
from flask_bootstrap import Bootstrap
import hashlib
from flask_dropzone import Dropzone
from bson.objectid import ObjectId
import os
from GFS import *
from Recognize.Recognize import Recognition
import types 
import random
import string

app = Flask(__name__)
# app.config.from_object(config)
app.config["SECRET_KEY"] = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 512 * 1024 * 1024    # 最大上传文件大小
dropzone = Dropzone(app)
bootstrap = Bootstrap(app)

Mongo_Addr = '127.0.0.1' #数据库所在ip地址，目前不使用站库分离
Mongo_Port = 27017
Mongo_Database = 'web'
Mongo_User = ''
Mongo_Password = ''
Picture_Collection = 'pictures'

client = MongoClient(host=Mongo_Addr, port=Mongo_Port)
# 暂时不使用密码登录数据库
# client.web.authenticate(Mongo_User, Mongo_Password)     # Login
gfs=GFS(Mongo_Database, Picture_Collection, client)     #   gridfs initialize
file_db_handler,file_table_handler = gfs.createDB()

def hash_code(s, salt='huyz'):
    '''
    written by 胡煜宗
    生成随机密钥，用md5进行散列，用于处理用户密码
    return:    field列表
    '''
    md5 = hashlib.md5()
    s += salt
    md5.update(s.encode('utf-8'))
    return md5.hexdigest()

def get_values_from_db(table, field):
    '''
    written by 杨正瑭
    查找mongodb中table中对应所有现存field
    :return:    field列表
    '''
    value_list = []
    db = client.web
    results = db[table].find()
    for result in results:
        value_list.append(result[field])
    return value_list

def get_random_string():
    '''
    written by 杨正瑭
    生成8位随机字符串
    :return:    字符串
    '''
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+=-"
    sa = []
    for i in range(8):
        sa.append(random.choice(seed))
    salt = ''.join(sa)
    return salt


@app.route('/upload', methods = ['POST', 'GET'])
def upload():
    '''
    written by 胡煜宗
    与前端upload.html中上传图片功能对应，将上传每张图片先存于临时文件夹
    前端每异步上传一张照片，调用一次该函数
    :return:
    '''
    if not session.get('is_login'): # 验证登录
        flash('please login first')
        return redirect('/login')

    if not session.get('upload_token'): #   添加upload_token，对每次用户使用upload功能进行标识
        existing_path = os.listdir('static/TmpUploadDir')
        while True:
            upload_token = get_random_string()
            if(upload_token not in existing_path):
                break
        #   防止随机字符串重复
        session['upload_token'] = upload_token
        os.makedirs(os.path.join('static/TmpUploadDir', session['upload_token'])) 
        #   新建临时文件夹，存储上传图片

    if request.method=='POST':  # POST表示提交了文件
        file = request.files['file']
        count=0
        fname=file.filename
        upload_dir = os.path.join('static/TmpUploadDir', session['upload_token'])
        while os.path.exists(os.path.join('static/TmpUploadDir', fname)):  # 防止文件名重复
            fname=file.filename[:file.filename.find('.')]+"_{:.0f}".format(count)+file.filename[file.filename.find('.'):]
            count+=1
        file.save(os.path.join(upload_dir, fname))  # 保存到临时文件夹
        print("Got the file. %s" % fname)
    return render_template('upload.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    written by 胡煜宗
    用户注册函数，与register.html对应，用户注册时将相关信息插入mongo
    :return:
    '''
    if request.method == 'POST':
        username = request.form.get('username')
        password = hash_code(request.form.get('password'))
        confirm_password = hash_code(request.form.get('confirm'))
        insert_info = {'username':username,'password':password,'models':['5cee6b9f53fbf62c37e49576']}   # 默认添加default model的ID
        if username and password and confirm_password:
            if password != confirm_password:
                flash('两次输入的密码不一致！')
                return render_template('register.html', username=username)
            db = client.web
            db.users.insert(insert_info)
            return redirect('/login')
        else:
            flash('所有字段都必须输入！')
            if username:
                return render_template('register.html', username=username)
            return render_template('register.html')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    written by 胡煜宗
    登录函数，与前端login.html对应
    当用户登录时，调用该函数进行用户名密码的验证，并将登录情况存入session中
    :return:
    '''
    if request.method == 'POST':
        username = request.form.get('username')
        password = hash_code(request.form.get('password'))
        db = client.web
        collection = db.users.find_one({'username':username})
        if collection['password'] == password:
            # 登录成功后存储session信息
            session['is_login'] = True
            session['name'] = username
            return render_template('sierra/base.html')
        else:
            flash('Bad credential')
            return render_template('login.html')
    return render_template('login.html')


@app.route('/logout')
def logout():
    '''
    written by 胡煜宗
    退出登录函数，清空session
    :return:
    '''
    # 退出登录，清空session
    if session.get('is_login'):
        session.clear()
        return redirect('/')
    return redirect('/')

@app.route('/')
def index():
    '''
    written by 杨正瑭
    首页界面
    :return:    显示sierra/base.html页面
    '''
    return render_template('sierra/base.html')

@app.route('/home', methods=['GET', 'POST'])
def goHome():
    '''
    written by 杨正瑭
    首页界面
    :return:    显示sierra/base.html页面
    '''
    return render_template('sierra/base.html')

@app.route('/uploadSuccess', methods=['GET', 'POST'])
def uploadSuccess():
    '''
    written by 杨正瑭
    跳转至上传成功后的页面
    :return:    显示uploadSuccess.html页面
    '''
    session.pop('upload_token',None)    # 清空session中upload_token
    print(str(session))
    return render_template('uploadSuccess.html')

@app.route('/setTrainLabel',methods=['POST','GET'])
def setTrainLabel():
    '''
    written by 杨正瑭
    在用户对新模型进行迁移学习时，显示页面由用户选择图片
    对应标签
    :return:    
    '''
    if(isValid()):
        upload_token = session['upload_token']
        upload_dir = os.path.join('static/TmpUploadDir', upload_token)
        temp_uploaded_files = os.listdir(upload_dir)
        uploaded_files = []
        for file in temp_uploaded_files:
            uploaded_files.append(os.path.join(upload_dir, file))
    #   以下两个变量用于判断跳转来源
    selected_label_before = request.form.getlist('selected_label_before')   #   args from navigateTrain.html
    selected_label_after = request.form.getlist('selected_label_after')     #   args from setTrainLabel.html
    if(selected_label_after!=[]):    
    #   完成标注后（从setTrainLabel.html跳转而来）
        uploaded_files = session['uploaded_files']
        showing_pic = uploaded_files.pop()          #   列表最后一张照片已经显示，pop之
        session['uploaded_files'] = uploaded_files
        query = {'filename': showing_pic}           #   准备更新数据库,插入照片
        id = gfs.insertFile(file_db_handler, showing_pic, query, selected_label_after[0])  
        for label in selected_label_after:  #   the count of each label should +1
            condition = {'emo': label}
            result = client.web.labels.find_one(condition)
            result['count'] += 1
        client.web.labels.update(condition, result)
    else:                                           
    #  第一次需要标注时，只需显示页面（ 从navigateTrain.html跳转而来）
        #   初始化session中的uploaded_files
        session['uploaded_files'] = uploaded_files
        #   数据库中新建model
        query = {'labels': selected_label_before, 'upload_token': upload_token}
        client.web.models.insert(query)
    if(not len(uploaded_files)):   
    #   列表中无文件，标记完毕
        #   在用户所预约的model中添加新项
        condition = {'username':session.get('name')}
        result = client.web.users.find_one(condition)
        result['models'].append(upload_token)
        client.web.users.update(condition, result)
        return redirect('/uploadSuccess')   #   跳转至结束页面
    else:   
        show_label_list = client.web.models.find_one({'upload_token': upload_token})['labels']
        return render_template('setTrainLabel.html', label_list=show_label_list, img_path=uploaded_files[-1])

@app.route('/progress')
def progressPage():
    '''
    written by 杨正瑭
    完成选择标签任务后，跳转至进度页面，显示现在各个标签上传进度
    :return:    progress.html页面  
    '''
    db = client.web
    result_list = db.labels.find()
    label_list = []
    for result in result_list:
        print(result)
        result.pop('_id')
        label_list.append(result)
    return render_template('progress.html', label_list=label_list)

@app.route('/navigateTrain', methods=['GET', 'POST'])
def navigateTrain():
    '''
    written by 杨正瑭
    选择train按钮后，跳转至中间页面
    :return:    
    '''    
    if request.method == 'POST': 
        print('something wrong.')
    else:   #   第一次点开navigateTrain的情况
        label_list = get_values_from_db('labels', 'emo')
        return render_template('navigateTrain.html', label_list=label_list)

@app.route('/navigateTest',methods=['GET','POST'])
def navigateTest():
    '''
    written by 胡煜宗
    显示该用户可用的模型，对应于upload.html中点击test按钮跳转的页面
    :return:
    '''
    if not session.get('is_login'):
        flash('please login first')
        return render_template('login.html')
    db = client.web
    model_id_list=db.users.find_one({'username':session.get('name')})['models']    # 存放models中属于他的model的_id
    model_info_list=[]
    for ID in model_id_list:    # ID为列表model_id
        one_model_info=db.models.files.find_one({'_id':ObjectId(ID)})
        model_info_list.append([ID,one_model_info['modelname'],one_model_info['labels']])  # 存放格式为[ID,'default',['happy','angry'....]]
    return render_template('navigateTest.html',model_info_list=model_info_list)

@app.route('/navigateAdditionLabel', methods=['GET', 'POST'])
def navigateAdditionLabel():
    '''
    written by 杨正瑭
    显示在挑选标签页面，若有新加标签，添加并刷新显示
    :return:    
    '''
    if request.method == 'POST':    #   点击add按钮的情况，添加标签，再次刷新返回navigateTrain页面
        #   Todo: add multiple labels
        label_list = get_values_from_db('labels', 'emo')
        additionLabels = request.form.get('additionLabels')
        print("Got it: " + additionLabels)
        if(additionLabels!='' and (additionLabels not in label_list)): #   Got new input
            db = client.web
            db.labels.insert({'emo': additionLabels, 'count': 0})
            label_list.append(additionLabels)
        return render_template('navigateTrain.html', label_list=label_list)

@app.route('/testResult',methods=['GET', 'POST'])
def recognize():
    '''
    written by 胡煜宗
    使用选中的已有模型进行识别，对应于navigateTest.html中的表单提交
    先根据用户选中的模型，从mongo中读取模型，存于static/TmpModels的临时目录下，对static/TmpUploadDir下上传的图片进行识别
    识别结果存于static/TmpResult临时目录中
    :return:
    '''
    selected_model_id=request.form.get('model_info')
    db = client.web
    labels = db.models.files.find_one({'_id': ObjectId(selected_model_id)})['labels']
    selected_json_id = db.models.files.find_one({'modelId': selected_model_id,'type':'json'})['_id']
    selected_xml_id = db.models.files.find_one({'modelId': selected_model_id,'type':'xml'})['_id']
    gfs_model = GFS(Mongo_Database, 'models', client)  # gridfs initialize
    db,_=gfs_model.createDB()

    if(isValid()):
        upload_token = session['upload_token']
        tmp_path = os.path.join('static/TmpModels', upload_token)

    #   新建model文件夹
    folder = os.path.exists(tmp_path)
    if not folder:
        os.makedirs(tmp_path) 

    tmp_save_model = os.path.join(tmp_path, 'tmp.h5')
    tmp_save_json  = os.path.join(tmp_path, 'tmp.json')
    tmp_save_xml   = os.path.join(tmp_path, 'tmp.xml')

    # 导出model文件到临时文件夹
    (bdata, attri) = gfs_model.getFile(db,ObjectId(selected_model_id))
    tmp_out_model=open(tmp_save_model,'wb')
    tmp_out_model.write(bdata)
    tmp_out_model.close()
    (bdata, attri) = gfs_model.getFile(db, ObjectId(selected_json_id))
    tmp_out_model=open(tmp_save_json,'wb')
    tmp_out_model.write(bdata)
    tmp_out_model.close()
    (bdata, attri) = gfs_model.getFile(db, ObjectId(selected_xml_id))
    tmp_out_model = open(tmp_save_xml, 'wb')
    tmp_out_model.write(bdata)
    tmp_out_model.close()

    #   每次使用test功能单独使用一个文件夹
    uploaded_path    = os.path.join('static/TmpUploadDir',upload_token)
    test_result_path = os.path.join('static/TmpResult',upload_token)
    tmp_model_path   = os.path.join('static/TmpModels',upload_token)

    #   新建result文件夹
    folder = os.path.exists(test_result_path)
    if not folder:
        os.makedirs(test_result_path) 

    test_imgs=os.listdir(uploaded_path)
    # 调用后端的模型调用代码，创建表情识别实例
    recog=Recognition(tmp_save_json,tmp_save_model,tmp_save_xml,labels)
    for img in test_imgs:
        origin_img = os.path.join(uploaded_path,img)
        target_img = os.path.join(test_result_path,"marked_"+img)
        print("Recognizing img, source:%s, target: %s" % (str(origin_img), str(target_img)))
        print("Recognizing......")
        emo_list = recog.recognize(origin_img, target_img)   # 保存识别结果
        print("Done.")

    #   初始化session中的result
    temp_result_list = os.listdir(test_result_path)
    result_list = []
    for result in temp_result_list:
        result_list.append(os.path.join(test_result_path, result))

    session['result'] = result_list

    for tmp_remove in test_imgs:     #   删除上传的图片
        os.remove(os.path.join(uploaded_path, tmp_remove))
    os.removedirs(uploaded_path)    #   删除临时文件夹

    tmp_model=os.listdir(tmp_model_path)
    for tmp_remove in tmp_model:    # 删除临时从mongo取出的model文件
        os.remove(os.path.join(tmp_model_path, tmp_remove))
    os.removedirs(tmp_model_path)    #   删除临时文件夹

    return render_template('testResult.html')

@app.route('/showTestResult',methods=['GET', 'POST'])
def showTestResult():
    '''
    written by 胡煜宗
    对应于testResult.html中点击next result的页面刷新功能，显示下一张打了标记的照片
    :return:
    '''
    if(isValid()):
        upload_token = session['upload_token']

    result=session['result']
    result_pic=result.pop() # 列表最后一张照片已显示过，pop之
    session['result']=result
    os.remove(result_pic)

    if result==[]:
        # 运行到这里说明每个结果文件都删除，此时清空对应临时文件夹
        os.removedirs(os.path.join('static/TmpResult',upload_token))    #   删除临时文件夹
        return redirect('/uploadSuccess')
    return render_template('testResult.html')

def isValid():
    '''
    written by 杨正瑭
    判断本次访问是否合法（是否是由正常顺序访问而来）
    :return:
    '''  
    if not session.get('is_login'): # 验证登录
        flash('please login first')
        return redirect('/login')

    if not session.get('upload_token'): # 验证是否上传过
        flash('Something wrong')
        return redirect('/home')    
    else:
        return True

if __name__ == '__main__':
    app.run(threaded=True,host="0.0.0.0",port=8090)

