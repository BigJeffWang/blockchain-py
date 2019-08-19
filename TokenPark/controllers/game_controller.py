# game相关
from controllers.base_controller import BaseController
from services.game_service import GameService
from tools.decorator_tools import FormatOutput


# 获取game实例信息
class GameInstanceController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['instance_id'])
        instance_id = request_data['instance_id']
        user_id = request_data.get('user_id', '')
        merge_id = request_data.get('merge_id', '')
        game_service = GameService()
        result = game_service.get_game_instance(instance_id, user_id, merge_id)

        return self.utctime_to_localtime(result)


# 非登录状态下获取game实例信息
class MergeGameInstanceController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['instance_id'])
        instance_id = request_data['instance_id']
        merge_id = request_data.get('merge_id', '')
        game_service = GameService()
        result = game_service.get_merge_game_instance(instance_id, merge_id)

        return self.utctime_to_localtime(result)


# 获取game实例信息 (非登录)
class GameInstanceNoneUserController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['instance_id'])
        instance_id = request_data['instance_id']
        game_service = GameService()
        result = game_service.get_game_instance_none_user(instance_id)

        return self.utctime_to_localtime(result)


# game实例列表
class GameInstanceListController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict()
        limit = request_data.get('limit', 10)
        offset = request_data.get('offset', 1)
        game_title = request_data.get('game_title', '')
        game_serial = request_data.get('game_serial', '')
        release_time_start = request_data.get('release_time_start', '')
        release_time_end = request_data.get('release_time_end', '')
        full_load_time_start = request_data.get('full_load_time_start', '')
        full_load_time_end = request_data.get('full_load_time_end', '')
        status = request_data.get('status', '')
        release_type = request_data.get('release_type', '')
        start_id = request_data.get("start_id", None)
        game_service = GameService()
        result = game_service.get_game_instance_list(limit, offset, game_title, game_serial,
                                                     release_time_start, release_time_end, full_load_time_start,
                                                     full_load_time_end, status, release_type, start_id)
        return self.utctime_to_localtime(result)


# game模板标题列表
class GameTemplateNameListController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        # request_data = self.get_argument_dict()
        game_service = GameService()
        result = game_service.get_game_template_name_list()

        return self.utctime_to_localtime(result)


# 用户参与列表
class GameParticipateInListController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict()
        limit = request_data.get('limit', 10)
        offset = request_data.get('offset', 1)
        game_instance_id = request_data.get('game_instance_id', '')
        start_id = request_data.get("start_id", None)
        game_service = GameService()
        result = game_service.get_participate_in_list(limit, offset, game_instance_id, start_id)

        return self.utctime_to_localtime(result)


# 后台管理用户参与列表
class ManageParticipateInController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict()
        limit = request_data.get('limit', 10)
        offset = request_data.get('offset', 1)
        game_title = request_data.get('game_title', '')
        game_serial = request_data.get('game_serial', '')
        part_in_time_start = request_data.get('part_in_time_start', '')
        part_in_time_end = request_data.get('part_in_time_end', '')
        channel = request_data.get('channel', '')
        pay_token = request_data.get('bet_token', '')
        user_name = request_data.get('user_name', '')
        start_id = request_data.get("start_id", None)
        instance_id = request_data.get("instance_id", '')
        game_service = GameService()
        result = game_service.manage_participate_in(limit, offset, game_title, game_serial, part_in_time_start,
                                                    part_in_time_end, channel, pay_token, user_name, start_id, instance_id)

        return self.utctime_to_localtime(result)


# game实例详情(包括模板详情、中奖详情)
class CurrentPeriodInfoController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['instance_id'])
        instance_id = request_data['instance_id']
        game_service = GameService()
        result = game_service.current_period_info(instance_id)

        return self.utctime_to_localtime(result)


# 获取手动发布game信息
class ManualReleaseInfoController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['template_id'])
        template_id = request_data['template_id']
        game_service = GameService()
        result = game_service.get_manual_release_info(template_id)

        return self.utctime_to_localtime(result)


# 手动发布game信息
class ManualReleaseController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['template_id', 'game_serial', 'need', 'game_describe'])
        template_id = request_data['template_id']
        game_serial = request_data['game_serial']
        need = request_data['need']
        game_describe = request_data['game_describe']
        game_service = GameService()
        result = game_service.manual_release(template_id, game_serial, need, game_describe)

        return self.utctime_to_localtime(result)


# 最新一期开奖信息
class NewWinningRecordController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict()
        instance_id = request_data.get('instance_id', '')
        timezone = -request_data.get("timezone")
        game_service = GameService()
        result = game_service.get_winning_record(timezone, instance_id)

        return self.utctime_to_localtime(result)


# 获取game实例信息和对应的区块链信息
class InstanceBlockchainInfoController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['instance_id'])
        instance_id = request_data['instance_id']
        timezone = -request_data.get("timezone")
        game_service = GameService()
        result = game_service.instance_blockchain_info(instance_id, timezone)

        return self.utctime_to_localtime(result)


# 英雄榜
class HeroListController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict()
        # limit = request_data.get('limit', 10)
        # offset = request_data.get('offset', 1)
        game_service = GameService()
        result = game_service.hero_list()

        return self.utctime_to_localtime(result)


# 获取实时币价
class GetCurrentPriceController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        game_service = GameService()
        result = game_service.get_current_price()

        return self.utctime_to_localtime(result)


# 本期合买列表
class MergeParticipateInListController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['instance_id'])
        limit = request_data.get('limit', 10)
        offset = request_data.get('offset', 1)
        instance_id = request_data['instance_id']
        start_id = request_data.get("start_id", None)
        game_service = GameService()
        result = game_service.merge_participate_in_list(limit, offset, instance_id, start_id)

        return self.utctime_to_localtime(result)


# 发起合买
class InitiateMergeController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id', 'instance_id', 'part_in_id'])
        user_id = request_data['user_id']
        instance_id = request_data['instance_id']
        part_in_id = request_data['part_in_id']
        game_service = GameService()
        result = game_service.initiate_merge(user_id, instance_id, part_in_id)

        return self.utctime_to_localtime(result)


# 合买获奖信息列表
class MergeInfoListController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['merge_id', 'instance_id'])
        limit = request_data.get('limit', 10)
        offset = request_data.get('offset', 1)
        merge_id = request_data['merge_id']
        instance_id = request_data['instance_id']
        game_service = GameService()
        result = game_service.merge_info_list(limit, offset, merge_id, instance_id)

        return self.utctime_to_localtime(result)


# 获取最新可投项目id
class LatestAvailableInstanceController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        game_service = GameService()
        result = game_service.latest_available_instance()

        return self.utctime_to_localtime(result)


# 本期合买参与列表
class MergeDetailListController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['instance_id', 'merge_id'])
        limit = request_data.get('limit', 10)
        offset = request_data.get('offset', 1)
        instance_id = request_data['instance_id']
        merge_id = request_data['merge_id']
        start_id = request_data.get("start_id", None)
        game_service = GameService()
        result = game_service.merge_detail_list(limit, offset, instance_id, merge_id, start_id)

        return self.utctime_to_localtime(result)
