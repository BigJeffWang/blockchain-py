from controllers.base_controller import BaseController
from services.game_bet_in_service import GameBetInServie
from services.game_model_service import GameModelServie, GamePublishLotteryServie
from tools.decorator_tools import FormatOutput
from utils.exchange_rate_util import get_exchange_rate


# 添加Game模版
class GameAddModelController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict()
        service = GameModelServie()

        result = service.add_model(request_data)
        return result


# 查询Game模版
class GameSearchModelController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        result = GameModelServie().search_model(self.get_argument_dict())
        return self.utctime_to_localtime(result)


# 编辑Game模版
class GameModifyModelController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        result = GameModelServie().modify_model(self.get_argument_dict())
        return result


# 删除Game模版
class GameDeleteModelController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        result = GameModelServie().delete_model(self.get_argument_dict())
        return result


# 更改Game启动停用状态
class GameModifyModelStatusController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        result = GameModelServie().modify_model_status(self.get_argument_dict())
        return result


# 用户操作接口=======================================================================================================================

# 用户下注
class GameBetInController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        result = GameBetInServie().bet_in(
            self.get_argument_dict(
                must_keys=['game_instance_id',
                           'user_id',
                           'user_channel_id',
                           # 'transaction_password',
                           'conin_id',
                           'bet_amount']))
        return result


# 外部调用接口=======================================================================================================================

# 公布开奖
class GamePublishTheLotteryController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        dic = self.get_argument_dict(must_keys=['id'])
        result = GamePublishLotteryServie().checkGameSoldOut(dic['id'])
        return result


# 服务接口=======================================================================================================================

# 币价格汇率
class GameExchangeRateController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['conin_id'])
        return get_exchange_rate(request_data['conin_id'])
