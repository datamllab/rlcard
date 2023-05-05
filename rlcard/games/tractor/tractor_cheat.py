import numpy as np

from DNQ.mygame.TractorArtifice.game_env.tractor_gameUtil import getKind, INF, printCard, CARDS_CNT, CARDS_CNT2, \
    NameTodecorId, decorName, stringToCardId, UNDERCARD_CNT


def __mkdeck_push(deck1,i,yu,pid,without,setDecor, setNum):
    if deck1[i] == 0:
        j = 0
        while (j < len(yu)):
            if without[pid][getKind(yu[j], setDecor, setNum)] == 0:
                break
            j += 1
        if j == len(yu):
            j -= 1
            print("有冲突，放置了b:", end=" ")
            printCard(yu[j])
        deck1[i] = yu[j]
        yu.pop(j)
    elif deck1[i] == INF:
        deck1[i] = yu[0]
        yu.pop(0)
numind={"A":1,"1":1,"2":1,"3":1,"4":1,"5":1,"6":1,"7":1,"8":1,"9":1,"10":1,"11":1,"12":1,"13":1,"J":1,"Q":1,"K":1}
def mkDeck(fun):#作弊洗牌，测试用
    deck1 = np.zeros((CARDS_CNT), dtype='int')
    ind=np.zeros((CARDS_CNT2+1), dtype='int')
    yu=[]
    without=[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]#without[i][j]==1代表玩家i不能有颜色j的牌
    cardDir,setDecor,setNum,setDealer=fun()
    setDecor=NameTodecorId[setDecor]
    for i in range(4):#设置每个玩家的手牌
        dir=cardDir[i]
        deck1_i=0
        for j in range(4):
            strDec=decorName[j]
            if strDec in dir:
                for k in range(len(dir[strDec])):
                    if dir[strDec][k]!="大王" and dir[strDec][k]!="小王" and (dir[strDec][k] in numind ):
                        dir[strDec][k]=strDec+dir[strDec][k]
                    a=stringToCardId[dir[strDec][k]]
                    deck1[deck1_i*4+i] = a
                    if a!=INF:
                        ind[a]+=1
                        if ind[a]>2:
                            print("错误")
                            return None
                    deck1_i+=1
                without[i][j]=1
    for i in range(len(cardDir[4])):#cardDir[4]代表牌堆的底牌
        a = stringToCardId[cardDir[4][i]]
        deck1[CARDS_CNT-i-1]=a
        if a != INF:
            ind[a] += 1
            if ind[a] > 2:
                print("错误")
                return None

    for i in range(1,CARDS_CNT2+1):
        if ind[i]==1:
            yu.append(i)
        elif ind[i]==0:
            yu.append(i)
            yu.append(i)
    print(without)
    for i in range(CARDS_CNT-UNDERCARD_CNT,CARDS_CNT):
        __mkdeck_push(deck1, i, yu, setDealer, without, setDecor, setNum)
    # print(deck1)
    for k in range(4):
        for i in range(k,CARDS_CNT-UNDERCARD_CNT,4):
            __mkdeck_push(deck1,i,yu,k,without,setDecor, setNum)
        # print(deck1)
    # print(deck1)
    # ind = np.zeros((CARDS_CNT2 + 1), dtype='int')
    # for a in deck1:
    #     ind[a]+=1
    # print(ind)
    return deck1,setDecor,setNum,setDealer

def cheator1():##作弊器
    setDecor="♠"
    setNum=2
    setDealer=0
    dir=[{},{},{},{},[]]
    dir[0]["♠"]=["A","A"]
    dir[0]["♣"] = ["7","7","6","6","5","5"]
    # dir[0]["♦"] = []
    dir[0]["♥"] = ["7","7","6","6","5","5"]

    # dir[1]["♠"] = ["A", "A"]
    dir[1]["♣"] = ["8", "8", "10", "A", "A"]
    # dir[1]["♦"] = ["8", "8", "10", "A", "A"]
    dir[1]["♥"] = ["K", "K", "Q", "Q", "8", "8"]

    dir[2]["♠"] = ["Q", "Q","3", "3"]
    # dir[2]["♣"] = ["7", "7", "6", "6", "5", "5"]
    # dir[2]["♦"] = []
    dir[2]["♥"] = ["A", "A"]

    # dir[3]["♠"] = ["9", "9", "J", "J"]
    # dir[3]["♣"] = []
    # dir[3]["♦"] = []
    # dir[3]["♥"] = []


    return dir,setDecor,setNum,setDealer