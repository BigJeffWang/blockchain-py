from controllers.base_controller import BaseController
from tools.decorator_tools import FormateOutput, AESOutput
from common_settings import *
from tools.check_tools import check_bg_ip
from flask import request
from tools.transfer_tools import transfer_to_platform
from log import raise_logger
from services.user_base_service import UserBaseService
from config import get_transfer_to_platform_config
from tools.check_tools import check_transfer_platform_ip
import json


class UsersTransferToPlatformController(BaseController):
    # 客户端与平台交互的接口
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 用户类型、登陆状态、platform配置文件key、采用何种加密key、校验token，返回值加密
        self.user_type = _USER_TYPE_INVEST
        self.request_type = _REQUEST_TYPE_LOGIN
        self.invariable_key = True
        self.check_token = True
        self.return_aes = True

        # 实效性校验、加密、补充进来userid
        self.verify_timeliness = True
        self.encrypt = True
        self.check_user_id = True
        self.check_form_token = False
        self.must_keys = ['user_id']

    @AESOutput(cover_body=False)
    @FormateOutput(default_value=10001, return_type='return_error')
    def post(self, path):
        all_path_list = request.path.split("/")[1:]
        path_list = path.split("/")

        # 1.0 区别前后台用户
        if all_path_list[0] == 'bg':
            if len(path_list) < 2:
                self.return_error(10043)
            self.user_type = _USER_TYPE_ADMIN
            # 后台用户需要校验ip
            result = check_bg_ip()
            if result is False:
                self.return_error(30000)
        elif all_path_list[0] == 'users':
            pass
        else:
            self.return_error(10004)

        # 2.0 获取参数
        argument_dict, share_key, nonce = self.get_argument_dict(
            must_keys=self.must_keys, is_transfer=True,
            api_type=self.user_type, request_type=self.request_type, invariable_key=self.invariable_key,
            check_token=self.check_token, check_user_id=self.check_user_id, verify_timeliness=self.verify_timeliness,
            encrypt=self.encrypt, check_form_token=self.check_form_token
        )
        raise_logger('UsersTransferToPlatformController' + json.dumps(argument_dict))
        # 3.0 后台用户校验权限
        user_service = UserBaseService(aes_share_key=share_key, aes_nonce=nonce)
        if self.user_type == _USER_TYPE_ADMIN:
            user_id = argument_dict['user_id']
            module_url = path_list[0]
            transfer_check_result = user_service.check_admin_user_module_rights_by_user_id(user_id, module_url)
            if not transfer_check_result:
                self.return_error(30232)
        transfer_url = get_transfer_to_platform_config()['default_ip'] + request.path
        response_dict = transfer_to_platform(transfer_url, data=argument_dict)
        if self.return_aes:
            return response_dict, share_key, nonce
        else:
            return response_dict

    def log_transfer_msg(self, argument_dict):
        raise_logger(str(self.__class__.__name__) + str(argument_dict))


class PlatformCheckFormTokenController(BaseController):
    # 客户端与平台交互的接口
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormateOutput(default_value=10001, return_type='return_error')
    def post(self, token):
        result = check_transfer_platform_ip()
        if not result:
            return False
        return self.check_form_token(token)


class CommonTransferToPlatformController(BaseController):
    # 非登陆状态客户端与平台交互的接口
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput(cover_body=False)
    @FormateOutput(default_value=10001, return_type='return_error')
    def get(self, path):
        argument_dict = self.get_request_content(set_default=False)
        raise_logger('CommonTransferToPlatformController' + json.dumps(argument_dict))
        transfer_url = get_transfer_to_platform_config()['default_ip'] + request.path
        response_dict = transfer_to_platform(transfer_url, data=argument_dict)
        return response_dict

    def log_transfer_msg(self, argument_dict):
        raise_logger(str(self.__class__.__name__) + str(argument_dict))


class BgUsersTransferToPlatformController(BaseController):
    # 客户端与平台交互的接口
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 用户类型、登陆状态、platform配置文件key、采用何种加密key、校验token，返回值加密
        self.user_type = _USER_TYPE_INVEST
        self.request_type = _REQUEST_TYPE_LOGIN
        self.invariable_key = False
        self.check_token = True
        self.return_aes = False

        # 实效性校验、加密、补充进来userid
        self.verify_timeliness = False
        self.encrypt = False
        self.check_user_id = True
        self.check_form_token = False
        self.must_keys = ['user_id']

    @AESOutput(cover_body=False)
    @FormateOutput(default_value=10001, return_type='return_error')
    def post(self, path):
        all_path_list = request.path.split("/")[1:]
        path_list = path.split("/")

        # 1.0 区别前后台用户
        if all_path_list[0] == 'bg':
            if len(path_list) < 2:
                self.return_error(10043)
            self.user_type = _USER_TYPE_ADMIN
            # 后台用户需要校验ip
            result = check_bg_ip()
            if result is False:
                self.return_error(30000)
        else:
            self.return_error(10004)

        # 2.0 获取参数
        argument_dict, share_key, nonce = self.get_argument_dict(
            must_keys=self.must_keys, is_transfer=True,
            api_type=self.user_type, request_type=self.request_type, invariable_key=self.invariable_key,
            check_token=self.check_token, check_user_id=self.check_user_id, verify_timeliness=self.verify_timeliness,
            encrypt=self.encrypt, check_form_token=self.check_form_token
        )
        raise_logger('UsersTransferToPlatformController' + json.dumps(argument_dict))
        # 3.0 后台用户校验权限
        user_service = UserBaseService(aes_share_key=share_key, aes_nonce=nonce)
        if self.user_type == _USER_TYPE_ADMIN:
            user_id = argument_dict['user_id']
            module_url = path_list[0]
            transfer_check_result = user_service.check_admin_user_module_rights_by_user_id(user_id, module_url)
            if not transfer_check_result:
                self.return_error(30232)
        transfer_url = get_transfer_to_platform_config()['default_ip'] + request.path
        response_dict = transfer_to_platform(transfer_url, data=argument_dict)
        if self.return_aes:
            return response_dict, share_key, nonce
        else:
            return response_dict

    def log_transfer_msg(self, argument_dict):
        raise_logger(str(self.__class__.__name__) + str(argument_dict))


