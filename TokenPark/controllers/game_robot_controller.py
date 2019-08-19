from controllers.base_controller import BaseController
from services.game_bet_in_service import GameBetInServie
from services.game_robot_service import GameRobotServie

from tools.decorator_tools import FormatOutput


# 创建机器人
class GameCreatRobotController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        result = GameRobotServie().creat_robot(
            self.get_argument_dict(must_keys=['number', 'user_id']))
        return result


# 选择指定数量机器人机器人
class GameSelectRobotController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        result = GameRobotServie().select_robot(
            self.get_argument_dict(must_keys=['game_serial',
                                              'robot_number',
                                              ]))
        return result


# 添加 投放机器人
class GameAddRobotCongifController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        result = GameRobotServie().add_robot_config(
            self.get_argument_dict(must_keys=['game_serial',
                                              'robot_number',
                                              'robots',
                                              'created_user_id'
                                              ]))
        return result


# 添加 自动投放机器人
class GameAddAutoRobotCongifController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        result = GameRobotServie().add_auto_robot_config(
            self.get_argument_dict(must_keys=['game_serial',
                                              'robot_numbers',
                                              'bet_numbers',
                                              'support_token',
                                              'start_time',
                                              'end_time',
                                              'bet_min',
                                              'bet_max',
                                              'created_user_id'
                                              ]))
        return result


# 重置机器人状态
class GameResetRobotCongifController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        result = GameRobotServie().reset_robot_config(
            self.get_argument_dict(must_keys=['robots']))
        return result


# 查询 游戏投放机器人配置
class GameSearchGameRobotCongifController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        result = GameRobotServie().search_game_robot_config(self.get_argument_dict())
        return self.utctime_to_localtime(result)


# 查询 投放机器人配置
class GameSearchRobotCongifController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        result = GameRobotServie().search_robot_config(self.get_argument_dict(must_keys=['id']))
        return self.utctime_to_localtime(result)


# 停止 游戏投放机器人配置
class GameCancelRobotCongifController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        result = GameRobotServie().cancel_robot_config(self.get_argument_dict(must_keys=['id']))
        return result


# 机器人投注
class GameRobotBetInController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        result = GameBetInServie().robot_bet_in(
            self.get_argument_dict(
                must_keys=['game_instance_id',
                           'user_id',
                           'conin_id',
                           'bet_amount']))
        return result
