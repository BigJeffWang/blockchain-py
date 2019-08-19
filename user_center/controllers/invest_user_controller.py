from controllers.base_controller import BaseController
from tools.decorator_tools import FormateOutput, AESOutput
from common_settings import *
from tools.data_formate_tools import *
from services.user_base_service import UserBaseService
from services.vcode_service import VcodeService
from tools.check_tools import check_bg_ip
from services.password_service import PasswordService
from config import *
from flask import redirect
from config import get_transfer_to_platform_path
from tools.transfer_tools import transfer_to_platform


class InvestUserGenerateRegisterKeySaltController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=10001, return_type='return_error')
    def post(self):
        """
        用户注册时,获取用户key_salt
        :return:
        """
        user_type = _USER_TYPE_INVEST
        if check_use_source(_USE_SOURCE_TYPE_1):
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_name', 'client_public_key', 'source', 'register_by', 'mobile_country_code'], check_token=False, invariable_key=False,
                api_type=user_type, request_type=_REQUEST_TYPE_REGISTER)
            name = argument_dict['user_name']
            client_public_key = argument_dict['client_public_key']
            user_source = argument_dict['source']
            register_by = argument_dict['register_by']
            mobile_country_code = argument_dict['mobile_country_code']

            # 2.0 创建用户并且创建salt
            us = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            result = us.get_register_key_salt_by_type(name, client_public_key, register_by, user_type=user_type,
                                                      user_source=user_source, mobile_country_code=mobile_country_code)
        else:
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_name', 'client_public_key'], check_token=False, invariable_key=False,
                api_type=user_type,
                request_type=_REQUEST_TYPE_REGISTER)
            name = argument_dict['user_name']
            client_public_key = argument_dict['client_public_key']

            # 2.0 创建用户并且创建salt
            us = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            result = us.get_register_key_salt(name, client_public_key, user_type=user_type)
        return result, aes_share_key, aes_nonce


class InvestUserRegisterController(BaseController):
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
        user_type = _USER_TYPE_INVEST

        if check_use_source(_USE_SOURCE_TYPE_1):
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_mobile', 'vcode', 'password', 'source', 'register_by', 'mobile_country_code'],
                check_token=False, invariable_key=True, api_type=user_type, check_form_token=True,
                request_type=_REQUEST_TYPE_REGISTER
            )
            user_mobile = argument_dict['user_mobile']
            vcode = argument_dict['vcode']
            password = argument_dict['password']
            source = argument_dict['source']
            register_by = argument_dict['register_by']
            mobile_country_code = argument_dict['mobile_country_code']
            # 新需求取消用户名注册的方式
            # user_name = argument_dict['user_name']
            user_name = None

            vcode_service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)

            # 3.0 检查验证码有效性
            vcode_service.check_vcode(vcode, _VCODE_REGISTER, user_mobile, user_type=user_type,
                                      register_by=register_by)

            user_service = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            # 4.0 处理用户注册逻辑
            result = user_service.register_by_type(user_mobile, password, user_type=user_type, source=source,
                                                   db_user_name=user_name, register_by=register_by,
                                                   mobile_country_code=mobile_country_code, change_key_nonce=True)

            if ('status' not in result) or result['status'] != "true":
                return result, aes_share_key, aes_nonce

            # 6.0 注册后直接登录
            login_result = user_service.login_by_type(user_mobile, password, user_type, source=source,
                                                      register_by=register_by, mobile_country_code=mobile_country_code)
            result = dict(result, **login_result)
        else:
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_mobile', 'vcode', 'password'], check_token=False,
                invariable_key=True, api_type=user_type, request_type=_REQUEST_TYPE_REGISTER)
            user_mobile = argument_dict['user_mobile']
            vcode = argument_dict['vcode']
            password = argument_dict['password']

            vcode_service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)

            # 3.0 检查验证码有效性
            vcode_service.check_vcode(vcode, _VCODE_REGISTER, user_mobile, user_type=user_type)

            user_service = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            # 4.0 处理用户注册逻辑
            result = user_service.register(user_mobile, password, 0, user_type=user_type)

            if ('status' not in result) or result['status'] != "true":
                return result, aes_share_key, aes_nonce

            # 5.0 账户表中生成用户账户
            transfer_url = get_transfer_to_platform_path("invest", "generate_account")
            account_response_dict = transfer_to_platform(transfer_url, data={
                "user_id": result['user_id'],
                "user_mobile": user_mobile
            })

            if ("code" not in account_response_dict) or ("data" not in account_response_dict) or \
                    ('status' not in account_response_dict["data"]) or account_response_dict["data"]['status'] != "true":
                return account_response_dict, aes_share_key, aes_nonce
            user_service.register_on(user_mobile)

            # 6.0 注册后直接登录
            login_result = user_service.login(user_mobile, password, user_type)
            result = dict(result, **login_result)
        return result, aes_share_key, aes_nonce


class InvestGenerateLoginKeySaltController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=10001, return_type='return_error')
    def post(self):
        """
        登录时创建key_salt
        :return:
        """
        user_type = _USER_TYPE_INVEST

        if check_use_source(_USE_SOURCE_TYPE_1):
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_name', 'client_public_key', 'source', 'register_by', 'mobile_country_code'],
                check_token=False, invariable_key=False, api_type=user_type,
                request_type=_REQUEST_TYPE_LOGIN)
            user_mobile = argument_dict['user_name']
            client_public_key = argument_dict['client_public_key']
            source = argument_dict['source']
            register_by = argument_dict['register_by']
            mobile_country_code = argument_dict['mobile_country_code']

            us = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            # 创建salt
            result = us.get_login_key_salt_by_type(user_mobile, client_public_key, user_type=user_type, source=source,
                                                   register_by=register_by, mobile_country_code=mobile_country_code)
        else:
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_name', 'client_public_key'], check_token=False, invariable_key=False, api_type=user_type,
                request_type=_REQUEST_TYPE_LOGIN)
            user_mobile = argument_dict['user_name']
            client_public_key = argument_dict['client_public_key']
            us = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            # 创建salt
            result = us.get_login_key_salt(user_mobile, client_public_key, user_type=user_type)
        return result, aes_share_key, aes_nonce


class InvestUserLoginController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30204, return_type='return_error')
    def post(self):
        """
        登录
        :return:
        """

        user_type = _USER_TYPE_INVEST
        if check_use_source(_USE_SOURCE_TYPE_1):
            # 2.0 获取登录参数
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_mobile', 'password', 'source', 'register_by', 'mobile_country_code'],
                check_token=False, api_type=user_type, request_type=_REQUEST_TYPE_LOGINING, check_form_token=True)
            user_mobile = argument_dict['user_mobile']
            password = argument_dict['password']
            source = argument_dict['source']
            register_by = argument_dict['register_by']
            mobile_country_code = argument_dict['mobile_country_code']

            # 3.0 完成登录
            r = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce). \
                login_by_type(user_mobile, password, user_type=user_type, source=source,
                              register_by=register_by, mobile_country_code=mobile_country_code)
        else:
            # 2.0 获取登录参数
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_mobile', 'password'], check_token=False, api_type=user_type,
                request_type=_REQUEST_TYPE_LOGINING)
            user_mobile = argument_dict['user_mobile']
            password = argument_dict['password']

            # 3.0 完成登录
            r = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce).\
                login(user_mobile, password, user_type=user_type)
        return r, aes_share_key, aes_nonce


class InvestGetUserMessageController(BaseController):
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
            api_type=_USER_TYPE_INVEST, request_type=_REQUEST_TYPE_LOGIN,
            decode_by_inner=_DECODE_TYPE_INNER, check_user_id=True)

        return argument_dict


class InvestGetUserInfoController(BaseController):
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

        user_type = _USER_TYPE_INVEST
        # 2.0 获取参数
        argument_dict, _, _ = self.get_argument_dict(
            must_keys=['user_id'], verify_timeliness=False, api_type=user_type, check_token=False, invariable_key=False,
            request_type=_REQUEST_TYPE_LOGIN, decode_by_inner=_DECODE_TYPE_INNER)

        user_info = UserBaseService().\
            get_user_info_by_id(argument_dict['user_id'], user_type=user_type)

        return user_info


class InvestUserClientInfoController(BaseController):
    """
    用于客户端获取用户的基本信息，需要根据用户的userid和token（相当于用户处于登录状态），确认用户的身份，才能获取用户的信息
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30207, return_type='return_error')
    def post(self):
        user_type = _USER_TYPE_INVEST
        # 2.0 获取参数
        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_id'], api_type=user_type, request_type=_REQUEST_TYPE_LOGIN)

        user_info = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce).\
            get_user_info_by_id(argument_dict['user_id'], user_type=user_type)

        if check_use_source(_USE_SOURCE_TYPE_1):
            if 'user_mobile' in user_info and 'user_id' in user_info and user_info['user_id'] == user_info['user_mobile']:
                user_info['user_mobile'] = ''
            if 'email' in user_info and 'user_id' in user_info and user_info['user_id'] == user_info['email']:
                user_info['email'] = ''

            # 5.0 补充账户信息
            transfer_url = get_transfer_to_platform_path("invest", "user_info")
            if transfer_url != '':
                account_response_dict = transfer_to_platform(transfer_url, data={
                    "user_id": user_info['user_id']
                })

                if ("code" not in account_response_dict) or ("data" not in account_response_dict):
                    self.return_error(30207)
                if account_response_dict['code'] != '00000':
                    self.return_error(account_response_dict['code'], account_response_dict['msg'])

                user_info.update(account_response_dict['data'])

        return user_info, aes_share_key, aes_nonce


class InvestUserChangeLoginPasswordController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    '''
    修改登录密码
    '''
    @AESOutput()
    @FormateOutput(default_value=30211, return_type='return_error')
    def post(self):
        password_config = get_password_config()
        user_type = _USER_TYPE_INVEST

        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_id', 'old_password', 'new_password'], api_type=_USER_TYPE_INVEST,
            request_type=_REQUEST_TYPE_LOGIN, check_form_token=True)

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
            change_login_password(user_id, old_password, new_password)
        return r, aes_share_key, aes_nonce


class InvestUserResetLoginPasswordController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    '''
    重置登录密码
    '''
    @AESOutput()
    @FormateOutput(default_value=30208, return_type='return_error')
    def post(self):
        user_type = _USER_TYPE_INVEST
        if check_use_source(_USE_SOURCE_TYPE_1):
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_mobile', 'vcode', 'password', 'mobile_country_code', 'register_by'], check_token=False,
                api_type=user_type, invariable_key=False, request_type=_REQUEST_TYPE_REGISTER, check_form_token=True)

            user_mobile = argument_dict['user_mobile']
            vcode = argument_dict['vcode']
            password = argument_dict['password']
            mobile_country_code = argument_dict['mobile_country_code']
            register_by = argument_dict['register_by']

            if register_by not in [
                _RESET_PWD_MOBILE,
                _RESET_PWD_EMAIL,
            ]:
                self.return_error(30223)

            vcode_service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            vcode_service.check_vcode(vcode, _VCODE_RESETPD, user_mobile, user_type=user_type,
                                      register_by=register_by)

            r = UserBaseService(
                aes_share_key=aes_share_key,
                aes_nonce=aes_nonce
            ).reset_login_password_by_type(
                user_mobile,
                password,
                user_type=user_type,
                register_by=register_by,
                mobile_country_code=mobile_country_code,
            )
        else:
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_mobile', 'vcode', 'password'], check_token=False, api_type=user_type,
                invariable_key=False, request_type=_REQUEST_TYPE_REGISTER)

            user_mobile = argument_dict['user_mobile']
            vcode = argument_dict['vcode']
            password = argument_dict['password']

            vcode_service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            vcode_service.check_vcode(vcode, _VCODE_RESETPD, user_mobile, user_type=user_type)

            r = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce).\
                reset_login_password(user_mobile, password, user_type=user_type)

        return r, aes_share_key, aes_nonce


class InvestUpdateUserInfoController(BaseController):
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

        user_type = _USER_TYPE_INVEST
        # 2.0 获取参数
        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_id'], verify_timeliness=False, api_type=user_type, check_token=False, invariable_key=False,
            request_type=_REQUEST_TYPE_LOGIN, decode_by_inner=_DECODE_TYPE_INNER)

        user_info = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce).\
            update_user_info_by_id(argument_dict, user_type=user_type)

        return user_info


class InvestGeneratePayKeySaltController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=10001, return_type='return_error')
    def post(self):
        """
        登录时创建key_salt
        :return:
        """
        user_type = _USER_TYPE_INVEST

        if check_use_source(_USE_SOURCE_TYPE_1):
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_id'], api_type=user_type,
                request_type=_REQUEST_TYPE_LOGIN)
            user_id = argument_dict['user_id']

            us = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            # 创建salt
            result = us.get_pay_salt(user_id)
            return result, aes_share_key, aes_nonce
        else:
            self.return_error(10004)


class InvestUserAuthenticationController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    '''
    实名认证
    '''
    @AESOutput()
    @FormateOutput(default_value=30219, return_type='return_error')
    def post(self):
        user_type = _USER_TYPE_INVEST

        if check_use_source(_USE_SOURCE_TYPE_1):
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_id', 'mobile_country_code', 'email', 'user_mobile', 'pay_password', 'login_password'],
                api_type=user_type, request_type=_REQUEST_TYPE_LOGIN
            )

            user_id = argument_dict['user_id']
            mobile_country_code = argument_dict['mobile_country_code']
            email = argument_dict['email']
            user_mobile = argument_dict['user_mobile']
            pay_password = argument_dict['pay_password']
            login_password = argument_dict['login_password']

            r = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce).\
                real_name_authentication(user_id, mobile_country_code, email, user_mobile, login_password,
                                         pay_password, user_type=user_type)
            return r, aes_share_key, aes_nonce
        else:
            self.return_error(10004)


class InvestUserResetPayPasswordController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30219, return_type='return_error')
    def post(self):
        user_type = _USER_TYPE_INVEST

        if check_use_source(_USE_SOURCE_TYPE_1):
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_id', 'pay_password', 'vcode', 'login_password', 'register_by'],
                api_type=user_type, request_type=_REQUEST_TYPE_LOGIN, check_form_token=True
            )

            user_id = argument_dict['user_id']
            login_password = argument_dict['login_password']
            vcode = argument_dict['vcode']
            pay_password = argument_dict['pay_password']
            register_by = argument_dict['register_by']

            if register_by not in [
                _REGISTER_RESET_PAYPD_MOBILE,
                _REGISTER_RESET_PAYPD_EMAIL,
            ]:
                self.return_error(30223)

            # 1.0 检查验证码有效性
            vcode_service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            vcode_service.check_vcode(vcode, _VCODE_RESET_PAY_PD, user_id, user_type=user_type,
                                      register_by=register_by)

            # 2.0 修改密码
            r = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce). \
                set_pay_password(user_id, login_password, pay_password, user_type=user_type)
            return r, aes_share_key, aes_nonce
        else:
            self.return_error(10004)


class InvestUserSetMobileController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    '''
    设置手机号
    '''
    @AESOutput()
    @FormateOutput(default_value=30225, return_type='return_error')
    def post(self):
        user_type = _USER_TYPE_INVEST

        if check_use_source(_USE_SOURCE_TYPE_1):
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_id', 'mobile_country_code', 'mobile', 'vcode'],
                api_type=user_type, request_type=_REQUEST_TYPE_LOGIN, check_form_token=True
            )

            user_id = argument_dict['user_id']
            mobile_country_code = argument_dict['mobile_country_code']
            user_mobile = argument_dict['mobile']
            vcode = argument_dict['vcode']
            register_by = _REGISTER_SET_MOBILE

            vcode_service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            vcode_service.check_vcode(
                vcode,
                _VCODE_SET_MOBILE,
                user_id,
                user_type=user_type,
                register_by=register_by,
            )

            r = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce). \
                set_mobile(user_id, mobile_country_code, user_mobile, user_type=user_type)
            return r, aes_share_key, aes_nonce
        else:
            self.return_error(10004)


class InvestUserEmailController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    '''
    设置email
    '''
    @AESOutput()
    @FormateOutput(default_value=30225, return_type='return_error')
    def post(self):
        user_type = _USER_TYPE_INVEST

        if check_use_source(_USE_SOURCE_TYPE_1):
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_id', 'email', 'vcode'],
                api_type=user_type, request_type=_REQUEST_TYPE_LOGIN, check_form_token=True
            )

            user_id = argument_dict['user_id']
            email = argument_dict['email']
            vcode = argument_dict['vcode']

            register_by = _REGISTER_SET_EMAIL

            vcode_service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            vcode_service.check_vcode(
                vcode,
                _VCODE_SET_EMAIL,
                user_id,
                user_type=user_type,
                register_by=register_by,
            )

            r = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce). \
                set_email(user_id, email, user_type=user_type)
            return r, aes_share_key, aes_nonce
        else:
            self.return_error(10004)


class InvestUserNickNameController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    '''
    设置昵称
    '''
    @AESOutput()
    @FormateOutput(default_value=30225, return_type='return_error')
    def post(self):
        user_type = _USER_TYPE_INVEST

        if check_use_source(_USE_SOURCE_TYPE_1):
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_id', 'nick_name'],
                api_type=user_type, request_type=_REQUEST_TYPE_LOGIN, check_form_token=True
            )

            user_id = argument_dict['user_id']
            nick_name = argument_dict['nick_name']

            r = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce). \
                set_nick_name(user_id, nick_name, user_type=user_type)
            return r, aes_share_key, aes_nonce
        else:
            self.return_error(10004)


class InvestUserAvatarController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    '''
    设置头像
    '''
    @AESOutput()
    @FormateOutput(default_value=30225, return_type='return_error')
    def post(self):
        user_type = _USER_TYPE_INVEST

        if check_use_source(_USE_SOURCE_TYPE_1):
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_id', 'avatar'],
                api_type=user_type, request_type=_REQUEST_TYPE_LOGIN, check_form_token=True
            )

            user_id = argument_dict['user_id']
            avatar = argument_dict['avatar']

            r = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce). \
                set_avatar(user_id, avatar, user_type=user_type)
            return r, aes_share_key, aes_nonce
        else:
            self.return_error(10004)


class InvestUserPayPWDController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    '''
    设置交易密码
    '''
    @AESOutput()
    @FormateOutput(default_value=30225, return_type='return_error')
    def post(self):
        user_type = _USER_TYPE_INVEST

        if check_use_source(_USE_SOURCE_TYPE_1):
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_id', 'pay_password', 'login_password', 'vcode', 'register_by'],
                api_type=user_type, request_type=_REQUEST_TYPE_LOGIN, check_form_token=True
            )

            user_id = argument_dict['user_id']
            pay_password = argument_dict['pay_password']
            login_password = argument_dict['login_password']
            vcode = argument_dict['vcode']
            register_by = argument_dict['register_by']

            # 1.0 检查验证码有效性
            vcode_service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
            vcode_service.check_vcode(vcode, _VCODE_SET_PAY_PD, user_id, user_type=user_type,
                                      register_by=register_by)

            r = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce). \
                set_pay_password(user_id, login_password, pay_password, user_type=user_type)
            return r, aes_share_key, aes_nonce
        else:
            self.return_error(10004)


class InvestUserLoginByMobileController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30204, return_type='return_error')
    def post(self):
        """
        登录
        :return:
        """

        user_type = _USER_TYPE_INVEST
        if check_use_source(_USE_SOURCE_TYPE_1):
            # 2.0 获取登录参数
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_mobile', 'vcode', 'source', 'mobile_country_code'],
                check_token=False, api_type=user_type, request_type=_REQUEST_TYPE_LOGINING, check_form_token=True)
            user_mobile = argument_dict['user_mobile']
            vcode = argument_dict['vcode']
            source = argument_dict['source']
            mobile_country_code = argument_dict['mobile_country_code']

            # 3.0 完成登录
            r = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce). \
                login_by_mobile(user_mobile, vcode, user_type=user_type, source=source,
                                mobile_country_code=mobile_country_code)
            return r, aes_share_key, aes_nonce
        else:
            self.return_error(10006)


class DevInvestUserGenerateRegisterKeySaltController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=10001, return_type='return_error')
    def post(self):
        """
        仅开发环境，不aes加密用户注册时,获取用户key_salt
        :return:
        """
        if get_conf('env') != 'dev':
            self.return_error(10044)
        user_type = _USER_TYPE_INVEST
        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_name', 'source', 'register_by', 'mobile_country_code'],
            verify_timeliness=False,
            check_token=False,
            invariable_key=False,
            encrypt=False,
            check_form_token=False,
            api_type=user_type,
            request_type=_REQUEST_TYPE_REGISTER
        )
        name = argument_dict['user_name']
        user_source = argument_dict['source']
        register_by = argument_dict['register_by']
        mobile_country_code = argument_dict['mobile_country_code']

        # 2.0 创建用户并且创建salt
        us = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
        result = us.dev_get_register_key_salt_by_type(
            name,
            register_by,
            user_type=user_type,
            user_source=user_source,
            mobile_country_code=mobile_country_code
        )
        return result, aes_share_key, aes_nonce


class DevInvestGenerateLoginKeySaltController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=10001, return_type='return_error')
    def post(self):
        """
        仅开发环境，不aes加密登录时创建key_salt
        :return:
        """
        if get_conf('env') != 'dev':
            self.return_error(10044)

        user_type = _USER_TYPE_INVEST
        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_name', 'source', 'register_by', 'mobile_country_code'],
            verify_timeliness=False,
            check_token=False,
            invariable_key=False,
            encrypt=False,
            check_form_token=False,
            api_type=user_type,
            request_type=_REQUEST_TYPE_LOGIN
        )
        user_mobile = argument_dict['user_name']
        source = argument_dict['source']
        register_by = argument_dict['register_by']
        mobile_country_code = argument_dict['mobile_country_code']

        us = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
        # 创建salt
        result = us.dev_get_login_key_salt_by_type(
            user_mobile,
            user_type=user_type,
            source=source,
            register_by=register_by,
            mobile_country_code=mobile_country_code
        )

        return result, aes_share_key, aes_nonce


class InvestLoginGenerateLoginKeySaltController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=10001, return_type='return_error')
    def post(self):
        """
        获取登陆盐，用于登陆状态下修改密码的接口
        :return:
        """

        user_type = _USER_TYPE_INVEST
        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=[],
            api_type=user_type,
            request_type=_REQUEST_TYPE_LOGIN
        )
        user_id = argument_dict['user_mobile']

        us = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
        # 创建salt
        result = us.get_login_client_salt(
            user_id,
            user_type=user_type,
        )
        return result, aes_share_key, aes_nonce


class InvestUnLoginGenerateLoginKeySaltController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=10001, return_type='return_error')
    def post(self):
        """
        登录时创建key_salt
        :return:
        """
        user_type = _USER_TYPE_INVEST

        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_mobile', 'register_by', 'mobile_country_code'],
            check_token=False,
            invariable_key=False,
            api_type=user_type,
            request_type=_REQUEST_TYPE_LOGIN
        )
        user_mobile = argument_dict['user_mobile']
        register_by = argument_dict['register_by']
        mobile_country_code = argument_dict['mobile_country_code']

        us = UserBaseService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
        # 创建salt
        result = us.get_unlogin_client_salt(
            user_mobile,
            user_type=user_type,
            register_by=register_by,
            mobile_country_code=mobile_country_code,
        )
        return result, aes_share_key, aes_nonce





