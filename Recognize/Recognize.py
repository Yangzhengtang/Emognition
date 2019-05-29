def recognition(photo,model):
    '''
    利用训练好的模型对photo进行识别
    :param photo:文件格式，需要识别的照片
    :param model:文件格式，在前端选择的.h5模型
    :return:photofile_labeled 打好标签并框选出人脸的照片
    '''


def train(label,photofile):
    '''
    先把photofile和label存入数据库，并放入某个文件夹下，把label和photofile放入网络训练，也是调用os.system()
    :param label: 目前先通过下拉栏给用户有限的选项
    :param photofile: 待放入网络训练的数据
    :return: new_photofile_labeled（通过新训练好的网络对刚刚用户输入的Photofile的预测，和用户给的标签可以进行对比）,new_accuary（返回新的准确度数组，现在可能实现不了，先放着）
    '''
