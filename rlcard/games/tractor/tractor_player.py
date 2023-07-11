import math
import random
from functools import cmp_to_key

import numpy as np

from tractor_gameUtil import HANDCARD_CNT, CARDS_CNT2, printCard, getNum, getDecor, getKindAndNum, getKind, \
    getDecorAndNum


class Player():
    def __init__(self,id):
        self.id=id
        self.dealerTag=0 #0是庄家，1是庄家跟班，23是闲家
        self.initCards()
    def initCards(self):
        self.cards= [[] for i in range(5)]  # 手牌
        self.uncards = [[] for i in range(5)]  # 已经出的牌
        self.cards_lord=[]# 主牌
        self.len=0
        self.unlen = 0
        self._lordnumAndKing_cnt=np.zeros(6,dtype='int')# 自己所有牌中的级牌和王的数量,级牌是0，1，2，3.小王在4，大王在5

    def initCards_orderCards_cnt(self,env):#初始化orderCards_cnt
        z0 = np.zeros(13 + 5, dtype='int')
        self.orderCards_cnt=[z0.copy(), z0.copy(), z0.copy(),z0.copy(), z0.copy()]
        # orderCards_cnt[i][j]代表类别i的手牌中，顺序是j的有多少个。它包含了所有当前玩家可见的牌
        self.orderCards_len=[0, 0, 0, 0, 0]# 别人已经出的手牌数量
        self.lordNumSee_cnt=np.zeros(4,dtype='int')# 可见级牌数量

        if self.lordDecor==4:
            self.orderCards_len[4]=3#无花色情况下主牌有12张,顺序有3个
            for i in range(4):
                self.orderCards_len[i]=13
        else:
            for i in range(4):
                self.orderCards_len[i] = 12
            self.orderCards_len[self.lordDecor] += 4  # 大小王级牌和主级牌
        self.lordNumOrder=env.getOrderID(54)-3#主级牌的顺序
        for i in range(5):
            for j in range(len(self.cards[i])):
                a=self.cards[i][j]
                if self.isLevelCard(a):#是级牌
                    self.lordNumSee_cnt[getDecor(a)]+=1
                k=env.getOrderID(a)
                # print(a,k)
                self.orderCards_cnt[i][k]+=1
        if self.dealerTag==0:
            for a in env.underCards:
                k=env.getOrderID(a)
                kind,num=getKindAndNum(a,self.lordDecor,self.lordNum)
                self.orderCards_cnt[kind][k] += 1
                if self.isLevelCard(a):
                    self.lordNumSee_cnt[getDecor(a)]+=1
    def isLevelCard(self,a):
        return getNum(a)==self.lordNum and a<53
    def addCard(self,kind,card):
        self.cards[kind].append(card)
        self.len+=1
        decor,num=getDecorAndNum(card)
        if num==self.lordNum:
            self._lordnumAndKing_cnt[decor]+=1
        elif decor==4:
            self._lordnumAndKing_cnt[num-1+4] += 1

    def delCard(self,kind,card):
        self.cards[kind].remove(card)
        self.len-=1
    def delCards(self,cards):
        for a in cards:
            kind=getKind(a,self.lordDecor,self.lordNum)
            self.cards[kind].remove(a)
        self.len-=len(cards)
    def mergeLords(self):#把级牌和大小王放入主牌所在花色，如果是无主则什么都不做
        if self.lordDecor!=4:
            self.cards[self.lordDecor]+=self.cards[4]
            self.cards[4]=[]
    def group(self):#0是庄家，1是闲家
        return self.dealerTag//2
    def isDealer(self):#是否为庄家
        return self.dealerTag<2
    def setNum(self,num):
        self.lordNum = num
    def setLord(self,decor,num):
        self.lordNum = num
        self.lordDecor = decor
        self.cards_lord = self.cards[decor]
    def getLordCnt(self):
        return len(self.cards[self.lordDecor])
    def getSelfMaxCard(self,decor,cmp):#cmp是比较函数，返回i，是牌的次序号，代表大于i的牌都满足cmp，i是从大到小第一个不满足cmp的牌顺序的编号。
        # 该函数返回自己牌以及自己见到的牌当中，某种花色从大到小第一张不满足cmp的顺序
        for i in range(self.orderCards_len[decor]-1,-1,-1):
            if i==self.lordNumOrder:
                for j in range(4):
                    if j!=self.lordDecor and not cmp(self.lordNumSee_cnt[j]):
                        return i
            elif not cmp(self.orderCards_cnt[decor][i]):
                return i
        return -1
    def updateSortCardsList(self,env):
        self.sortCardsList2=self.toSortCardsList2(env)
        self.sortCardsList1=self.toSortCardsList1(self.sortCardsList2,env)
    def toSortCardsList1(self,sortCardList2,env):#去重
        li=[]
        for i in range(5):
            # oneList, doubleList, traList = env.sortCardList1(self.cards_decorList[i])
            li.append((env.sortCardList1(sortCardList2[i][0],sortCardList2[i][1],sortCardList2[i][2])))
        return li
    def toSortCardsList2(self,env):#相互包含
        li=[]
        for i in range(5):
            # oneList, doubleList, traList = env.sortCardList1(self.cards_decorList[i])
            li.append((env.sortCardList2(self.cards[i][0:len(self.cards[i])])))
        return li
    def printCards(self):
        print("玩家{}".format(self.id),end=" ")
        k=0
        for i in  range(5):
            for j in range(len(self.cards[i])):
                printCard(self.cards[i][j],k)
                k+=1
        print("")
    def addCardsList(self,env,cards):
        cnt=0
        for a in cards:
            if a<=0 or a>54:
                continue
            cnt+=1
            order = env.getOrderID(a)
            kind, num = getKindAndNum(a,self.lordDecor,self.lordNum)
            decor=getDecor(a)
            self.uncards[kind].remove(a)
            self.cards[kind].append(a)
            env.undeck.remove(a)
            for i in range(4):
                if i != self.id:
                    env.players[i].orderCards_cnt[kind][order] -= 1
                    if num == self.lordNum and decor < 4:
                        env.players[i].lordNumSee_cnt[decor] -= 1
        self.len+=cnt
        self.unlen-=cnt
    def useCardsList(self,env,cards):
        cnt=0
        for a in cards:
            if a<=0 or a>54:
                continue
            cnt+=1
            order = env.getOrderID(a)
            kind, num = getKindAndNum(a,self.lordDecor,self.lordNum)
            decor = getDecor(a)
            self.cards[kind].remove(a)
            self.uncards[kind].append(a)
            env.undeck.append(a)
            for i in range(4):
                if i != self.id:
                    env.players[i].orderCards_cnt[kind][order] += 1
                    if num == self.lordNum and decor < 4:
                        env.players[i].lordNumSee_cnt[decor] += 1
        self.len-=cnt
        self.unlen+=cnt
    def useAction(self,env,act):
        self.useCardsList(env, act.one)
        for dou in act.double:
            self.useCardsList(env, dou)

    def otherKindCards(self, kind):  # 获取所有kind以外类别的牌
        ans = []
        for i in range(5):
            if i!=kind:
                ans += self.cards[i].copy()
        return ans
