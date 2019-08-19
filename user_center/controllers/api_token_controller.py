from controllers.base_controller import BaseController
from services.api_token_service import ApiTokenService
from tools.decorator_tools import FormateOutput, AESOutput
from common_settings import *
from tools.check_tools import check_bg_ip
from tools.data_formate_tools import *


class BgRefreshAccessTokenController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30205, return_type='return_error')
    def post(self):
        """
        刷新用户access_token
        :return:
        """
        # 1.0 校验平台
        result = check_bg_ip()
        if result is False:
            self.return_error(30000)

        api_type = _USER_TYPE_ADMIN
        # 2.0 获取参数
        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_id', 'refresh_token'], check_token=False, api_type=api_type,
            request_type=_REQUEST_TYPE_LOGIN, decode_by_inner=_DECODE_TYPE_INNER)
        user_id = argument_dict['user_id']
        refresh_token = argument_dict['refresh_token']

        # 3.0 刷新token
        r = ApiTokenService(aes_share_key=aes_share_key, aes_nonce=aes_nonce).\
            refresh_token(user_id, refresh_token, user_type=api_type)
        return r, aes_share_key, aes_nonce


class InvestRefreshAccessTokenController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30205, return_type='return_error')
    def post(self):
        """
        刷新用户access_token
        :return:
        """

        api_type = _USER_TYPE_INVEST
        # 2.0 获取参数
        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_id', 'refresh_token', 'source'], check_token=False, api_type=api_type,
            check_form_token=True, request_type=_REQUEST_TYPE_LOGIN)
        user_id = argument_dict['user_id']
        refresh_token = argument_dict['refresh_token']
        source = argument_dict['source']

        # 3.0 刷新token
        r = ApiTokenService(aes_share_key=aes_share_key, aes_nonce=aes_nonce).\
            refresh_token(user_id, refresh_token, user_type=api_type, source=source)
        return r, aes_share_key, aes_nonce


class BorrowRefreshAccessTokenController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30205, return_type='return_error')
    def post(self):
        """
        刷新用户access_token
        :return:
        """

        api_type = _USER_TYPE_BORROW
        # 2.0 获取参数
        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_id', 'refresh_token'], check_token=False, api_type=api_type,
            request_type=_REQUEST_TYPE_LOGIN)
        user_id = argument_dict['user_id']
        refresh_token = argument_dict['refresh_token']

        # 3.0 刷新token
        r = ApiTokenService(aes_share_key=aes_share_key, aes_nonce=aes_nonce).\
            refresh_token(user_id, refresh_token, user_type=api_type)
        return r, aes_share_key, aes_nonce



