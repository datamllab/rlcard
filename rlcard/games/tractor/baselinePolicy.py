import random
import numpy as np
from functools import cmp_to_key

import tractor_game
# from DNQ.mygame.TractorArtifice.cheater import mkDeck, cheator1
from tractor_gameUtil import fenInd,getNum
from tractor_game import Tractor
from tractor_player import Player
env=Tractor()
def _baselinecmp(a,b):#比较两组牌大小。返回1是a大，返回0是b大
    return a[1]>b[1] and 1 or -1
def baselineColdeck(env:Tractor,p: Player,undercard_i):#贪心的换牌算法,cards有8张
    li = []
    for i in range(4):
        if i!=p.lordDecor and len(p.cards[i])>0:
            li.append((i,len(p.cards[i])))
    li = sorted(li, key=cmp_to_key(_baselinecmp))
    mincard=0
    minnum=100
    for _ in li:#无脑扣每个类别里最小的牌
        kind,cardslen=_[0],_[1]
        for card in reversed(p.cards[kind]):
            if minnum>env.orderInd[card] and fenInd[getNum(card)]==0:
                mincard,minnum=card,env.orderInd[card]
                break
    if mincard==0:#只有主牌，则从主牌里扣
        return p.cards[p.lordDecor][-1]
    return mincard

def bidFun_random(env,p,round,allActList):#回调函数
    n=len(allActList)
    return random.randint(0,n-1)
def firstPolicyFun_random(env,p,usedAct,allActList):#回调函数
    n = len(allActList)
    act_id = random.randint(0, n - 1)
    # dfsPrintActList(allActList )
    # dfsPrintActList(allActList[act_id])
    # env.printAllInfo(p.id)
    # print("")
    return act_id
def otherPolicyFun_random(env, p, usedAct, allActList):#回调函数
    n = len(allActList)
    act_id=random.randint(0, n - 1)
    # dfsPrintActList(allActList )
    # dfsPrintActList(allActList[act_id])
    # env.printAllInfo(p.id)
    # print("")
    return act_id

# def baselineAct(p,knowCards,cardsCnt,knowCards_seq,maxi,kind):#player_cards代表自己玩家的手牌，knowCards是已知前置位的牌,knowCards_seq代表第几个出
#     #cardsCnt代表knowCards每组牌的数量
#     #maxi是最大的玩家的位置，kind代表出的花色，级牌算主牌的花色
#     #player_cards通过排序被编码成了4个颜色，每个颜色又分为3组分别代表；oneList,doubleList,traList
#     #
#     cardsMax=knowCards[maxi]
#     player_cards=p.toSortCardsList1(env)
#     if knowCards_seq==0:#先出
#         #算跑了多少分，如果外置位分数大于50，则无脑出大的。外置位分数计算方式：200-自己的分数-底牌的分数(如果可见)-已经出去的别人的分数
#         #如果外置位分数不大于50，随机尽量出小的，可以出分
#         #
#         pass
#     elif knowCards_seq==1:#第二个出
#         #无脑大过0号，否则随机跟小牌且尽量不跟分
#         if len(cardsMax[2])>0:#敌方又拖拉机
#             if len(player_cards[kind][2])==0:#我方没拖拉机
#                 if len(player_cards[kind][1])==0:#我方没对子
#                     if len(player_cards[kind][0])>=cardsCnt:#这一类花色有牌可出
#                         cards=baselineAct_followSmall1()#跟小牌
#                         return
#
#             # else:#个数大于它且比他多
#         for a in cardsMax[2]:  # 看看有没有拖拉机
#             pass
#         pass
#     elif knowCards_seq == 2:#第三个
#         #如果1号大，就无脑大过1号
#         #如果0号大，且0号是王或级牌或大于1张的甩牌拖拉机对子，就跟分，没有分跟小牌
#         #如果0号大，且0号较小，无脑大过他
#
#         pass
#     elif knowCards_seq == 3:#最后出牌，策略是：
#         #如果我方大:就无脑跟分,能用分杀就用分杀,没有分就随机跟小牌;
#         #如果敌方大:且没有分:能用分杀就用分杀，否则就随机跟小牌且尽量不跟分；
#         #如果敌方大且有分:就尽量大过前面的，大不过就随机跟小牌且尽量不跟分
#         pass
