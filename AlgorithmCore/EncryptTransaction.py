from Crypto.Util import number
from Crypto.Random import atfork
from pymongo import MongoClient
from multiprocessing import Pool
from configparser import ConfigParser

class Transaction(object):
    def __init__(self,item_set,item_num=1000):
        self.item=[int(str(i) in item_set) for i in range(item_num)]
    def encrypt(self,s,a,p):
        return {str(i):str(s*(a*value+number.getRandomNBitInteger(25))%p) for i,value in enumerate(self.item)}
    
# def init(username):
#     cf=ConfigParser()
#     cf.read('config.ini')
#     m,db,ds=cf.get(username,'MONGO_ADDRESS'),cf.get(username,'DATABASE_NAME'),cf.get(username,'DATASET_NAME').split(',')
#     sp=MongoClient(m)[db]['security_parameter'].find_one()
#     return (m,db,ds,int(sp['a']),int(sp['p']),int(sp['s']))
    
def EncryptTransaction(line):
    atfork()
    item_list=line.decode().split()
    transaction=Transaction(item_list)
    MongoClient(CC_mongo_address).encrypted[collection_name].insert_one(transaction.encrypt(s,a,p))
    
def Encrypt(username,ip,dataset,Parameter_s,Parameter_a,Parameter_p):
    global CC_mongo_address,collection_name,s,a,p
    CC_mongo_address,collection_name,s,a,p=ip,username,int(Parameter_s),int(Parameter_a),int(Parameter_p)
    pool=Pool()
    pool.map(EncryptTransaction,dataset)
    pool.close()
