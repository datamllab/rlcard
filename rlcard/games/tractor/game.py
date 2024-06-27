import random

from tractor_game import Tractor

class TractorGame(Tractor):
    def __init__(self):
        super().__init__()  # 调用父类的初始化方法
        self.allow_step_back = False
        self.isBeginGame=False#是否是游戏开始阶段
    # 以下是rlcard的通用方法：
    def init_game(self):
        playerId=0
        if self.dealer!=-1:#不是-1说明是非初始阶段
            winPlayer,playerId,grade=self.calcGameScore()
        if playerId!=-1:
            self.reset_game()
            return [], self.currentPlayer
        else:
            return [], (self.dealer+1)%4

    def get_num_players(self):
        return 4

    def get_num_actions(self):
        return 25

    def configure(self, game_config):
        """
        Specify some game specific parameters, such as number of players, initial chips, and dealer id.
        If dealer_id is None, he will be randomly chosen
        """
        self.num_players = game_config['game_num_players']
        # must have num_players length
        self.init_chips = [game_config['chips_for_each']] * game_config["game_num_players"]
        self.dealer_id = game_config['dealer_id']
    def step(self,act):#step
        next_state=0
        player_id=0
        if self.game_stage=="bid":
            player_id=0
            env.dealCards(None, bidFun)
            '''
            把回调拆开
            '''

        elif self.game_stage=="ambush":

        elif self.game_stage == "play":


        return next_state, player_id

    def step_back(self):
        pass
    def is_over(self):
        return self.isTer
    def get_player_id(self):
        #返回当前出牌的玩家id
        return self.currentPlayer

def bidFun(env,p,round,allActList):#回调函数
    n=len(allActList)
    return random.randint(0,n-1)
env=TractorGame()
env.reset_game()
env.dealCards(None, bidFun)
print(env.get_player_id())
