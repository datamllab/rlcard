import math
import random
from functools import cmp_to_key
import numpy as np

from tractor_gameUtil import getNum, fenInd, printCard, cardToString, INF, getKind


class Action():
    def __init__(self, one=[],double=[],playerId=-1):  # double里包含对子和拖拉机，如[[3,3],[4,4,5,5]]
        self.one=one.copy()
        self.double = double.copy()
        self.len=len(one)
        self.playerId=playerId
        for dou in double:
            self.len+=len(dou)
    def add(self,one=[],double=[]):
        for a in one:
            self.one.append(a)
        self.len += len(one)
        for dou in double.copy():
            self.double.append(dou)
            self.len += len(dou)
    def addOne(self,a):
        self.one.append(a)
        self.len += 1
    def addDou(self,dou):
        self.double.append(dou.copy())
        self.len+=len(dou)
    def setDou(self,i,dou):
        if i<len(self.double):
            self.len += len(dou) - len(self.double[i])
            self.double[i]=dou
        elif i==len(self.double):
            self.double.append(dou)
            self.len += len(dou)
    def isCombination(self):#判断是否为甩牌
        return len(self.one)+len(self.double)>1
    def getDouleCnt(self):#返回对子数量
        return (self.len-len(self.one))//2
    def getDouleLen(self):#返回对子数组长度
        return len(self.double)
    def isSeq(self):#是否为甩牌
        return len(self.double)+len(self.one)>1
    def getFen(self):
        sc=0
        for dou in self.double:
            for a in dou:
                num = getNum(a)  # 点数，[1,13]王是14
                sc += fenInd[num]  # 分数
        for a in self.one:
            num = getNum(a)  # 点数，[1,13]王是14
            sc += fenInd[num]  # 分数
        return sc
    def print(self,i=0):
        print("act"+str(i)+":",end="")
        i=0
        for dou in self.double:
            for a in dou:
                printCard(a,i)
                i+=1
        for a in self.one:
            printCard(a,i)
            i+=1
    def println(self,i=0):
        self.print(i)
        print("")
    def toString(self):
        ans=""
        for dou in self.double:
            for a in dou:
                ans+=cardToString(a)
        for a in self.one:
            ans+=cardToString(a)
        return ans

    def tolist(self):
        li=self.one.copy()
        for dou in self.double:
            for a in dou:
                li.append(a)
        return li
    def getKind(self,env):
        if len(self.one)>0:
            return getKind(self.one[0],env.lordDecor,env.lordNum)
        return getKind(self.double[0][0], env.lordDecor, env.lordNum)
    def sort(self,env):
        self.one.sort(key=cmp_to_key(env._sortCardList_cmp1))
        for dou in self.double:
            dou.sort(key=cmp_to_key(env._sortCardList_cmp1))
    def getMinCard(self,env):#返回最小的牌
        mincard=0
        minOrder=INF
        for dou in self.double:
            for a in dou:
                if minOrder>env.orderInd[a]:
                    minOrder =env.orderInd[a]
                    mincard=a
        for a in self.one:
            if minOrder > env.orderInd[a]:
                minOrder = env.orderInd[a]
                mincard = a
        return Action([a])

def __dfsPrintActList(newLi, li0,printFun=None):#printFun是打印这张牌的条件
    if isinstance(li0,np.ndarray):
        n=li0.shape[0]
    else:
        n=len(li0)

    for i in range(n):
        if isinstance(li0[i],int) or isinstance(li0[i],np.int32) or isinstance(li0[i],np.int64):
            if printFun==None or printFun(li0[i]):
                newLi.append(cardToString(li0[i]))
        elif isinstance(li0[i],Action):
            if printFun==None or printFun(li0[i]):
                newLi.append(li0[i].toString())
        else:
            t=[]
            __dfsPrintActList(t,li0[i])
            if printFun==None or printFun(t):
                newLi.append(t)
def dfsPrintActList(li,printFun=None):
    newLi=[]
    if isinstance(li,int) or isinstance(li,np.int32):
        newLi.append(cardToString(li))
    elif isinstance(li,Action):
        newLi.append(li.toString())
    else:
        __dfsPrintActList(newLi,li,printFun)
    print(newLi)

def cardsListToAction(env,pid,cards):#cards只有一个类型
    li=(env.sortCardList2(cards))
    li=(env.sortCardList1(li[0], li[1], li[2]))
    dou=[]
    for a in li[1]:
        dou.append([a,a])
    for tra in li[2]:
        dou.append([tra[i//2] for i in range(len(tra)*2)])
    act = Action(li[0], dou, playerId=pid)
    act.sort(env)
    return act
