# game相关
from controllers.base_controller import BaseController
from services.instant_game_model_service import InstantGameModelService
from services.instant_game_service import InstantGameService
from tools.decorator_tools import FormatOutput


# 添加Game模版
class InstantGameAddModelController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict()
        service = InstantGameModelService()

        result = service.add_model(request_data)
        return result


# 查询Game模版
class InstantGameSearchModelController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        result = InstantGameModelService().search_model(self.get_argument_dict())
        return self.utctime_to_localtime(result)


# 编辑Game模版
class InstantGameModifyModelController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        result = InstantGameModelService().modify_model(self.get_argument_dict())
        return result


# 删除Game模版
class InstantGameDeleteModelController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        result = InstantGameModelService().delete_model(self.get_argument_dict())
        return result


# 更改Game启动停用状态
class InstantGameModifyModelStatusController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        result = InstantGameModelService().modify_model_status(self.get_argument_dict())
        return result


# 即时开下注
class InstantGameBetController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        result = InstantGameService().bet_in(
            self.get_argument_dict(
                must_keys=['game_instance_id', 'user_id', 'user_channel_id',
                           'coin_id', 'bet_amount', 'bet_start', 'bet_end']))
        return result


# 获取game实例信息 (非登录)
class InstantGameNoneUserController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict()
        # instance_id = request_data['instance_id']
        game_service = InstantGameService()
        result = game_service.get_game_instance_none_user()

        return self.utctime_to_localtime(result)


# 获取game实例信息
class InstantGameController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id'])
        user_id = request_data['user_id']
        game_service = InstantGameService()
        result = game_service.get_game_instance(user_id)

        return self.utctime_to_localtime(result)


# 获取即时开参与信息
class GetInstantResultController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['part_in_id'])
        part_in_id = request_data['part_in_id']
        game_service = InstantGameService()
        result = game_service.get_instant_result(part_in_id)

        return self.utctime_to_localtime(result)


class InstantGameListController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict()
        limit = request_data.get('limit', 10)
        offset = request_data.get('offset', 1)
        game_serial = request_data.get('game_serial', '')
        release_time_start = request_data.get('release_time_start', '')
        release_time_end = request_data.get('release_time_end', '')
        full_load_time_start = request_data.get('full_load_time_start', '')
        full_load_time_end = request_data.get('full_load_time_end', '')
        lottery_time_start = request_data.get('lottery_time_start', '')
        lottery_time_end = request_data.get('lottery_time_end', '')
        start_id = request_data.get("start_id", None)
        game_service = InstantGameModelService()
        result = game_service.instant_game_list(limit, offset, game_serial, release_time_start, release_time_end,
                                                full_load_time_start, full_load_time_end,
                                                lottery_time_start, lottery_time_end,
                                                start_id)
        return self.utctime_to_localtime(result)


class GetInstantPartInListController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict()
        limit = request_data.get('limit', 10)
        offset = request_data.get('offset', 1)
        start_id = request_data.get("start_id", None)
        game_serial = request_data.get('game_serial', '')
        bet_time_start = request_data.get('bet_time_start', '')
        bet_time_end = request_data.get('bet_time_end', '')
        result = request_data.get('result', '')
        user_name = request_data.get('user_name', '')
        game_service = InstantGameService()
        result = game_service.get_instant_part_in_list(limit, offset, game_serial, bet_time_start,
                                                       bet_time_end, result, user_name, start_id)

        return self.utctime_to_localtime(result)
