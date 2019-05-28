#在linux环境下（windows环境下）
1.sudo pip install virtualenv  *安装virtualenv虚拟环境
2.进入到项目目录下 执行 virtualenv -p python3 venv    *创建虚拟环境venv
3.执行 source venv/bin/activate   *激活虚拟环境（在windows环境下这步改为 venv\Scripts\activate 其余步骤都相同）
4.执行 pip install -r requirement.txt   *安装相关依赖
5.执行 python app.py 后在本机127.0.0.1:5000 可访问


在利用gunicorn+nginx的情况下可以在内网范围进行访问，至于如何部署到服务器上还有待研究。。