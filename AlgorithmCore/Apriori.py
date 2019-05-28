from Crypto.Util import number
from pymongo import MongoClient
from functools import reduce
from itertools import combinations,dropwhile
from configparser import ConfigParser
from pprint import pprint

class Apriori(object):
    def __init__(self,username):
        cf=ConfigParser()
        cf.read('config.ini')
        self.db=MongoClient(cf.get(username,'MONGO_ADDRESS'))[cf.get(username,'DATABASE_NAME')]
        self.decryptor=Decryptor(self.db)
    def FilterSupport(self,C,min_support,k):
        support_list=[0 for itemset in C]
        for t in self.db.encrypted.find():
            sub_support_list=(reduce(lambda x,y:x*y,map(lambda item:int(t[item]),itemset)) for itemset in C)
            support_list=[x+y for x,y in zip(support_list,sub_support_list)]
        return list(filter(lambda i:i[1]>=min_support,zip(C,self.decryptor.Decrypt(support_list,k))))
    def Run(self,min_support,min_confidence):
        min_support*=self.db.encrypted.count_documents({})
        L=self.FilterSupport([(str(i),) for i in range(1000)],min_support,1)
        itemset_length,L_length=1,len(L)
        frequent_itemsets=L
        while L_length>itemset_length:
            C=[]
            for i in range(L_length):
                j=i+1
                while j<L_length and L[i][0][:-1]==L[j][0][:-1]:
                    C.append(L[i][0]+L[j][0][-1:])
                    j+=1
            L=set(map(lambda itemset:itemset[0],L))
            C=list(filter(lambda itemset:set(tuple(combinations(itemset,itemset_length))[2:]).issubset(L),C))
            if not C:
                break
            itemset_length+=1
            L=self.FilterSupport(C,min_support,itemset_length)
            L_length=len(L)
            frequent_itemsets.extend(L)
        return self.FindRules(frequent_itemsets,min_confidence)
    def FindRules(self,itemsets,min_confidence):
        support_dict=dict(itemsets)
        association_rules=set()
        N=self.db.encrypted.count_documents({})
        for i in dropwhile(lambda itemset:len(itemset[0])==1,itemsets):
            condition_length,rule=len(i[0])-1,set(((i[0],),))
            while condition_length and rule:
                candidates=reduce(lambda x,y:x|y,map(lambda can:set(combinations(can[0],condition_length)),rule))
                rule=set(filter(lambda rule:rule[3]>=min_confidence,map(lambda can:(can,i[0],i[1]/N,i[1]/support_dict[can]),candidates)))
                condition_length-=1
                association_rules|=rule
        return association_rules
        
class Decryptor(object):
    def __init__(self,db):
        sp=db.security_parameter.find_one()
        self.a,self.p,self.s=int(sp['a']),int(sp['p']),int(sp['s'])
    def Decrypt(self,support_list,k):
        return map(lambda support:number.inverse(self.s**k,self.p)*support%self.p//self.a**k,support_list)

association_rules=Apriori('user0').Run(0.05,0.5)
pprint(association_rules)
