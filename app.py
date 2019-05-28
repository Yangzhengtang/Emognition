from flask import Flask,request,render_template,redirect,flash,session,get_flashed_messages
from Crypto.Util import number #安装时是pycrypto而不是crypto
from pymongo import MongoClient
from flask_bootstrap import Bootstrap
import hashlib
from flask_dropzone import Dropzone
from AlgorithmCore.MiningData import MiningData
from AlgorithmCore.CalculateAssociation import Calculation
from AlgorithmCore.EncryptTransaction import Encrypt
import os

app = Flask(__name__)
# app.config.from_object(config)
app.config["SECRET_KEY"] = os.urandom(24)
bootstrap=Bootstrap(app)
TA_mongo_address,CC_mongo_address='10.162.203.204','10.162.203.204' #数据库所在ip地址
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
dropzone = Dropzone(app)



def security_parameter_gen():
    s = number.getRandomNBitInteger(1020)
    a = number.getPrime(100)
    p = number.getPrime(1024)
    return str(s),str(a),str(p)


def hash_code(s, salt='huyz'):
    md5 = hashlib.md5()
    s += salt
    md5.update(s.encode('utf-8'))
    return md5.hexdigest()


@app.route('/upload', methods = ['POST', 'GET'])
def encryption():
    if request.method=='POST':
        #if not session.get('name'):
            #flash('Please login first')
        return render_template('login.html')
    #    client = MongoClient(host=TA_mongo_address, port=27017)
     #   db = client.user
      #  name = session.get('name')
       # s, a, p = db.user.find_one({'username': name})['s'], db.user.find_one({'username': name})['a'],db.user.find_one({'username': name})['p']
        file=request.files.get('file')
        file = request.files['uploaded_file']
        print("Got the file.")
        #Encrypt(name,CC_mongo_address,file,s,a,p)
        return render_template('uploadSuccess.html')
    return render_template('upload.html')


@app.route('/calculate')
def calculate():
    if not session.get('name'):
        flash('please login first')
        return render_template('login.html')
    client = MongoClient(host=TA_mongo_address, port=27017)
    db = client.user
    name = session.get('name')
    SupAndConf = db.user.find_one({'username': name})['SupAndConfList']
    ruleList=[]
    for x in SupAndConf:
        ruleList.append(x['rule'])
    return render_template('calculate.html', ruleList=ruleList)


@app.route('/calculateEncryption',methods=['POST'])
def mining():
    if request.method == 'POST':
        name = session.get('name')
        file = request.files.get('file')
        MiningData(name,CC_mongo_address,TA_mongo_address,file)
        # prod_1 = str(request.form.get('product_1'))
        # prod_2 = str(request.form.get('product_2'))
        # Ix = list(map(eval, prod_1.split(',')))
        # Iy = list(map(eval, prod_2.split(',')))
        # support_xy, support_x, N = MiningOneData(name,ip,Ix,Iy)
        # client = MongoClient(host=TA_mongo_address, port=27017)
        # db = client.user
        # SupAndConf = db.user.find_one({'username': name})['SupAndConfList']
        # SupAndConf.append({'rule': 'item' + prod_1 + '-->' + 'item' + prod_2, 'support_xy': str(support_xy),
        #                    'support_x': str(support_x), 'N': N, 'k1': len(Ix), 'k2': len(Iy)})
        # db.user.update({'username': name}, {'$set': {'SupAndConfList': SupAndConf}})
        # print('ok')
        flash('计算完成')
    return redirect('/calculate')


@app.route('/all_result')
def all_result():
    client = MongoClient(host=TA_mongo_address, port=27017)
    db = client.user
    name = session.get('name')
    s, a, p = db.user.find_one({'username': name})['s'], db.user.find_one({'username': name})['a'],db.user.find_one({'username': name})['p']
    ruleList,supList,confList=[],[],[]
    SupAndConf = db.user.find_one({'username': name})['SupAndConfList']
    for enc in SupAndConf:
        ruleList.append(enc['rule'])
        k1=enc['k1']
        k2=enc['k2']
        SC_xy=enc['support_xy']
        SC_x=enc['support_x']
        N=int(enc['N'])
        sup,conf=Calculation(k1,k2,s,a,p,SC_xy,SC_x,N)
        supList.append(sup)
        confList.append(conf)
    return render_template('all_result.html',ruleList=ruleList,supList=supList,confList=confList,name=name)



@app.route('/register', methods=['GET', 'POST'])
def register():
    s,a,p=security_parameter_gen()
    if request.method == 'POST':
        username = request.form.get('username')
        password = hash_code(request.form.get('password'))
        confirm_password = hash_code(request.form.get('confirm'))
        insert_info = {'username':username,'password':password,'s':s,'a':a,'p':p,'SupAndConfList':[]}
        if username and password and confirm_password:
            if password != confirm_password:
                flash('两次输入的密码不一致！')
                return render_template('register.html', username=username)

            client = MongoClient(host=TA_mongo_address, port=27017)
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
        client = MongoClient(host=TA_mongo_address, port=27017)
        db = client.user
        collection = db.user.find_one({'username':username})
        if collection['password'] == password:
            # 登录成功后存储session信息
            session['is_login'] = True
            session['name'] = username
            return render_template('welcome.html')
        else:
            flash('用户名或密码错误！')
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


if __name__ == '__main__':
    app.run(threaded=True,host="0.0.0.0")

