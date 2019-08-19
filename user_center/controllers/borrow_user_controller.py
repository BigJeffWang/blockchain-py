from controllers.base_controller import BaseController
from tools.decorator_tools import FormateOutput, AESOutput
from common_settings import *
from tools.data_formate_tools import *
from services.user_base_service import UserBaseService
from services.vcode_service import VcodeService
from tools.check_tools import check_bg_ip
from config import *
from flask import redirect
from services.password_service import PasswordService


class BorrowUserGenerateRegisterKeySalt(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=10001, return_type='return_error')
    def post(self):
        """
        用户注册时,获取用户key_salt
        :return:
        """
        user_type = _USER_TYPE_BORROW
        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_name', 'client_public_key'], check_token=False, invariable_key=False, api_type=user_type,
            request_type=_REQUEST_TYPE_REGISTER)
        name = argument_dict['user_name']
        client_public_key = argument_dict['client_public_key']

        # 2.0 创建用户并且创建salt
        us = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
        result = us.get_register_key_salt(name, client_public_key, user_type=user_type)
        return result, aes_share_key, aes_nonce


class BorrowUserRegisterController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30202, return_type='return_error')
    def post(self):
        """
        用户注册
        :return:
        """
        # 1.0 获取注册参数
        user_type = _USER_TYPE_BORROW

        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_mobile', 'vcode', 'password', 'register_signature'], check_token=False,
            invariable_key=True, api_type=user_type, request_type=_REQUEST_TYPE_REGISTER)
        user_mobile = argument_dict['user_mobile']
        vcode = argument_dict['vcode']
        password = argument_dict['password']
        register_signature = argument_dict['register_signature']

        vcode_service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
        # 2.0 校验touken
        vcode_service.check_register_signature(register_signature)

        # 3.0 检查验证码有效性
        vcode_service.check_vcode(vcode, _VCODE_REGISTER, user_mobile, user_type=user_type)

        user_service = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
        # 4.0 处理用户注册逻辑
        result = user_service.register(user_mobile, password, 0, user_type=user_type)

        if ('status' not in result) or result['status'] != "true":
            return result, aes_share_key, aes_nonce

        # 5.0 注册后直接登录
        login_result = user_service.login(user_mobile, password, user_type)
        result = dict(result, **login_result)
        return result, aes_share_key, aes_nonce


class BorrowGenerateLoginKeySalt(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=10001, return_type='return_error')
    def post(self):
        """
        登录时创建key_salt
        :return:
        """
        user_type = _USER_TYPE_BORROW
        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_name', 'client_public_key'], check_token=False, invariable_key=False, api_type=user_type,
            request_type=_REQUEST_TYPE_LOGIN)
        user_mobile = argument_dict['user_name']
        client_public_key = argument_dict['client_public_key']
        us = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
        # 创建salt
        result = us.get_login_key_salt(user_mobile, client_public_key, user_type=user_type)
        return result, aes_share_key, aes_nonce


class BorrowUserLoginController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30204, return_type='return_error')
    def post(self):
        """
        登录
        :return:
        """

        user_tyoe = _USER_TYPE_BORROW
        # 2.0 获取登录参数
        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_mobile', 'password'], check_token=False, api_type=user_tyoe,
            request_type=_REQUEST_TYPE_LOGINING)
        user_mobile = argument_dict['user_mobile']
        password = argument_dict['password']

        # 3.0 完成登录
        r = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce).\
            login(user_mobile, password, user_type=user_tyoe)
        return r, aes_share_key, aes_nonce


class BorrowGetUserMessageController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormateOutput(default_value=30206, return_type='return_error')
    def post(self):
        # 1.0 校验平台
        result = check_bg_ip()
        if result is False:
            self.return_error(30000)

        # 2.0 获取参数
        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            api_type=_USER_TYPE_BORROW, request_type=_REQUEST_TYPE_LOGIN, check_user_id=True)

        return argument_dict


class BorrowGetUserInfoController(BaseController):
    """
    用于其他平台获取用户的基本信息，需要根据用户的userid和token（相当于用户处于登录状态），确认用户的身份，才能获取用户的信息
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormateOutput(default_value=30207, return_type='return_error')
    def post(self):
        # 1.0 校验平台
        result = check_bg_ip()
        if result is False:
            self.return_error(30000)

        user_type = _USER_TYPE_BORROW
        # 2.0 获取参数
        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_id'], verify_timeliness=False, api_type=user_type, check_token=False,
            invariable_key=False, request_type=_REQUEST_TYPE_LOGIN,
            decode_by_inner=_DECODE_TYPE_INNER)

        user_info = UserBaseService().\
            get_user_info_by_id(argument_dict['user_id'], user_type=user_type)

        return user_info


class BorrowUserClientInfoController(BaseController):
    """
    用于客户端获取用户的基本信息，需要根据用户的userid和token（相当于用户处于登录状态），确认用户的身份，才能获取用户的信息
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30207, return_type='return_error')
    def post(self):
        user_type = _USER_TYPE_BORROW
        # 2.0 获取参数
        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_id'], api_type=user_type, request_type=_REQUEST_TYPE_LOGIN)

        user_info = UserBaseService().\
            get_user_info_by_id(argument_dict['user_id'], user_type=user_type)

        return user_info, aes_share_key, aes_nonce


class BorrowUserChangeLoginPasswordController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    '''
    修改登录密码
    '''
    @AESOutput()
    @FormateOutput(default_value=30211, return_type='return_error')
    def post(self):
        password_config = get_password_config()
        user_type = _USER_TYPE_BORROW

        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_id', 'old_password', 'new_password'], api_type=user_type,
            request_type=_REQUEST_TYPE_LOGIN)

        if 'change_method' in password_config and password_config['change_method'] != "":
            password_check_service = PasswordService(
                aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            # 自己的修改密码方法
            if hasattr(password_check_service, password_config['change_method']):
                method_name = password_config['change_method']
                tmp_method = eval('password_check_service.' + method_name)
                r = tmp_method(argument_dict, user_type=user_type)
            else:
                r = password_check_service.base_check_method(argument_dict, user_type=user_type)
            if r['status'] == _PASSWORD_CHECK_TYPE_SUCCESS:
                return r, aes_share_key, aes_nonce
            elif r['status'] == _PASSWORD_CHECK_TYPE_REDIRECT:
                return redirect(r['rediret_url'])
            else:
                self.return_error(30211)

        user_id = argument_dict['user_id']
        old_password = argument_dict['old_password']
        new_password = argument_dict['new_password']

        r = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce).\
            change_login_password(user_id, old_password, new_password, user_type=user_type)
        return r, aes_share_key, aes_nonce


class BorrowUpdateUserInfoController(BaseController):
    """
    用于其他平台获取用户的基本信息，需要根据用户的userid和token（相当于用户处于登录状态），确认用户的身份，才能获取用户的信息
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormateOutput(default_value=30214, return_type='return_error')
    def post(self):
        # 1.0 校验平台
        result = check_bg_ip()
        if result is False:
            self.return_error(30000)

        user_type = _USER_TYPE_BORROW
        # 2.0 获取参数
        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_id'], verify_timeliness=False, api_type=user_type, check_token=False, invariable_key=False,
            request_type=_REQUEST_TYPE_LOGIN, decode_by_inner=_DECODE_TYPE_INNER)

        user_info = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce).\
            update_user_info_by_id(argument_dict, user_type=user_type)

        return user_info
