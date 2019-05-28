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
app.config['MAX_CONTENT_LENGTH'] = 512 * 1024 * 1024    # 最大上传文件大小
dropzone = Dropzone(app)


def hash_code(s, salt='huyz'):
    md5 = hashlib.md5()
    s += salt
    md5.update(s.encode('utf-8'))
    return md5.hexdigest()


@app.route('/upload', methods = ['POST', 'GET'])
def upload():
    if request.method=='POST':  # POST表示提交了文件
        # if not session.get('name'): # 验证登录
        #     flash('please login first')
        #     return render_template('login.html')
        file = request.files['file']
        count=0
        fname=file.filename
        while os.path.exists(os.path.join('TmpUploadDir', fname)):  # 防止文件名重复
            fname=file.filename[:file.filename.find('.')]+"_{:.0f}".format(count)+file.filename[file.filename.find('.'):]
            count+=1
        file.save(os.path.join('TmpUploadDir', fname))  # 保存到临时文件夹
        print(type(file))
        print("Got the file.")
        # return render_template('upload.html')
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

            client = MongoClient(host=mongo_address, port=27017)
            db = client.user
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
        client = MongoClient(host=mongo_address, port=27017)
        db = client.user
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

if __name__ == '__main__':
    app.run(threaded=True,host="0.0.0.0")

