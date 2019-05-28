from flask import Flask,request,render_template,redirect,flash,session,get_flashed_messages
from pymongo import MongoClient
from flask_bootstrap import Bootstrap
import hashlib
from flask_dropzone import Dropzone
from gridfs import *
import os


app = Flask(__name__)
# app.config.from_object(config)
app.config["SECRET_KEY"] = os.urandom(24)
bootstrap=Bootstrap(app)
mongo_address='127.0.0.1' #数据库所在ip地址
client = MongoClient(host=mongo_address, port=27017)
app.config['MAX_CONTENT_LENGTH'] = 512 * 1024 * 1024    # 最大上传文件大小
dropzone = Dropzone(app)


def hash_code(s, salt='huyz'):
    md5 = hashlib.md5()
    s += salt
    md5.update(s.encode('utf-8'))
    return md5.hexdigest()

upload_img_count=0
uploaded_img=[]

def get_upload_img():   # 由于有.gitkeep文件，所以需要过滤一次，返回所有临时文件的名字列表
    global uploaded_img
    if uploaded_img!=[]:
        return
    uploaded_img=os.listdir("static/TmpUploadDir")
    uploaded_img.remove('.gitkeep')
    return

def get_img_path(): # 加载下一张临时图片
    global upload_img_count,uploaded_img
    get_upload_img()    # 修改全局变量uploaded_img,如果uploaded_img为空则将临时文件夹下所有文件名加入uploaded_img
    if upload_img_count==0:
        for img in uploaded_img:    # 删除临时文件
            os.remove(os.path.join("static/TmpUploadDir",img))
        return '-1'
    filepath=uploaded_img[upload_img_count-1]
    upload_img_count-=1
    return os.path.join('static/TmpUploadDir',filepath)

@app.route('/upload', methods = ['POST', 'GET'])
def upload():
    if request.method=='POST':  # POST表示提交了文件
        # if not session.get('name'): # 验证登录
        #     flash('please login first')
        #     return render_template('login.html')
        file = request.files['file']
        count=0
        fname=file.filename
        while os.path.exists(os.path.join('static/TmpUploadDir', fname)):  # 防止文件名重复
            fname=file.filename[:file.filename.find('.')]+"_{:.0f}".format(count)+file.filename[file.filename.find('.'):]
            count+=1
        file.save(os.path.join('static/TmpUploadDir', fname))  # 保存到临时文件夹
        global upload_img_count
        upload_img_count+=1
        # print(upload_img_count)
        # print("Got the file.")
    return render_template('upload.html')



    # client = MongoClient('localhost', 27017)
    # db = client.Pic
    # fs = GridFS(db, 'images')
    # with open ('F:/测试数据/hehe.jpg'.decode('utf-8'),'rb') as myimage:
    #     data=myimage.read()
    #     id = fs.put(data,filename='first')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = hash_code(request.form.get('password'))
        confirm_password = hash_code(request.form.get('confirm'))
        insert_info = {'username':username,'password':password}
        if username and password and confirm_password:
            if password != confirm_password:
                flash('两次输入的密码不一致！')
                return render_template('register.html', username=username)
            db = client.users
            db.user.insert(insert_info)
            return redirect('/login')
        else:
            flash('所有字段都必须输入！')
            if username:
                return render_template('register.html', username=username)
            return render_template('register.html')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = hash_code(request.form.get('password'))
        print("user: %s, password: %s" % (username, password))
        db = client.users
        collection = db.user.find_one({'username':username})
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

@app.route('/resultsAfterSelection', methods=['GET', 'POST'])
def navigatefterSelection():
    if request.method == 'POST':
        print("here")
        description = request.form.get('description')
        selection = request.form.get('selection')
        print("Got it")
        print(description + selection)
    return render_template('sierra/base.html')


@app.route('/finishUpload',methods=['POST','GET'])
def finishUpload():
    if request.method=='POST':
        label=request.form.get('selected_label')
        print(label)
        img_path=get_img_path()
        #########################这里应该完成插入数据库的操作######################
    else:
        img_path=get_img_path()
    if img_path=='-1':
        return render_template('uploadSuccess.html')
    label_list=['angry','happy','fear','sad']   # 之后为从数据库读取，各个用户所需标签不同
    return render_template('setLabel.html',label_list=label_list,img_path=img_path)


if __name__ == '__main__':
    app.run(threaded=True,host="0.0.0.0")

