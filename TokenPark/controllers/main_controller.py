from controllers.base_controller import BaseController
from services.main_service import MainService
from tools.decorator_tools import FormatOutput


class MainPageController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        # request_data = self.get_argument_dict()
        main_service = MainService()
        result = main_service.main_page()

        return self.utctime_to_localtime(result)


class GamePageController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict()
        limit = request_data.get('limit', 10)
        offset = request_data.get('offset', 1)
        status = request_data.get('status', '')
        start_id = request_data.get("start_id", None)
        main_service = MainService()
        result = main_service.game_instance_info_list(limit, offset, status, start_id)

        return self.utctime_to_localtime(result)


class IndianaRecordController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id'])
        limit = request_data.get('limit', 10)
        offset = request_data.get('offset', 1)
        start_id = request_data.get("start_id", None)
        user_id = request_data['user_id']
        main_service = MainService()
        result = main_service.indiana_record(limit, offset, user_id, start_id)

        return self.utctime_to_localtime(result)


class IndianaRecordNewController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id'])
        limit = request_data.get('limit', 10)
        offset = request_data.get('offset', 1)
        start_id = request_data.get("start_id", None)
        user_id = request_data['user_id']
        main_service = MainService()
        result = main_service.indiana_record_new(limit, offset, user_id, start_id)

        return self.utctime_to_localtime(result)


class IndianaNumberController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['participate_id'])
        participate_id = request_data['participate_id']
        main_service = MainService()
        result = main_service.indiana_number(participate_id)

        return self.utctime_to_localtime(result)


class IndianaNumberNewController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['participate_id'])
        participate_id = request_data['participate_id']
        main_service = MainService()
        result = main_service.indiana_number_new(participate_id)

        return self.utctime_to_localtime(result)


# 夺宝详情
class IndianaDetailController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['instance_id', 'participate_id'])
        instance_id = request_data['instance_id']
        participate_id = request_data['participate_id']
        main_service = MainService()
        result = main_service.indiana_detail(instance_id, participate_id)

        return self.utctime_to_localtime(result)


# app版本检查
class AppVersionCheckController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['version_code'])
        version_code = request_data['version_code']
        main_service = MainService()
        result = main_service.app_version_check(version_code)

        return self.utctime_to_localtime(result)
