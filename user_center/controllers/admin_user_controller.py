from controllers.base_controller import BaseController
from tools.decorator_tools import FormateOutput, AESOutput
from common_settings import *
from tools.data_formate_tools import *
from tools.check_tools import check_bg_ip
from services.user_base_service import UserBaseService
from tools.check_tools import check_authentication
from tools.check_tools import check_admin_user_platform_level, check_admin_user_platform_level_new
from config import check_use_source


class BgGenerateRegisterKeySaltController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=10001, return_type='return_error')
    def post(self):
        """
        用户注册时,获取用户key_salt
        :return:
        """
        # 1.0 校验平台
        result = check_bg_ip()
        if result is False:
            self.return_error(30000)

        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_name', 'client_public_key', 'level'], check_token=False, invariable_key=False,
            api_type=_USER_TYPE_ADMIN,  request_type=_REQUEST_TYPE_REGISTER,
            decode_by_inner=_DECODE_TYPE_INNER)
        name = argument_dict['user_name']
        client_public_key = argument_dict['client_public_key']
        level = argument_dict['level']
        if not check_admin_user_platform_level(level):
            self.return_error(10039)

        # 2.0 创建用户并且创建salt
        us = UserBaseService( aes_share_key=aes_share_key, aes_nonce=aes_nonce)
        result = us.get_register_key_salt(name, client_public_key, user_type=_USER_TYPE_ADMIN, admin_level=level)
        return result, aes_share_key, aes_nonce


class AdminUserRegisterController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30202, return_type='return_error')
    def post(self):
        """
        用户注册
        :return:
        header 放入 User-Mobile 为用户名
        """
        # 1.0 校验平台
        result = check_bg_ip()
        if result is False:
            self.return_error(30000)

        if check_use_source(_USE_SOURCE_TYPE_1):
            return result
        else:
            # 2.0 获取注册参数
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_mobile', 'vcode', 'password', 'level'], check_token=False, api_type=_USER_TYPE_ADMIN,
                 request_type=_REQUEST_TYPE_REGISTER, decode_by_inner=_DECODE_TYPE_INNER)

            user_name = argument_dict['user_mobile']
            vcode = argument_dict['vcode']
            password = argument_dict['password']
            level = argument_dict['level']

            if not check_admin_user_platform_level(level):
                self.return_error(10039)

            # 3.0 检查验证码有效性
            if not check_authentication(vcode):
                self.return_error(30201)

            # 4.0 处理用户注册逻辑, 注册后更新saltkey
            result = UserBaseService( aes_share_key=aes_share_key, aes_nonce=aes_nonce).\
                register(user_name, password, level, user_type=_USER_TYPE_ADMIN)
            return result, aes_share_key, aes_nonce


class BgGenerateLoginKeySaltController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=10001, return_type='return_error')
    def post(self):
        """
        登录时创建key_salt
        :return:
        """

        # 1.0 校验平台
        result = check_bg_ip()
        if result is False:
            self.return_error(30000)

        user_type = _USER_TYPE_ADMIN
        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_mobile', 'client_public_key', 'level'], check_token=False, invariable_key=False,
            api_type=user_type,  request_type=_REQUEST_TYPE_LOGIN,
            decode_by_inner=_DECODE_TYPE_DEFAULT, check_form_token=False)

        user_mobile = argument_dict['user_mobile']
        client_public_key = argument_dict['client_public_key']
        level = argument_dict['level']
        if not check_admin_user_platform_level_new(level):
            self.return_error(10039)

        us = UserBaseService( aes_share_key=aes_share_key, aes_nonce=aes_nonce)
        # 创建salt
        result = us.get_login_key_salt(user_mobile, client_public_key, user_type=user_type, admin_level=level)
        return result, aes_share_key, aes_nonce


class AdminUserLoginController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30204, return_type='return_error')
    def post(self):
        """
        登录
        :return:
        """
        # 1.0 校验平台
        result = check_bg_ip()
        if result is False:
            self.return_error(30000)

        user_type = _USER_TYPE_ADMIN
        # 2.0 获取登录参数
        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_mobile', 'password', 'level'], check_token=False, api_type=user_type, 
            request_type=_REQUEST_TYPE_LOGINING, decode_by_inner=_DECODE_TYPE_INNER, check_form_token=True)
        user_name = argument_dict['user_mobile']
        password = argument_dict['password']
        level = argument_dict['level']
        if not check_admin_user_platform_level_new(level):
            self.return_error(10039)

        # 3.0 完成登录
        r = UserBaseService( aes_share_key=aes_share_key, aes_nonce=aes_nonce).\
            login(user_name, password, user_type=user_type, admin_level=level)
        return r, aes_share_key, aes_nonce


class BgGetUserMessageController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormateOutput(default_value=30206, return_type='return_error')
    def post(self):
        # 1.0 校验平台
        result = check_bg_ip()
        if result is False:
            self.return_error(30000)

        # 2.0 获取参数
        argument_dict, _, _ = self.get_argument_dict(
            api_type=_USER_TYPE_ADMIN,  request_type=_REQUEST_TYPE_LOGIN,
            decode_by_inner=_DECODE_TYPE_INNER)

        return argument_dict


class BgGetUserInfoController(BaseController):
    """
    用于其他平台获取用户的基本信息，需要根据用户的userid和token（相当于用户处于登录状态），确认用户的身份，才能获取用户的信息
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormateOutput(default_value=30207, return_type='return_error')
    def post(self):
        if check_use_source( _USE_SOURCE_TYPE_1):
            # 1.0 校验平台
            result = check_bg_ip()
            if result is False:
                self.return_error(30000)
            # 2.0 获取参数
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_id', 'level'], verify_timeliness=False, api_type=_USER_TYPE_ADMIN, check_token=False,
                invariable_key=False,  request_type=_REQUEST_TYPE_LOGIN,
                decode_by_inner=_DECODE_TYPE_DEFAULT)

            user_id = argument_dict['user_id']
            level = argument_dict['level']

            user_service = UserBaseService( aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            user_info = user_service.get_admin_user_info_by_id(
                user_id,
                admin_level=level
            )

            return user_info
        else:
            # 1.0 校验平台
            result = check_bg_ip()
            if result is False:
                self.return_error(30000)

            # 2.0 获取参数
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_id', 'level'], verify_timeliness=False, api_type=_USER_TYPE_ADMIN, check_token=False,
                invariable_key=False,  request_type=_REQUEST_TYPE_LOGIN,
                decode_by_inner=_DECODE_TYPE_INNER)

            user_service = UserBaseService( aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            user_info = user_service.get_user_info_by_id(argument_dict['user_id'], user_type=_USER_TYPE_ADMIN, admin_level=argument_dict['level'])

            return user_info


class AdminUserResetLoginPasswordController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    '''
    重置登录密码, 必须是登录状态下重置，否则直接删数据库，从新注册
    '''
    @AESOutput()
    @FormateOutput(default_value=30208, return_type='return_error')
    def post(self):
        # 1.0 校验平台
        result = check_bg_ip()
        if result is False:
            self.return_error(30000)

        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_id', 'vcode', 'password', 'level'], api_type=_USER_TYPE_ADMIN, 
            request_type=_REQUEST_TYPE_LOGIN, decode_by_inner=_DECODE_TYPE_INNER)

        user_id = argument_dict['user_id']
        vcode = argument_dict['vcode']
        password = argument_dict['password']
        level = argument_dict['level']
        if not check_admin_user_platform_level(level):
            self.return_error(10039)

        # 3.0 检查验证码有效性
        if not check_authentication(vcode):
            self.return_error(30201)

        r = UserBaseService( aes_share_key=aes_share_key, aes_nonce=aes_nonce).\
            reset_login_password(user_id, password, user_type=_USER_TYPE_ADMIN, admin_level=level)

        return r, aes_share_key, aes_nonce


class AdminUserRegisterByAdminController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30202, return_type='return_error')
    def post(self):
        if check_use_source( _USE_SOURCE_TYPE_1):
            # 1.0 校验平台
            result = check_bg_ip()
            if result is False:
                self.return_error(30000)
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_id', 'user_name', 'password', 'rights_list'],
                api_type=_USER_TYPE_ADMIN,  request_type=_REQUEST_TYPE_LOGIN, check_form_token=True,
            )

            user_id = argument_dict['user_id']
            user_name = argument_dict['user_name']
            password = argument_dict['password']
            rights_list = argument_dict['rights_list']

            user_service = UserBaseService( aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            result = user_service.register_by_admin(user_id, user_name, password, rights_list)

            return result, aes_share_key, aes_nonce
        else:
            return False


class AdminUserDeleteByAdminController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30202, return_type='return_error')
    def post(self):
        if check_use_source( _USE_SOURCE_TYPE_1):
            # 1.0 校验平台
            result = check_bg_ip()
            if result is False:
                self.return_error(30000)
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_id', 'user_name'],
                api_type=_USER_TYPE_ADMIN,  request_type=_REQUEST_TYPE_LOGIN, check_form_token=True,
            )

            user_id = argument_dict['user_id']
            user_name = argument_dict['user_name']

            user_service = UserBaseService( aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            result = user_service.delete_by_admin(user_id, user_name)

            return result, aes_share_key, aes_nonce
        else:
            return False


class AdminUserChangeRightsByAdminController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30202, return_type='return_error')
    def post(self):
        if check_use_source( _USE_SOURCE_TYPE_1):
            # 1.0 校验平台
            result = check_bg_ip()
            if result is False:
                self.return_error(30000)
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_id', 'user_name', 'rights_list', 'password', 'change_type'],
                api_type=_USER_TYPE_ADMIN,  request_type=_REQUEST_TYPE_LOGIN, check_form_token=True,
            )

            user_id = argument_dict['user_id']
            user_name = argument_dict['user_name']
            rights_list = argument_dict['rights_list']
            password = argument_dict['password']
            change_type = argument_dict['change_type']

            user_service = UserBaseService( aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            result = user_service.change_rights_by_admin(user_id, user_name, rights_list, password, change_type)

            return result, aes_share_key, aes_nonce
        else:
            return False


class AdminUserListRightsByAdminController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30202, return_type='return_error')
    def post(self):
        if check_use_source( _USE_SOURCE_TYPE_1):
            # 1.0 校验平台
            result = check_bg_ip()
            if result is False:
                self.return_error(30000)
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_id', 'user_name'],
                api_type=_USER_TYPE_ADMIN,  request_type=_REQUEST_TYPE_LOGIN, check_form_token=False,
            )

            user_id = argument_dict['user_id']
            user_name = argument_dict['user_name']

            user_service = UserBaseService( aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            result = user_service.list_rights_by_admin(user_id, user_name)

            return result, aes_share_key, aes_nonce
        else:
            return False


class AdminListRightsByAdminController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30202, return_type='return_error')
    def post(self):
        if check_use_source(_USE_SOURCE_TYPE_1):
            # 1.0 校验平台
            result = check_bg_ip()
            if result is False:
                self.return_error(30000)
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_id'],
                api_type=_USER_TYPE_ADMIN,  request_type=_REQUEST_TYPE_LOGIN,
            )

            user_id = argument_dict['user_id']

            user_service = UserBaseService( aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            result = user_service.list_rights_to_admin(user_id)

            return result, aes_share_key, aes_nonce
        else:
            return False


