from pymongo import MongoClient
from multiprocessing import Pool
from functools import reduce
from configparser import ConfigParser

def CalculateRule(association_rule):
    db=MongoClient(CC_mongo_address).encrypted
    itemset=association_rule.split('->')
    Ix,Iy=itemset[0].split(','),itemset[1].split(',')
    support_x,support_xy=0,0
    N = db[collection_name].count_documents({})
    for t in db[collection_name].find():
        sub_support_x=reduce(lambda x,y:x*y,map(lambda item:int(t[item]),Ix))
        sub_support_xy=sub_support_x*reduce(lambda x,y:x*y,map(lambda item:int(t[item]),Iy))
        support_x+=sub_support_x
        support_xy+=sub_support_xy
    db=MongoClient(TA_mongo_address).user
    SupAndConf = db.user.find_one({'username': name})['SupAndConfList']
    SupAndConf.append({'rule': 'item' + itemset[0] + '-->' + 'item' + itemset[1], 'support_xy': str(support_xy),
                       'support_x': str(support_x), 'N': N, 'k1': len(Ix), 'k2': len(Iy)})
    db.user.update({'username': name}, {'$set': {'SupAndConfList': SupAndConf}})
    # db.insert_one({'rule':association_rule,'xy':str(support_xy),'x':str(support_x),'N':str(db[collection_name].count_documents({}))})
        
def MiningData(username,CC_mongo_ip,TA_mongo_ip,config):
    global CC_mongo_address,TA_mongo_address,collection_name,name
    rule = config.readline().decode().split()
    CC_mongo_address,TA_mongo_address,collection_name,name=CC_mongo_ip,TA_mongo_ip,username,username
    pool=Pool()
    pool.map(CalculateRule,rule)
    pool.close()

