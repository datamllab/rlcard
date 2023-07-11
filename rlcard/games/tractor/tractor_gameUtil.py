import math
import random
from functools import cmp_to_key
import numpy as np


CARDS_CNT=108
CARDS_CNT2=54
UNDERCARD_CNT=8
INF=1000
HANDCARD_CNT = (CARDS_CNT - UNDERCARD_CNT) // 4
fenInd=[0,0,0,0,0,5,0,0,0,0,10,0,0,10,0,0,0,0,0,0]
decorName=["♠","♥","♣","♦","王"]
NameTodecorId={"♠":0,"♥":1,"♣":2,"♦":3,"王":4}
numName=["","A","2","3","4","5","6","7","8","9","10","J","Q","K"]

def getKind(id,dec,num):  # id从1开始，判断类别，会把级牌和王算进主牌里
    if id<1:
        return 0
    d = (id - 1) // 13  # 黑桃是0，红糖是1，梅花是2，方片是3，王是4
    n= (id - 1) % 13 + 1  # 点数
    if d==4 or n==num:
        return dec
    return d
def getDecor(id):  # id从1开始，判断花色
    return int((id - 1) // 13)
def getNum(id):  # id从1开始，判断点数
    return int((id - 1) % 13+1)
def getDecorAndNum(id):
    if id<1:
        return 0,0
    decor = (id - 1) // 13  # 黑桃是0，红糖是1，梅花是2，方片是3，王是4
    num = (id - 1) % 13 + 1  # 点数
    return int(decor),int(num)
def getKindAndNum(id,dec,num):
    if id<1:
        return 0,0
    d = (id - 1) // 13  # 黑桃是0，红糖是1，梅花是2，方片是3，王是4
    n = (id - 1) % 13 + 1  # 点数
    if d==4 or n==num:## 黑桃是0，红糖是1，梅花是2，方片是3，王是4
        return dec,num
    return int(d),int(n)
def toCardIndex(decor,num):
    return num+decor*13
def cardToString(id,up=False):#
    decor, num = getDecorAndNum(id)
    if id == INF:
        return "<任意>"
    elif num == 0:
        return "<null>"
    elif decor == 4:
        return "<"+ (num == 1 and "小" or "大") + "王>"
    else:
        return "<" + decorName[decor] + numName[num] + ">"
stringToCardId={}
def initStringToCard():
    stringToCardId["INF"]=INF
    stringToCardId["大王"] = 54
    stringToCardId["小王"] = 53
    for i in range(1,CARDS_CNT2+1):
        stringToCardId[cardToString(i)]=i
        stringToCardId[cardToString(i).lower()] = i
        stringToCardId[cardToString(i)[1:-1]] = i
        stringToCardId[str(i)] = i
initStringToCard()

def printCard(id,i=0):
    decor,num=getDecorAndNum(id)
    if id==INF:
        print("<i:{} ".format(i) + "任意 >", end=" ")
    elif num==0:
        print("<i:{} ".format(i)+ "null >", end=" ")
    elif decor==4:
        print("<i:{} ".format(i)+(num==1 and "小"or"大") + "王>", end=" ")
    else:
        print("<i:{} ".format(i)+decorName[decor]+numName[num]+">",end=" ")
def printCardln(id,i=0):
    printCard(id,i)
    print("")
def snatchLord_v0(env,p,round,allActList):#发牌时候抢主的常规策略
    if env.lordDecor>=0:
        return -1

    for i in range(4):
        p=env.players[id]
        c=p.cards_decorLen[i]+p.cards_decorLen[4]

        if  c>=0 :#没人亮过，超过均值就亮牌,且牌数大于等于4,主牌一共36个，平局每人9个
            for j in range(p.cards_decorLen[4]):
                decor,num=getDecorAndNum(p.cards_decorList[4][j])
                if num ==env.lordNum and decor==i:  # 有级牌
                    return i
    return -1
def randomUpdateINF(roundId,p,act:list, kind):#随机选取动作，kind是第一个出牌的玩家的花色。返回种类和在cards_decorList中位置的编号
    actList=[]
    for j in range(p.cards_decorLen[kind]):#先看本花色有木有
        if p.cards_decorList[kind][j]!=0:
            actList.append((kind,j))
    if len(actList)==0:#本花色没有，去其它花色找
        for i in range(5):
            if i==kind or p.cards_decorLen[i]==0:
                continue
            for j in range(p.cards_decorLen[i]):
                if p.cards_decorList[i][j] != 0:
                    actList.append((i,j))
    ans=actList[random.randint(0,len(actList)-1)]
    return ans[0],ans[1]
def getAllAct(self, sortCardsList, p, cardsList_max, kind):  # sortCardsList是p玩家分好类的手牌
    # 返回所有大过之前最大的玩家的牌和小于之前玩家的牌
    # cardsList_max只能是单张，对子，连对
    # 小于玩家的牌有太多组合会被忽略
    n = len(cardsList_max)
    ansUp = []
    ansDown = []
    if n == 1:  # 单张牌
        ansDown = self.getFollowAct_one(p, cardsList_max[0], kind)
        if kind == self.lordDecor or p.cards_decorLen[kind] > 0:  # 是主牌或副牌，但有这类副牌
            for i in range(p.cards_decorLen[kind]):
                a = p.cards_decorList[kind][i]
                if self.orderInd[a] > self.orderInd[cardsList_max[0]]:
                    ansUp.append([a])
def getActListFen(actList:list):#得到动作列表的所有分
    ans=0
    for act in actList:
        ans+=act.getFen()
    return ans
def searchFen(cardList):
    ans=0
    for a in cardList:
        num=getNum(a)
        ans+=fenInd[num]
    return ans

# env=CC()
# env.dealCards(None,0,5,0)#发牌测试
# # env.dfsPrintActList([9,27])
# act1=Action([],[[4,4,6,6],[10,10]])
# act2=Action([],[[8,8,9,9],[11,11]])
# print(env.useCmpCards(act1,act2))
# <i:0 ♠9>
# <i:0 ♦A>
# <i:0 ♦10>
# <i:0 ♦9>
# actList,doubleList,traList=env.sortCardList2([11,11,12,12,13,13,14,1,2,3,4,5,5,6,15,6,8,8,9,9])
# print(actList,doubleList,traList)
# ansDown=[]
# nowList=[]
# begin_time = time.time()
# env.getAllAct_dfs(doubleList,0,ansDown,nowList,0,4)
# passed_time = time.time() - begin_time
# print(ansDown)
# print(passed_time)
# li=[39, 39, 23, 12, 26, 5, 53, 1, 38, 30, 46, 54, 48, 40, 36, 6, 28, 46, 26, 18, 7, 16, 27, 5, 22, 20, 47, 41, 41, 34, 8, 3, 31, 30, 13, 16, 23, 15, 48, 13, 51, 4, 37, 44, 33, 25, 52, 34, 9, 37, 21, 3, 17, 50, 29, 24, 51, 49, 38, 35, 43, 24, 6, 18, 32, 22, 29, 7, 20, 11, 19, 15, 36, 14, 42, 27, 45, 14, 12, 50, 45, 52, 31, 11, 42, 40, 47, 33, 54, 32, 8, 21, 10, 49, 9, 25, 53, 44, 1, 4, 17, 19, 10, 2, 35, 43,28,2]
# env.dealCards()#发牌测试
# env=CC()
# env.dealCards()
# # actList,doubleList,traListt=env.sortCardList2(li)
# # print(env.dfsPrintActList(actList))
# li=np.zeros(33,dtype=np.int32)
# li[0]=2
# li = sorted(li, key=cmp_to_key(env._sortCardList_cmp1))
# env.dfsPrintActList(li)
# print(env.orderInd)
# actList, doubleList, traListt =env.sortCardList2([1,3,53,53,5,5,31,31,3,4,4,6,6,8,8,11,12,1])
# env.dfsPrintActList(actList)
# env.dfsPrintActList(doubleList)
# env.dfsPrintActList(traListt)




