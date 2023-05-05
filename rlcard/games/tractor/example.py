
#使用该游戏环境的样例
import random

from DNQ.mygame.TractorArtifice.game_env.tractor_cheat import mkDeck, cheator1
from baselinePolicy import baselineColdeck
from tractor_action import dfsPrintActList
from tractor_game import Tractor
def bidFun(env,p,round,allActList):#回调函数
    n=len(allActList)
    return random.randint(0,n-1)
def firstPolicyFun(env,p,usedAct,allActList):#回调函数
    n = len(allActList)
    act_id = random.randint(0, n - 1)
    # dfsPrintActList(allActList )
    # dfsPrintActList(allActList[act_id])
    # env.printAllInfo(p.id)
    # print("")
    return act_id
def otherPolicyFun(env, p, usedAct, allActList):#回调函数
    n = len(allActList)
    act_id=random.randint(0, n - 1)
    # dfsPrintActList(allActList )
    # dfsPrintActList(allActList[act_id])
    # env.printAllInfo(p.id)
    # print("")
    return act_id
def playAGame(env):#4个人双方随机游戏
    # deck1=[39, 39, 23, 12, 26, 5, 53, 1, 38, 30, 46, 54, 48, 40, 36, 6, 28, 46, 26, 18, 7, 16, 2, 27, 5, 22, 20, 47, 41, 41, 34, 8, 3, 31, 30, 13, 16, 23, 15, 48, 13, 51, 4, 37, 44, 33, 25, 52, 34, 9, 37, 21, 3, 17, 50, 29, 24, 51, 49, 38, 35, 43, 24, 6, 18, 32, 22, 29, 7, 20, 11, 19, 15, 36, 14, 42, 27, 45, 14, 12, 50, 45, 52, 31, 11, 42, 40, 47, 33, 54, 32, 8, 28, 21, 10, 49, 9, 25, 53, 44, 1, 4, 17, 19, 10, 2, 35, 43]
    # deck1, setDecor, setNum, setDealer=mkDeck(cheator1)
    # env.dealCards(deck1,bidFun,(setDecor, setNum , setDealer))
    env.dealCards(None, bidFun)
    # env.printAllInfo()
    env.setUnderCards(baselineColdeck)#换底牌，baselineColdeck是基于贪心的换底牌策略：无脑扣小排
    env.printAllInfo()
    dfsPrintActList(env.players[env.dealer].cards[env.lordDecor])
    firstPlayerId=env.dealer
    isTer=False
    epoch=0
    while(not isTer):#开始出牌
        # env.printAllCards()
        # print("轮次：",epoch,"  先出牌玩家：",firstPlayerId)
        act4 = [None,None,None,None]
        # print("先出玩家：", firstPlayerId)
        act4[firstPlayerId] = env.firstPolicy(firstPlayerId,firstPolicyFun)#获取动作
        # firstKind=env.getActKind(act4[firstPlayerId])

        # print(env.players[firstPlayerId].cards_decorList)
        # env.dfsPrintActList(sortCardList2[firstPlayerId])
        # env.dfsPrintActList(allAct[firstPlayerId],printCmp)
        # env.dfsPrintActList(act[firstPlayerId] )
        # print(firstKind)
        # act[firstPlayerId].println()
        for i in range(1,4):
            nextID=(firstPlayerId+i)%4
            act4[nextID]= env.otherPolicy(act4,firstPlayerId,nextID,otherPolicyFun)

        firstPlayerId,sc,isTer,endSc=env.step(act4,firstPlayerId)#评价谁赢，返回赢者id,本轮分数(双方都会得分)，isTer是游戏有木有结束
        # reset
        # env.printAllInfo(firstPlayerId,act4)
        if isTer :
            # env.printUnderCards()
            sc=env.sumSc
            winPlayer,playerId,grade=env.calcGameScore()#重置游戏，playerId==-1代表继续,否则代表先达到A的玩家。
            print(sc,winPlayer)
            isTer=playerId!=-1
            return isTer,winPlayer,grade
        epoch+=1
    return -1,-1

def train_game(trainMaxCnt):
    env=Tractor()
    for _ in range(trainMaxCnt):
        env.reset_game()
        while (True):#有先超过A的玩家就游戏结束
            isTer,winPlayer,grade=playAGame(env)
            # print(env.levelOfBoth)
            if isTer:
                break

train_game(1)