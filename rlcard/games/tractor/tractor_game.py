import math
import random
from functools import cmp_to_key

import numpy as np

from tractor_action import Action, dfsPrintActList, cardsListToAction
from tractor_gameUtil import CARDS_CNT2, HANDCARD_CNT, UNDERCARD_CNT, CARDS_CNT, getKindAndNum, INF, getKind, fenInd, \
    getNum, decorName, getDecor, toCardIndex, printCard, printCardln
from tractor_player import Player


class Tractor():
    def __init__(self):
        self.undeck = []  # 存数组
        self.reset_game()
    def __reset(self):
        self.players = [Player(0), Player(1), Player(2), Player(3)]  # 0代表没有
        self.lordDecor = -1  # 主牌花色
        self.sumSc = 0  # 闲家得分
        self.underCards = []
        self.nowDealCardPlayer = 0  # 当前到发牌的玩家
        self.round_i = 0  # 轮数
        self.deck = [i%CARDS_CNT2+1 for i in range(CARDS_CNT)]
        self.useCards_i=0#放回deck

    def reset_game(self):#重置游戏进度
        self.__reset()
        self.roundGame_i=0
        self.levelOfBoth = [2, 2]
        self.dealer = -1
        self.lordNum = 2  # 级牌
        for i in range(4):
            self.players[i].setNum(2)
    def calcGameScore(self):#结算一局游戏的分数，更新级牌,但不重置游戏进度,preSc代表上局闲家的分数,返回-1代表继续游戏，返回庄家编号代表谁先达到A
        preSc=self.sumSc
        self.__reset()
        grade = self.getGrade(preSc)#结算等级
        if grade>=0:#换庄
            g=grade
            self.dealer =(self.dealer+1)%4#换庄
            a = self.levelOfBoth[self.dealer%2]
            if 2<=a <= 5:  # 5，10，k不能跳
                self.levelOfBoth[self.dealer%2] = min(a + g, 5)
            elif 5<a <=10:
                self.levelOfBoth[self.dealer%2] = min(a + g, 10)
            elif 10<a <=13:
                self.levelOfBoth[self.dealer%2] = min(a + g, 13)
            else:
                self.levelOfBoth[self.dealer%2]=1
                if g>0:
                    return self.getWinPlayer(),self.dealer,grade
        else:
            g = -grade
            self.dealer = (self.dealer + 2) % 4  # 换同伙坐庄
            a = self.levelOfBoth[self.dealer%2]
            if 2 <= a < 5:  # 5，10，k不能跳
                self.levelOfBoth[self.dealer % 2] = min(a + g, 5)
            elif 5 <= a < 10:
                self.levelOfBoth[self.dealer % 2] = min(a + g, 10)
            elif 10 <= a < 13:
                self.levelOfBoth[self.dealer % 2] = min(a + g, 13)
            else:
                self.levelOfBoth[self.dealer % 2] = 1
                if a==1 or a==13 and g>1:
                    return self.getWinPlayer(),self.dealer,grade
        self.lordNum=self.levelOfBoth[self.dealer%2]
        self.roundGame_i+=1
        for i in range(4):
            self.players[i].setNum(self.lordNum)
        return self.getWinPlayer(),-1,grade
    def getWinPlayer(self):
        grade = self.getGrade(self.sumSc)  # 结算等级
        winplayer=self.dealer
        if grade>=0:
            winplayer=(winplayer+1)%4
        return winplayer
    def setDealerID(self,dealer):
        self.players[dealer].dealerTag=0
        self.players[(dealer+1)%4].dealerTag = 2
        self.players[(dealer+2)%4].dealerTag = 1
        self.players[(dealer + 3) % 4].dealerTag =3

    def getNowUsedCards(self):
        cardList=self.deck[0:self.useCards_i]
        return cardList

    def _updateSortCardList(self,sortCardList:list,act:list):
        if sortCardList == None:
            return
        for a in act:  # 刷新sortCardList
            kind, num = getKindAndNum(a, self.lordDecor, self.lordNum)
            li = sortCardList[kind]  # 遍历这个花色
            for i in range(len(li[0])):  # 从单牌里删除
                if li[0][i] == a:
                    li[0].pop(i)
                    break
            for i in range(len(li[1])):  # 从对子里删除
                if li[1][i] == a:
                    li[1].pop(i)
                    break
            # print(sortCardList)
            for i in range(len(li[2])):
                # print(li[2])
                m = len(li[2][i])
                for j in range(m):  # 遍历每个拖拉机
                    if li[2][i][j] == a:
                        tra = li[2].pop(i)
                        beginTra = tra[:j]
                        endTra = tra[j + 1:]
                        if len(beginTra) > 1:  # 剩下的长度大于1，放回li[2]
                            li[2].append(beginTra)
                        if len(endTra) > 1:  # 剩下的长度大于1，放回li[2]
                            li[2].append(endTra)
                        break
                else:#这段用来代替goto,表示找到if时，跳出2层循环。python用goto要单独安装包
                    continue
                break
            # print(sortCardList)
            li[2].sort(key=cmp_to_key(self._sortCardList_cmp2))

    def checkReDealCards(self):
        if self.lordDecor<4 and self.players[0].getLordCnt()+ self.players[2].getLordCnt()<10:
            return True
        if self.lordDecor<4 and self.players[1].getLordCnt()+ self.players[3].getLordCnt()<10:
            return True
        # for i in range(4):
        #     if self.players[i].getLordCnt()>=HANDCARD_CNT-2: #一个人几乎全是主牌，可以重开
        #         return True
        #     fen=0
        #     p=self.players[i]
        #     for j in range(HANDCARD_CNT):
        #         fen+=fenInd[getNum(int(p.cards[j]))]
        #     if fen<15:
        #         return True
        return False
    def printCardsList(self,li,up=-1):
        if up<0:
            up=len(li)
        for i in range(up):
            printCard(li[i],i)
        print("")
    def printAllCards(self):
        for i in range(4):
            self.players[i].printCards()
        print("底牌",end=": ")
        self.printCardsList(self.deck[-8:])
    # def getBidAction(self,):

    def CrossShuffle(self):#交叉洗牌
        for i in range(CARDS_CNT // 2-1,-1,-1):  # 交叉洗牌
            rnd1, rnd2 = i, i * 2
            self.deck[rnd1], self.deck[rnd2] = self.deck[rnd2], self.deck[rnd1]

    def shuffleDeck(self,T=10):
        up=len(self.deck)-1
        self.CrossShuffle()
        # print(self.deck)
        while(T>0):
            self.CrossShuffle()

            for i in range(up, 0, -1):
                rnd = random.randint(0, i)  # 每次随机出0-i-1之间的下标
                self.deck[i], self.deck[rnd] = self.deck[rnd], self.deck[i]
            T-=1


    def dealCards(self,beginDeckList,bidFun,lordInfo=(-1,-1,-1)):#
        # 发牌,bidFun是叫牌策略
        #setDecor=-1,setNum=-1,setDealer=-1代表
        setDecor, setNum , setDealer=lordInfo[0],lordInfo[1],lordInfo[2]
        if beginDeckList is None:
            self.shuffleDeck()  # 洗牌
        else:
            for i in range(len(self.deck)):
                self.deck[i]=beginDeckList[i]
        # print(self.deck.tolist())
        self.deck_i = 0
        self.nowDealCardPlayer = 0
        for i in range(4):
            self.players[i].initCards()
        #bidFun(env,round,allActList)
        isSet=setDecor!=-1 or setDealer!=-1 or setNum>0
        if isSet:#人为设置，调试用
            self.lordNum = setNum

            print("指定主牌:",decorName[setDecor]+str(setNum),"   庄家：",setDealer)
            self.dealer = setDealer
            self.bidAns = [toCardIndex(setDecor,self.lordNum)]
            self.bidPlayer =setDealer
            while (self.deck_i < CARDS_CNT - UNDERCARD_CNT):
                self.__dealCard(bidFun)
            self.setLord(setDecor, setDealer)
        else:
            self.bidAns=[]
            self.bidPlayer =-1
            while (self.deck_i < CARDS_CNT - UNDERCARD_CNT):
                self.__dealCard(bidFun)
            if self.bidPlayer!=-1:
                if self.dealer==-1:
                    self.setLord(getDecor(self.bidAns[0]), self.bidPlayer)
                else:
                    self.setLord(getDecor(self.bidAns[0]))
            else:# 如果没人叫主，则重新发牌
                # print("重新发牌")
                self.dealCards(beginDeckList, bidFun, lordInfo)
        for i in range(4):
            p=self.players[i]
            p.mergeLords()
            self.sortPlayerHand(p)
        self.setDealerID(self.dealer)

        self.undeck = []  # 存数组
        if self.checkReDealCards() and not isSet:  # 满足一定条件可以重开
            # print("重新发牌")
            self.dealCards(beginDeckList, bidFun, lordInfo)


    def __dealCard(self,bidFun):#发牌
        card=self.deck[self.deck_i]
        p=self.players[self.nowDealCardPlayer]
        p.addCard(getKind(card,4,self.lordNum),card)#级牌放入无主里
        allActList=[[]]#空列表代表不叫牌
        for i in range(4):
            a=toCardIndex(i, self.lordNum)
            n=len(self.bidAns)
            if p._lordnumAndKing_cnt[i]==1 and n==0:
                allActList.append([a])
            elif p._lordnumAndKing_cnt[i]==2 and n==0:
                allActList.append([a])
                allActList.append([a,a])
            elif p._lordnumAndKing_cnt[i]==2 and n==1:
                allActList.append([a,a])
        if p._lordnumAndKing_cnt[4]==2 and (len(self.bidAns)<2 or len(self.bidAns)==2 and self.bidAns[0]<53):#对小王可以反无主
            allActList.append([53,53])
        if p._lordnumAndKing_cnt[5]==2 and (len(self.bidAns)<2 or len(self.bidAns)==2 and self.bidAns[0]<54):#对大王可以反无主
            allActList.append([54,54])
        # dfsPrintActList(allActList)
        act_id = bidFun(self,p,self.deck_i//4,allActList)
        act=allActList[act_id]
        self.deck_i += 1
            # self.snatchLord_v0(self.nowDealCardPlayer)  # 抢主

        #self.printAllCards()
        if len(act) > 0 :
            # print("玩家"+str(self.nowDealCardPlayer)+"叫了：",end=" ")
            dfsPrintActList(act)
            self.bidAns=act
            self.bidPlayer=self.nowDealCardPlayer
        self.nowDealCardPlayer=(self.nowDealCardPlayer+1)%4

    def setUnderCards(self,discardFun):#换牌，
        p = self.players[self.dealer]
        self.underCards=[]
        for a in self.deck[-8:]:
            p.addCard(getKind(a,self.lordDecor,self.lordNum),a)
        self.sortPlayerHand(p)
        for i in range(8):
            a=discardFun(self,p,i)#选择八张底牌扣下
            self.underCards.append(a)
            p.delCard(getKind(a,self.lordDecor,self.lordNum),a)
        if len(self.underCards)!=UNDERCARD_CNT:
            print("erro",self.underCards)
            exit()
        # dfsPrintActList(self.underCards)
        self.deck[-8:]=self.underCards
        self.sortPlayerHand(p)

        for i in range(4):
            self.players[i].initCards_orderCards_cnt(self)
        # for i in range(5):
        #     env.printCardsList(p.cards_decorList[i], p.cards_decorLen[i])
        # print("")
    def setOrder(self):#设置单牌的大小
        self.orderInd = np.zeros((CARDS_CNT+1),dtype='int')
        self.decorInd = np.zeros((CARDS_CNT + 1),dtype='int')#花色分类，大小王和级牌都算主牌里
        h=CARDS_CNT//2
        self.orderInd[0]=-1
        self.orderInd[h]=99#大王
        self.orderInd[h-1]= 98  # 小王
        for j in range(4):
            for i in range(1,14):
                self.orderInd[j*13+i]=i
                self.decorInd[j * 13 + i] =j
            self.orderInd[j * 13+1] =14#A更大
        for i in range(1, 14):#主牌更大
            self.orderInd[self.lordDecor * 13 + i]=i+40
            self.decorInd[self.lordDecor * 13 + i] = 4
        self.orderInd[self.lordDecor * 13 + 1]= 14+40  # A更大
        for i in range(4):#级牌
            self.orderInd[self.lordNum+i*13]=60
            self.decorInd[self.lordNum+i*13] = 4
        self.orderInd[self.lordNum + self.lordDecor * 13] =  61

        #紧凑化
        ind=[0]*100
        for i in range(1,h+1):
            d=int(self.orderInd[i])
            ind[d]+=1
        k=1
        for i in range(1,100):
            if ind[i]>0:
                ind[i] = k
                k+=1
        for i in range(1,h+1):
            self.orderInd[h+i] = self.orderInd[i]=ind[int(self.orderInd[i])]
            self.decorInd[h+i] = self.decorInd[i]
        self.unlordMax=self.lordDecor==4 and 13 or 12#无主就是13

    def getDecor(self,id):#id从1开始
        return (id - 1) // 13
    def cmpCard(self,a,b):#比较两组牌大小。返回1是a大，返回0是b大
        if a==0 or b==0 :
            return b==0
        # print(self.orderInd)
        num1=self.orderInd[a]
        num2=self.orderInd[b]
        d1, d2 = self.getDecor(a), self.getDecor(b)
        if num1<=self.unlordMax and num2<=self.unlordMax:#都不是主
            if d1==d2:#花色相同
                return num1>=num2
            else:
                return d1>=d2
        elif num1>self.unlordMax and num2>self.unlordMax:  # 都是主牌
            if num1==num2:#地位相同
                return d1>=d2
            else:
                return num1>num2
        return num1>self.unlordMax
    def _sortCardList_cmp(self,a,b):#比较两组牌大小。返回1是a大，返回-1是b大
        if self._ind[a]>1 and self._ind[b]>1 or self._ind[a]==1 and self._ind[b]==1:
            num1 = self.orderInd[a]
            num2 = self.orderInd[b]
            if num1<=self.unlordMax and num2<=self.unlordMax:#都不是主牌
                if self.getDecor(a) == self.getDecor(b):  # 花色相同
                    return num1 >= num2 and -1 or 1
                return self.getDecor(a) > self.getDecor(b) and -1 or 1
            return num1>=num2 and -1 or 1
        elif self._ind[a]>1:
            return -1
        return 1
    def _sortCardList_cmp1(self,a,b):#比较两组牌大小。返回1是a大，返回0是b大
        return (self.cmpCard(a,b) and -1 or 1)
    def _sortCardList_cmp2(self,a,b):#比较两组牌大小。把拖拉机排序
        lena = len(a)
        lenb = len(b)
        num1 = self.orderInd[a[0]]
        num2 = self.orderInd[b[0]]
        if lena==lenb:
            if num1<=self.unlordMax and num2<=self.unlordMax:#都不是主牌
                if self.getDecor(a[0]) == self.getDecor(b[0]):  # 花色相同
                    return num1 >= num2 and -1 or 1
                return self.getDecor(a[0]) > self.getDecor(b[0]) and -1 or 1
            return num1>=num2 and -1 or 1
        return lena>lenb and -1 or 1
    def sortCardList2(self,actList):#对卡牌排序，找出几个拖拉机，几个对子,几个单牌，会重叠,并且要求是相同颜色
        self._ind=np.zeros((CARDS_CNT2+1))
        n=len(actList)
        cnt2 = 0
        for i in range(n):
            self._ind[actList[i]]+=1
            if self._ind[actList[i]]==2:
                cnt2+=1
        actList = sorted(actList, key=cmp_to_key(self._sortCardList_cmp))
        traList=[]
        doubleList = []
        prePos=-1
        for i in range(cnt2-1):#找拖拉机
            next_i=(i+1)*2
            s = self.orderInd[actList[i * 2]] - self.orderInd[actList[next_i]]
            if (s == 0 or s== 1):
                if prePos==-1:
                    prePos=i*2
            elif prePos!=-1:
                traList.append([actList[t] for t in range(prePos,i*2+2,2)])
                prePos=-1
            doubleList.append(actList[i*2])
        if cnt2!=0:
            if prePos != -1 :
                traList.append([actList[t] for t in range(prePos,cnt2*2,2)])
            doubleList.append(actList[(cnt2-1) * 2])
        traList = sorted(traList, key=cmp_to_key(self._sortCardList_cmp2))
        actList = sorted(actList, key=cmp_to_key(self._sortCardList_cmp1))
        return actList,doubleList,traList
    def sortCardList1(self,actList,doubleList,traList):#对卡牌排序，找出几个拖拉机，几个对子,会把不同类别区分开(去重)//,要提前调用sortCardList2
        cnt2=len(doubleList)
        ind=np.zeros(55,dtype=int)
        for tra in traList:
            for a in tra:
                ind[a]+=1
        for a in doubleList:
            ind[a] += 1
        doubleList1 = []
        actList1=[]
        for a in actList:
            if ind[a]==0:
                actList1.append(a)
        for a in doubleList:
            if ind[a]==1:
                doubleList1.append(a)
        return actList1,doubleList1,traList
    def _isLord(self,actList):
        for a in actList:
            if self.orderInd[a]<=self.unlordMax:
                return False
        return True
    def isLord(self,act:Action):
        if self._isLord(act.one) == False:
            return False
        for dou in act.double:
            if self._isLord(dou)==False:
                return False
        return True
    def getActKind(self,act:Action):#获得一个动作类别，如果什么都有或者为空返回INF
        kind=INF
        for a in act.one:
            k=getKind(a,self.lordDecor,self.lordNum)
            if kind!=INF and kind!=k:
                return INF
            kind=k
        for dou in act.double:
            for a in dou:
                k = getKind(a, self.lordDecor, self.lordNum)
                if kind != INF and kind != k:
                    return INF
                kind = k
        return kind
    def _useCmpCards(self,act1:Action,act2:Action):#必须二者是同一种类别!!!
        n=len(act1.double)
        for i in range(n):#先判断2是否为对子
            for j in range(0,len(act1.double[i]),2):
                if act2.double[i][j]!=act2.double[i][j+1]:
                    return True
        if n>0:#有对子或者拖拉机，就看对应牌的大小
            for i in range(n):  # 先判断act2是否为拖拉机
                tra1=act1.double[i]
                tra2=act2.double[i]
                for j in range(2, len(tra2), 2):
                    if abs(self.orderInd[tra2[j]]- self.orderInd[tra2[j-2]])>1:#是相邻的
                        return True
                if self.orderInd[tra1[0]] >= self.orderInd[tra2[0]]:#只有前面的牌比后面的牌大，就返回True
                    return True
            return False
        for i in range(len(act1.one)):  # 最后判断单牌
            if self.orderInd[act1.one[i]] != self.orderInd[act2.one[i]]:  # 单牌且不等
                return self.cmpCard(act1.one[i], act2.one[i])
        return True  # 完全想等，先出的大


    def useCmpCards(self,act1:Action,act2:Action):#比较两组牌大小，保证两组牌一样多，且actList1为先出，actList2为后出。返回1是actList1大，否则actList2大
        n=act1.len
        k1 = self.getActKind(act1)#判断什么类型
        k2 = self.getActKind(act2)
        if k1==self.lordDecor and k2==self.lordDecor:#如果都是主牌,先判断拖拉机，在判断单对子
            return self._useCmpCards(act1,act2)
        elif k1!=self.lordDecor and k2!=self.lordDecor:#如果都是非主牌,判断花色，花色相同比大小，否则先出的大。
            if k2!=k1:#act2是杂牌
               return 1
            return self._useCmpCards(act1,act2)
        elif k1==self.lordDecor:#先出的是主牌，后出的不是，先出的大
            return 1
        else:#先出的不是主牌，后出的是主牌,要看主牌能否完全管上先出的。这里先出的一定是同一花色。主牌要杀拖拉机，只需要相应数量对子。
            for i in range(len(act1.double)):  # 先判断2是否为对子或拖拉机
                for j in range(0, len(act1.double[i]), 2):
                    if act2.double[i][j] != act2.double[i][j + 1]:
                        return 1
            return 0

    # def judgeRoundWin(self):
    def getOrderID(self,a):#从0开始，非主牌是[0,11],主牌[0,15]
        k = self.orderInd[int(a)]
        if k > self.unlordMax:
            k -= self.unlordMax
        return int(k-1)

    def getMaxCards_cmp1(self,a):
        return a==2
    def getMaxCards_cmp2(self,a):
        return a>0
    def getMaxCards(self,p:Player):  # 返回已知的玩家手里最大的牌,来判断先手玩家是否可以甩牌,sortCardsList2是一名玩家分好类的手牌，且会相互包含
        li=[]
        sortCardsList2=p.toSortCardsList2(self)
        for kind in range(5):
            if kind==self.lordDecor:#主牌不能甩
                continue
            k1 = p.getSelfMaxCard(kind, self.getMaxCards_cmp1)#从大到小找到第一个没有出过2张牌的牌的顺序号
            k2 = p.getSelfMaxCard(kind, self.getMaxCards_cmp2)#从大到小找到第一个出过0张牌的牌的顺序号
            act=Action()
            for a in sortCardsList2[kind][0]:
                k=self.getOrderID(a)
                if k>=k1:#看比它大的有多少已经出过2张，如果都出过2张，说明它是最大的牌
                    act.addOne(a)
            for a in sortCardsList2[kind][1]:#看是不是最大的对子
                k = self.getOrderID(a)
                if k>=k2:#看有多少出了0张，如果都没有出了0张
                    act.addDou([a,a])
            maybeTra=[]
            seqCnt=0

            for i in range(p.orderCards_len[kind] - 1, -1,-1):#寻找所有可能的拖拉机
                if i == p.lordNumOrder:
                    c=0
                    for j in range(4):
                        if j != p.lordDecor:
                            c+=p.lordNumSee_cnt[j]==0
                    seqCnt+=c
                    if c<3 and seqCnt>0:
                        if seqCnt>1:
                            maybeTra.append((i,seqCnt))
                        # maxSeqCnt = max(maxSeqCnt, seqCnt)
                        seqCnt = 0
                elif p.orderCards_cnt[kind][i]==0:
                    seqCnt+=1
                elif seqCnt>0:
                    if seqCnt > 1:
                        maybeTra.append((i+seqCnt,seqCnt))
                    seqCnt = 0
            if seqCnt>1:
                maybeTra.append((-1+seqCnt,seqCnt))
            # if p.id == 0:
            #     print(maybeTra)
            for traList in sortCardsList2[kind][2]:#看自己的拖拉机
                n=len(traList)
                k = self.getOrderID(traList[0])
                for tra in maybeTra:
                    # if p.id == 0:
                    #     print(tra, n)
                    if tra[1]>=n and tra[0]>k:#可能的拖拉机的长度大于等于自己的拖拉机，且可能的拖拉机比我方的次序大。
                        break
                else:#正常结束循环，说明我方的拖拉机最大
                    act.addDou([traList[i//2] for i in range(len(traList)*2)])
            if act.isSeq():
                li.append(act)
        return li#返回一个5元列表，代表一定可以甩的牌、
    def updatesortCardList2(self):
        self.sortCardsList2=[]
        for i in range(4):
            li=self.players[i].toSortCardsList2(self)
            self.sortCardsList2.append(li)  # 会重叠
    def _judgeSeqUse(self,act:Action):#
        # 是否为甩牌,是否可以出
        self.updatesortCardList2()
        sortCardList4=self.sortCardsList2
        if act.isSeq():#是甩牌
            mina=INF
            card=0
            for a in act.one:#找出最小的牌
                if mina>self.orderInd[a]:
                    mina=self.orderInd[a]
                    card=a
            kind, num = getKindAndNum(card,self.lordDecor,self.lordNum)
            if card>0:
                for pid in range(4):
                    if pid != act.playerId:
                        li=sortCardList4[pid]
                        if len(li[kind][0])>0 and self.orderInd[li[kind][0][0]]>self.orderInd[card]:#寻找这个花色所有比card顺序大的牌：
                            return True,False

            for pid in range(4):
                if pid != act.playerId:#遍历每个人手牌的对子。
                    li = sortCardList4[pid]
                    for dou in act.double:
                        kind, num = getKindAndNum(dou[0], self.lordDecor, self.lordNum)
                        lendou=len(dou)#它是li里面拖拉机牌数的2倍，比如3344，则li里面表示为34
                        if lendou==2:
                            a=li[kind][1]
                            if len(a) > 0 and self.orderInd[a[0]] > self.orderInd[dou[0]]:  # 寻找这个花色所有比card顺序大的牌：
                                return True, False
                        else:
                            tractors = li[kind][2]
                            for tra in tractors:
                                if len(tra)*2>=lendou and self.orderInd[tra[0]] > self.orderInd[dou[0]]:
                                    return True, False
            return True, True
        return False,True

    def firstPolicy(self,firstPlayerId,firstPolicyFun):#第一个人出牌，policyFun是一个回调，代表如果有甩牌，甩牌的出牌策略
        p=self.players[firstPlayerId]
        allActList=self.getFirstAllAction(p)
        act_id=firstPolicyFun(self,p,Action([],[],playerId=p.id),allActList)
        act = allActList[act_id]
        if isinstance(act,Action) :#act是action代表要使用的动作
            # act.println()
            p.useAction(self,act)
            return act
        else:#act是list代表要甩牌的类
            kind=act[0]
            pHandCards=p.cards[kind]
            cardsList=[]
            act=Action([],[],playerId=p.id)
            for i in range(len(pHandCards)):
                allActList=[]
                if i>=2:
                    allActList.append([])
                for i in range(len(pHandCards)):
                    a=pHandCards[i]
                    allActList.append([a])
                act_id=firstPolicyFun(self,p,act,allActList)
                if len(allActList[act_id])==0:
                    break
                p.useCardsList(self, allActList[act_id])
                cardsList.append(allActList[act_id][0])
                act = cardsListToAction(self, p.id, cardsList)


            isSeq, canSeq = self._judgeSeqUse(act)
            if isSeq and canSeq == False:  # 如果不能甩
                # print("不能甩！！！")
                if self.players[act.playerId].dealerTag < 2:  # 是庄家甩牌失败
                    self.sumSc += 10
                else:
                    self.sumSc = max(0, self.sumSc - 10)
                p.addCardsList(self, cardsList)
                act= act.getMinCard(self)
                p.useAction(self, act)
            return act

    def getFirstAllAction(self,p:Player):#返回作为先出玩家的所有可能的动作(不包含甩牌),sortCardsList1是一名玩家分好类的手牌，且会相互包含
        ans=[]
        sortCardsList2= p.toSortCardsList2(self)  # 会相互包含
        # maxCards=self.getMaxCards(sortCardsList1,p)
        for i in range(5):
            for a in sortCardsList2[i][0]:
                ans.append(Action([a],playerId=p.id))
            for a in sortCardsList2[i][1]:
                ans.append(Action([],[[a,a]],playerId=p.id))
            for tractor in sortCardsList2[i][2]:#拖拉机
                ltr=len(tractor)
                for begin_i in range(ltr):
                    tractor_tmp = [tractor[begin_i],tractor[begin_i]]
                    for begin_j in range(begin_i+1,ltr):
                        tractor_tmp.append(tractor[begin_j])
                        tractor_tmp.append(tractor[begin_j])
                        ans.append(Action([],[tractor_tmp.copy()],playerId=p.id))
        for i in range(4):
            if i!=self.lordDecor and len(p.cards[i])>1:
                ans.append([i])
        return ans
    def getAllAct_dfs(self,doubleList,doubleList_i,ansDown,nowList,nowList_i,n):
        if nowList_i==n:
            ansDown.append(nowList.copy())
            return
        doubleList_len=len(doubleList)
        for i in range(doubleList_i,doubleList_len):
            if doubleList_len-i<n-nowList_i:
                return
            else:
                nowList.append(doubleList[i])
                nowList.append(doubleList[i])
                self.getAllAct_dfs(doubleList,i+1,ansDown,nowList,nowList_i+1,n)
                nowList.pop()
                nowList.pop()

    # def getAllAction(self, p: Player, firstAct: Action):  # 得到所有非第一家的动作

    def getAllAction(self, p: Player, firstAct:list):  # 得到所有非第一家的动作，sortCardsList是p玩家分好类的手牌，且会相互包含
        # 返回所有大过之前最大的玩家的牌和小于之前玩家的牌
        # firstAct只能是单张，对子，连对
        #小于玩家的牌有太多组合会被忽略
        toSortCardsList2 =p.toSortCardsList2(self)   # 会重叠
        n = len(firstAct)
        kind=getKind(firstAct[0],self.lordDecor,self.lordNum)
        n2=n//2
        ansUp = []
        ansDown = []
        isHave=False
        c0,c1,c2=len(toSortCardsList2[kind][0]),len(toSortCardsList2[kind][1]),len(toSortCardsList2[kind][2])
        if n == 1:  # 单张牌
            isHave = c0 > 0
            ansDown=self.getFollowAct_one(p,firstAct[0],kind)
            if kind == self.lordDecor or c0 > 0:  # 是主牌或副牌，但有这类副牌
                for i in range(c0):
                    a = toSortCardsList2[kind][0][i]
                    if self.orderInd[a] > self.orderInd[firstAct[0]]:
                        ansUp.append([a])
            else:  # 用主牌杀
                for i in range(len(p.cards[self.lordDecor])):
                    a = p.cards[self.lordDecor][i]
                    ansUp.append([a])
        elif n == 2:
            isHave = c1>0
            if kind == self.lordDecor or c1>0:  # 这类牌有对子
                for a in toSortCardsList2[kind][1]:
                    if self.orderInd[a] > self.orderInd[firstAct[0]]:
                        ansUp.append([a,a])
            elif len(p.cards[kind]) == 0:  # 用主牌杀
                for a in toSortCardsList2[self.lordDecor][1]:
                    ansUp.append([a,a])
            if c1>0:
                for a in toSortCardsList2[kind][1]:
                    if self.orderInd[a] <= self.orderInd[firstAct[0]]:
                        ansDown.append([a, a])
            else:
                ansDown.append([INF ,INF])  #比如先手出了66，而自己有7，则此时依然返回INFINF
        else:#拖拉机
            #较大的拖拉机和较小的拖拉机
            if kind == self.lordDecor or c2>0:  # 这类牌有拖拉机
                for tractor in toSortCardsList2[kind][2]:
                    for j in range(len(tractor)-n2+1):#比如最大的拖拉机是3344，而自己手里又55667788，则此时有3种出牌方式管上它
                        isHave = True
                        if self.orderInd[tractor[j]]>self.orderInd[firstAct[0]]:
                            ansUp.append([tractor[j+k//2] for k in range(n)])
                        else:
                            ansDown.append([tractor[j + k // 2] for k in range(n)])
            elif len(p.cards[kind]) == 0:  # 用主牌杀
                for tractor in toSortCardsList2[self.lordDecor][2]:
                    for j in range(len(tractor)-n2+1):
                        ansUp.append([tractor[j+k // 2] for k in range(n)])

            if not isHave:#如果没有同样长度的拖拉机,则从对子里出
                tempLi = []
                if len(toSortCardsList2[kind][1]) > n2:
                    self.getAllAct_dfs(toSortCardsList2[kind][1], 0, ansDown, tempLi, 0, n2)  # 从对子里选取所有组合
                else:
                    for a in toSortCardsList2[kind][1]:
                        tempLi.append(a)
                        tempLi.append(a)
                    tempLi_len = len(tempLi)
                    for i in range(tempLi_len, n):
                        tempLi.append(INF)
                        # 剩余牌优先从这个颜色里选取
                        #没有这个颜色再从其他任意牌选
                        #比如先手是'<♥A>', '<♥A>', '<♥K>', '<♥K>', '<♥Q>', '<♥Q>'，我有JJQQ9,此时会返回JJQQINFINF
                    ansDown.append(tempLi)

        return ansUp,ansDown,isHave

    def getFollowAct_one(self, p: Player, card_max, kind):  # 返回小于某张牌的全部牌
        ans=[]
        if len(p.cards[kind])>0:#大于0
            for i in range(len(p.cards[kind])):
                a=p.cards[kind][i]
                if self.orderInd[a]<=self.orderInd[card_max]:
                    ans.append([a])
        else:#
            for i in range(5):
                if i!=self.lordDecor:
                    for j in range(len(p.cards[i])):
                        ans.append([p.cards[i][j]])
        return ans

    def __otherPolicy(self, p:Player,firstAct:Action,usedAct,cards, otherPolicyFun):
        allActList_up,allActList_down,isHave = self.getAllAction(p, cards)
        allActList=allActList_down+allActList_up
        act_id = otherPolicyFun(self, p, usedAct, allActList)
        act_ans = allActList[act_id]
        firstKind=firstAct.getKind(self)
        doulasti=len(usedAct.double)-1
        p.useCardsList(self, act_ans)
        usedList=[]
        for i in range(len(act_ans)):
            if act_ans[i]==INF:
                if len(p.cards[firstKind])==0:#没有这个类别的牌就从其他牌里选
                    allActList_1 = p.otherKindCards(firstKind)
                else:#从这个类别里选
                    allActList_1=p.cards[firstKind].copy()
                act_id_1 = otherPolicyFun(self, p, usedAct, allActList_1)
                # dfsPrintActList(allActList_1)
                # print(act_id_1,act_ans)
                act_ans[i]=allActList_1[act_id_1]
                usedList.append(act_ans[i])
                p.useCardsList(self, [act_ans[i]])
                usedAct.setDou(doulasti, usedList.copy())  # 设置牌
        return act_ans
    def otherPolicy(self,act4,firstPlayerID,nowPlayerId,otherPolicyFun):
        # 第一个人出牌，otherPolicyFun是一个回调，代表如果跟牌太多，
        p = self.players[nowPlayerId]
        firstAct=act4[firstPlayerID]
        act_ans = Action([], [], playerId=p.id)
        for a in firstAct.one:
            li = self.__otherPolicy(p,firstAct,act_ans,[a],otherPolicyFun)
            act_ans.add(li)
        for dou in firstAct.double:
            act_ans.addDou([])
            li=self.__otherPolicy(p, firstAct, act_ans, dou, otherPolicyFun)
            act_ans.setDou(len(act_ans.double)-1, li)  # 设置牌
        return act_ans

    def step(self,actList4,first_playerId):#输入4个人的出牌组合,保证每个人出的牌数量一样多，返回赢得那个人和所得分数
        playerId=first_playerId
        actList4[playerId].sort(self)#
        for i in range(1,4):
            k=(first_playerId+i)%4
            actList4[k].sort(self)#
            if self.useCmpCards(actList4[playerId],actList4[k])==0:#actList4[k]大
                playerId=k
        self.round_i+=1
        #找找到最大的那个人
        sc=0
        n=actList4[first_playerId].len#所有人的牌数量都是n
        for i in range(4):
            sc+=actList4[i].getFen()
        if self.players[playerId].dealerTag>1:
            self.sumSc+=sc
        leftCardsCnt=0
        for i in range(4):
            leftCardsCnt+= self.players[i].len
        if leftCardsCnt==0:#游戏结束,结算底牌分数
            sc_under = rate=0
            # if self.players[playerId].dealerTag > 1:  # 不是庄家赢
            for a in self.underCards:  # 结算底牌分数
                num = getNum(a)  # 点数，[1,13]王是14
                sc_under += fenInd[num]  # 分数
            rate = 2
            if n > 1:  # 判断倍数
                doubleCnt = actList4[playerId].getDouleCnt() * 2
                if doubleCnt > 0:  # 每有一个对子，倍数+2
                    rate = 2 + doubleCnt
                else:  # 普通甩牌没有对子，倍数+1
                    rate = 2 + 1  # 普通甩牌为3倍
            if self.players[playerId].dealerTag>1:#不是庄家赢
                self.sumSc += sc_under*rate
            self.undeck+=self.underCards
            return playerId, sc,True,sc_under*rate
        return playerId,sc,False,0#返回赢得玩家id，本轮得分，是否结束游戏，结算信息
    def getGrade(self,sc):
        if sc<80:
            return (sc==0 and 0 or (sc//40+1))-3#判断庄家升几级
        else:
            return sc // 40-2#如果不足120仅仅换庄，不升级
    def setLord(self,kind,playerID=-1):
        self.lordDecor=kind
        if playerID!=-1:
            self.dealer=playerID
        for i in range(4):
            self.players[i].setLord(kind,self.lordNum)
        self.setOrder()
    def getLord(self):
        return self.lordNum+self.lordDecor*13

    def sortPlayerHand(self,player):
        for i in range(5):
            player.cards[i].sort(key=cmp_to_key(self._sortCardList_cmp1))

    def _getActListMaxCmp(self,a:Action,b:Action):
        if a.len==b.len:
            la,lb=a.getDouleCnt(),b.getDouleCnt()
            if la==lb and la==0:
                return self.orderInd[b.one[0]]-self.orderInd[a.one[0]]
            elif la==lb:
                for i in range(min(len(a.double),len(b.double))):
                    if len(a.double[i])!=len(b.double[i]):
                        return len(b.double[i])-len(a.double[i])
                else:
                    return self.orderInd[b.double[0][0]]-self.orderInd[a.double[0][0]]
            return lb-la
        return b.len-a.len
    def getActListMax(self,allActionList):#从动作列表里寻找最大的动作
        for act in allActionList:
            act.sort(self)
        allActionList.sort(key=cmp_to_key(self._getActListMaxCmp))
        return allActionList[0]


    def printAllInfo(self,nowpid=None, act=None):  # act代表4个人每个人出的牌,类型是Action
        if nowpid!=None:
            print("当前玩家:"+str(nowpid), end=",")
        print("双方等级", self.levelOfBoth,end=",")
        print("主牌:", decorName[self.lordDecor] + str(self.lordNum), "   庄家：", self.dealer)
        self.printAllCards()
        if act!=None and isinstance(act[0],Action):
            for i in range(4):
                act[i].println(i)
        print("当前闲家的分" + str(self.sumSc))
    def printUnderCards(self):  # act代表4个人每个人出的牌
        self.printCardsList(self.deck[-8:])
    def getPlayNowGrade(self,playerId):
        g=self.levelOfBoth[playerId%2]
        if g==1:
            g=14
        return g