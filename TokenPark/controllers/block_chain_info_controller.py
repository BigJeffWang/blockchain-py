"""
-------------------------------------------------
   File Name：     block_chain_info_controller
   Description:
   Author:        Zyt
   Date：          2018/11/21
-------------------------------------------------
"""

from controllers.base_controller import BaseController
from services.block_chain_info_service import BlockChainInfoService
from tools.decorator_tools import FormatOutput
from utils.log import raise_logger


class BlockChainInfoController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    @FormatOutput()
    def post():
        info = BlockChainInfoService().get_block_info()
        return info


class BlockChainInfoDetailController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(
            must_keys=['info_type', 'instance_id']
        )
        info_type = request_data.get("info_type")
        instance_id = request_data.get("instance_id")
        user_id = request_data.get("user_id", "")
        participate_id = request_data.get("participate_id", "")
        timezone = -request_data.get("timezone")
        info_type = str(info_type)
        try:
            info = BlockChainInfoService().get_info_detail(
                info_type, instance_id, user_id, participate_id, timezone
            )
            return info
        except ValueError:
            self.return_error(20003)
        except Exception as error:
            raise_logger(error, 'rs', 'error')
            self.return_error(20002)


class UserBlockChainInfoDetailController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(
            must_keys=['info_type', 'user_id']
        )
        info_type = request_data.get("info_type")
        instance_id = request_data.get("instance_id", "")
        user_id = request_data.get("user_id")
        participate_id = request_data.get("participate_id", "")
        timezone = -request_data.get("timezone")
        info_type = str(info_type)
        try:
            info = BlockChainInfoService().get_info_detail(
                info_type, instance_id, user_id, participate_id, timezone
            )
            return info
        except ValueError:
            self.return_error(20003)
        except Exception as error:
            raise_logger(error, 'rs', 'error')
            self.return_error(20002)


class UserBlockInfoController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(
            must_keys=['user_id']
        )
        user_id = request_data['user_id']
        page_num = request_data.get("offset", 1)
        page_limit = request_data.get("limit", 5)
        start_id = request_data.get("start_id", None)
        game_serial = request_data.get("game_serial", None)
        timezone = -request_data.get("timezone")
        instance_id = request_data.get('instance_id', None)

        result = BlockChainInfoService.user_block_recode(
            user_id, game_serial, page_num, page_limit, start_id, timezone,
            instance_id)
        return result


class NewestBlockInfoController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict()
        page_num = request_data.get("offset", 1)
        page_limit = request_data.get("limit", 5)
        start_id = request_data.get("start_id", None)
        game_serial = request_data.get("game_serial", None)
        record_type = request_data.get("record_type", None)
        timezone = -request_data.get("timezone")

        if record_type:
            try:
                record_type = int(record_type)
            except TypeError:
                self.return_error(10003)

        result = BlockChainInfoService.newest_online_record(
            game_serial, page_num, page_limit, start_id, record_type, timezone)
        return result
