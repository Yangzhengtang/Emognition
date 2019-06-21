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
    md5 = hashlib.md5()
    s += salt
    md5.update(s.encode('utf-8'))
    return md5.hexdigest()

# 因为会刷新页面，因此会多次调用某个函数，因此只能使用全局变量进行存储
upload_img_count=0  # 上传图片的数量
uploaded_img=[]     # 上传图片的路径名列表

def get_upload_img(path):
    '''
    written by 胡煜宗
    将临时文件夹下的文件路径加入全局变量uploaded_img
    :param path: 临时文件夹路径名，如stattc/TmpUploadDir
    :return:
    '''
    global uploaded_img
    if uploaded_img!=[]:
        return
    uploaded_img=os.listdir(path)
    uploaded_img.remove('.gitkeep') # 由于有.gitkeep文件，所以需要过滤一次，返回所有临时文件的名字列表
    return

def clear_imgs():
    '''
    written by 胡煜宗
    清空临时文件
    :return:
    '''
    global upload_img_count,uploaded_img
    for img in uploaded_img:    # 删除临时文件
        os.remove(os.path.join("static/TmpUploadDir",img))
    uploaded_img=[]
    # print("Clear temp pics")
    return

def get_img_path(path):
    '''
    written by 胡煜宗
    加载下一张临时图片的路径
    :param path:
    :return:
    '''
    global upload_img_count,uploaded_img
    get_upload_img(path)    # 修改全局变量uploaded_img,如果uploaded_img为空则将临时文件夹下所有文件名加入uploaded_img
    if upload_img_count==0:
        return '-1'
    filepath=uploaded_img[upload_img_count-1]
    upload_img_count-=1
    return os.path.join('static/TmpUploadDir',filepath)

def get_values_from_db(table, field):
    value_list = []
    db = client.web
    results = db[table].find()
    for result in results:
        #print(result)
        value_list.append(result[field])
    return value_list


@app.route('/upload', methods = ['POST', 'GET'])
def upload():
    '''
    written by 胡煜宗
    与前端upload.html中上传图片功能对应，将上传每张图片先存于临时文件夹
    前端每异步上传一张照片，调用一次该函数
    :return:
    '''
    if request.method=='POST':  # POST表示提交了文件
        if not session.get('is_login'): # 验证登录
            flash('please login first')
            return render_template('login.html')
        file = request.files['file']
        count=0
        fname=file.filename
        while os.path.exists(os.path.join('static/TmpUploadDir', fname)):  # 防止文件名重复
            fname=file.filename[:file.filename.find('.')]+"_{:.0f}".format(count)+file.filename[file.filename.find('.'):]
            count+=1
        file.save(os.path.join('static/TmpUploadDir', fname))  # 保存到临时文件夹
        global upload_img_count
        upload_img_count+=1
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
    return render_template('sierra/base.html')

@app.route('/home')
def goHome():
    return render_template('sierra/base.html')

@app.route('/uploadSuccess')
def uploadSuccess():
    return render_template('uploadSuccess.html')

img_path = '-1'
@app.route('/FinishUpload',methods=['POST','GET'])
def FinishUpload():
    global img_path
    if request.method == 'POST':  
        selected_label_before = request.form.getlist('selected_label_before')   #   args from setting.html
        selected_label_after = request.form.getlist('selected_label_after')     #   args from setLabel.html
        print(selected_label_before)
        print(selected_label_after)

        if(selected_label_after!=[]):    #   from setLabel.html
            print("Run 1")
            query = {'filename': img_path}
            id = gfs.insertFile(file_db_handler, img_path, query, selected_label_after[0])  # 插入照片
            #   the count of each label should +1
            for label in selected_label_after:
                condition = {'emo': label}
                result = client.web.labels.find_one(condition)
                result['count'] += 1
            client.web.labels.update(condition, result)
            img_path = get_img_path("static/TmpUploadDir")
            if img_path == '-1':
                clear_imgs()
                img_path = '-1'
                return render_template('uploadSuccess.html')
            show_label_list = client.web.models.find_one({'uid':session['uid']})['labels']
            return render_template('setLabel.html', label_list=show_label_list, img_path=img_path)

        else:   #   from setting.html
            print("Run 2")
            img_path = get_img_path("static/TmpUploadDir")
            uid = str(os.urandom(24))
            query = {'labels': selected_label_before, 'uid': uid}
            client.web.models.insert(query)
            session['uid'] = uid
            if img_path == '-1':
                clear_imgs()
                img_path = '-1'
                return render_template('uploadSuccess.html')
            show_label_list = client.web.models.find_one({'uid':session['uid']})['labels']
            return render_template('setLabel.html', label_list=show_label_list, img_path=img_path)
    else:
        print("WHAT")


@app.route('/progress')
def progressPage():
    db = client.web
    result_list = db.labels.find()
    label_list = []
    for result in result_list:
        print(result)
        result.pop('_id')
        label_list.append(result)
    return render_template('progress.html', label_list=label_list)

@app.route('/setting', methods=['GET', 'POST'])
def setting():
    if request.method == 'POST': #   Refresh
        label_list = get_values_from_db('labels', 'emo')
        additionLabels = request.form.get('additionLabels')
        print("Got it: " + additionLabels)
        if(additionLabels!='' and (additionLabels not in label_list)): #   Got new input
            db = client.web
            db.labels.insert({'emo': additionLabels, 'count': 0})
            label_list.append(additionLabels)
        return render_template('setting.html', label_list=label_list)
    else:
        label_list = get_values_from_db('labels', 'emo')
        return render_template('setting.html', label_list=label_list)


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
    if request.method == 'POST':    #   Refresh
        #   Todo: add multiple labels
        label_list = get_values_from_db('labels', 'emo')
        additionLabels = request.form.get('additionLabels')
        print("Got it: " + additionLabels)
        if(additionLabels!='' and (additionLabels not in label_list)): #   Got new input
            db = client.web
            db.labels.insert({'emo': additionLabels, 'count': 0})
            label_list.append(additionLabels)
        return render_template('setting.html', label_list=label_list)

@app.route('/testResult',methods=['GET', 'POST'])
def recognize():
    '''
    使用选中的已有模型进行识别，对应于navigateTest.html中的表单提交
    先根据用户选中的模型，从mongo中读取模型，存于static/TmpModels的临时目录下，对static/TmpUploadDir下上传的图片进行识别
    识别结果存于static/TmpResult临时目录中
    :return:
    '''
    selected_model_id=request.form.get('model_info')
    db = client.web
    selected_json_id = db.models.files.find_one({'modelId': selected_model_id,'type':'json'})['_id']
    selected_xml_id = db.models.files.find_one({'modelId': selected_model_id,'type':'xml'})['_id']
    gfs_model = GFS(Mongo_Database, 'models', client)  # gridfs initialize
    db,_=gfs_model.createDB()
    tmp_save_model,tmp_save_json,tmp_save_xml='static/TmpModels/tmp.h5','static/TmpModels/tmp.json','static/TmpModels/tmp.xml'
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

    uploaded_path,test_result_path,tmp_model_path='static/TmpUploadDir','static/TmpResult','static/TmpModels'
    test_img=os.listdir(uploaded_path)
    test_img.remove('.gitkeep')
    # 调用后端的模型调用代码，创建表情识别实例
    recog=Recognition(tmp_save_json,tmp_save_model,tmp_save_xml)
    for img in test_img:
        recog.recognize(os.path.join(uploaded_path,img),os.path.join(test_result_path,"marked_"+img))
    result_list=os.listdir('static/TmpResult')
    result_list.remove('.gitkeep')
    session['result']=result_list
    for tmp_remove in test_img:  # 删除上传的图片
        os.remove(os.path.join(uploaded_path, tmp_remove))
    tmp_model=os.listdir(tmp_model_path)
    tmp_model.remove('.gitkeep')
    for tmp_remove in tmp_model:    # 删除临时从mongo取出的model文件
        os.remove(os.path.join(tmp_model_path, tmp_remove))
    return render_template('testResult.html')

@app.route('/showTestResult',methods=['GET', 'POST'])
def showTestResult():
    '''
    written by 胡煜宗
    对应于testResult.html中点击next result的页面刷新功能，显示下一张打了标记的照片
    :return:
    '''
    result=session['result']
    result_pic=result.pop() # 列表最后一张照片已显示过，pop之
    session['result']=result
    os.remove(os.path.join('static/TmpResult',result_pic))
    if result==[]:
        return render_template('testSuccess.html')
    return render_template('testResult.html')

if __name__ == '__main__':
    app.run(threaded=True,host="0.0.0.0")

