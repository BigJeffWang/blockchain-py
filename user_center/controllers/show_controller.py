from controllers.base_controller import BaseController
from config import get_conf
from common_settings import *


class ShowController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def post(self, path):
        env = get_conf('env')
        if env != 'dev':
            return 'Hello'
        result = path

        # api_type = _USER_TYPE_ADMIN
        #
        # argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
        #     must_keys=['user_id', 'refresh_token'], check_token=False, api_type=api_type,
        #     request_type=_REQUEST_TYPE_LOGIN, decode_by_inner=_DECODE_TYPE_INNER)




        return result

    def get(self):
        env = get_conf('env')
        if env != 'dev':
            return 'Hello'
        result = 'yyy'
        return result


