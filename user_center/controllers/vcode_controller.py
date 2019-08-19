from controllers.base_controller import BaseController
from services.vcode_service import VcodeService
from common_settings import *
from tools.decorator_tools import FormateOutput, AESOutput
from flask import Response
from tools.data_formate_tools import *
from config import *


class InvestUserGetPictureVCodeController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormateOutput(default_value=30050, return_type='return_error_by_header')
    def post(self):
        """
        发送验证码
        :return:
        """
        service = VcodeService()
        result, vcode_str = service.make_vcode_picture()
        resp = Response(result)
        service.set_vcode_picture(vcode_str, user_type=_USER_TYPE_INVEST)
        return resp


class InvestUserSendRegisterVCodeController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30051, return_type='return_error')
    def post(self):
        """
        发送验证码
          :param user_mobile: 手机号码
        :return:
        """
        user_type = _USER_TYPE_INVEST
        if check_use_source(_USE_SOURCE_TYPE_1):
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_mobile', 'pvcode', 'register_by', 'mobile_country_code'], check_token=False,
                invariable_key=False, api_type=user_type, request_type=_REQUEST_TYPE_REGISTER)

            user_mobile = str(argument_dict['user_mobile'])
            pvcode = str(argument_dict['pvcode'])
            register_by = argument_dict['register_by']
            mobile_country_code = argument_dict['mobile_country_code']
            send_type = _VCODE_REGISTER
            service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)

            # 校验图形验证码
            service.check_vcode_picture(pvcode)

            # 校验是否已经注册
            result = service.send_vcode_by_register_type(send_type, user_mobile, user_type=user_type,
                                                         register_by=register_by,
                                                         mobile_country_code=mobile_country_code)
        else:
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_mobile', 'pvcode'], check_token=False, invariable_key=False, api_type=user_type,
                request_type=_REQUEST_TYPE_REGISTER)

            user_mobile = str(argument_dict['user_mobile'])
            pvcode = str(argument_dict['pvcode'])
            send_type = _VCODE_REGISTER
            service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)

            # 校验图形验证码
            service.check_vcode_picture(pvcode)

            # 校验是否已经注册
            result = service.send_vcode(send_type, user_mobile, user_type=user_type)
        return result, aes_share_key, aes_nonce


class InvestUserRegisterSignatureController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormateOutput(default_value=30057, return_type='return_error')
    def post(self):
        """
        发送验证码
        :return:
        """
        # 仅仅是为了保证不是重复请求
        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            encrypt=False, check_token=False, invariable_key=False, api_type=_USER_TYPE_INVEST,
            request_type=_REQUEST_TYPE_REGISTER, check_form_token=False)
        service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
        result = service.make_register_signature(save_time=1800)
        return result


class InvestUserSendResetPWDVCodeController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30051, return_type='return_error')
    def post(self):
        """
        发送验证码
          :param user_mobile: 手机号码
        :return:
        """
        user_type = _USER_TYPE_INVEST
        if check_use_source(_USE_SOURCE_TYPE_1):
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_mobile', 'pvcode', 'register_by', 'mobile_country_code'], check_token=False,
                invariable_key=False, api_type=user_type, request_type=_REQUEST_TYPE_REGISTER)

            user_mobile = str(argument_dict['user_mobile'])
            pvcode = str(argument_dict['pvcode'])
            register_by = argument_dict['register_by']
            mobile_country_code = argument_dict['mobile_country_code']
            send_type = _VCODE_RESETPD
            service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)

            if register_by not in [
                _RESET_PWD_MOBILE,
                _RESET_PWD_EMAIL,
            ]:
                self.return_error(30223)

            # 校验图形验证码
            service.check_vcode_picture(pvcode, vcode_type=send_type)

            # 校验是否已经注册
            result = service.send_vcode_by_register_type(send_type, user_mobile, user_type=user_type,
                                                         register_by=register_by,
                                                         mobile_country_code=mobile_country_code)
        else:
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_mobile', 'pvcode'], check_token=False, invariable_key=False, api_type=user_type,
                request_type=_REQUEST_TYPE_REGISTER)

            user_mobile = str(argument_dict['user_mobile'])
            pvcode = str(argument_dict['pvcode'])
            send_type = _VCODE_RESETPD
            service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)

            # 校验图形验证码
            service.check_vcode_picture(pvcode, vcode_type=send_type)

            # 校验是否已经注册
            result = service.send_vcode(send_type, user_mobile, user_type=user_type)
        return result, aes_share_key, aes_nonce


class InvestUserGetResetPWDPictureVCodeController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormateOutput(default_value=30050, return_type='return_error_by_header')
    def post(self):
        """
        发送验证码
        :return:
        """
        service = VcodeService()
        result, vcode_str = service.make_vcode_picture()
        resp = Response(result)
        service.set_vcode_picture(vcode_str, user_type=_USER_TYPE_INVEST, vcode_type=_VCODE_RESETPD)
        return resp


class BorrowUserGetPictureVCodeController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormateOutput(default_value=30050, return_type='return_error_by_header')
    def post(self):
        """
        发送验证码
        :return:
        """
        service = VcodeService()
        result, vcode_str = service.make_vcode_picture()
        resp = Response(result)
        service.set_vcode_picture(vcode_str, user_type=_USER_TYPE_BORROW)
        return resp


class BorrowUserSendRegisterVCodeController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30051, return_type='return_error')
    def post(self):
        """
        发送验证码
          :param user_mobile: 手机号码
        :return:
        """
        user_type = _USER_TYPE_BORROW
        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            must_keys=['user_mobile', 'pvcode'], check_token=False, invariable_key=False, api_type=user_type,
            request_type=_REQUEST_TYPE_REGISTER)

        user_mobile = str(argument_dict['user_mobile'])
        pvcode = str(argument_dict['pvcode'])
        send_type = _VCODE_REGISTER
        service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)

        # 校验图形验证码
        service.check_vcode_picture(pvcode)

        # 校验是否已经注册
        result = service.send_vcode(send_type, user_mobile, user_type=user_type)
        return result, aes_share_key, aes_nonce


class BorrowUserRegisterSignatureController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormateOutput(default_value=30057, return_type='return_error')
    def post(self):
        """
        发送验证码
        :return:
        """
        # 仅仅是为了保证不是重复请求
        argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
            encrypt=False, check_token=False, invariable_key=False, api_type=_USER_TYPE_BORROW,
            request_type=_REQUEST_TYPE_REGISTER)
        service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)
        result = service.make_register_signature()
        return result


class InvestUserSendResetPayPDVCodeController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30051, return_type='return_error')
    def post(self):
        """
        发送验证码
          :param user_mobile: 手机号码
        :return:
        """
        user_type = _USER_TYPE_INVEST
        if check_use_source(_USE_SOURCE_TYPE_1):
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_id', 'register_by', 'pvcode'], api_type=user_type, request_type=_REQUEST_TYPE_LOGIN)

            user_id = str(argument_dict['user_id'])
            register_by = argument_dict['register_by']
            pvcode = argument_dict['pvcode']

            if register_by not in [
                _REGISTER_RESET_PAYPD_MOBILE,
                _REGISTER_RESET_PAYPD_EMAIL,
            ]:
                self.return_error(30223)

            send_type = _VCODE_RESET_PAY_PD
            service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)

            service.check_vcode_picture(pvcode, user_type=_USER_TYPE_INVEST, vcode_type=_VCODE_RESET_PAY_PD)

            # 校验是否已经注册
            result = service.send_vcode_by_register_type(send_type, user_id, user_type=user_type,
                                                         register_by=register_by)
            return result, aes_share_key, aes_nonce
        else:
            self.return_error(10004)


class InvestUserSendSetPayPDVCodeController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30051, return_type='return_error')
    def post(self):
        """
        发送验证码
          :param user_mobile: 手机号码
        :return:
        """
        user_type = _USER_TYPE_INVEST
        if check_use_source(_USE_SOURCE_TYPE_1):
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_id', 'register_by', 'pvcode'], api_type=user_type, request_type=_REQUEST_TYPE_LOGIN)

            user_id = str(argument_dict['user_id'])
            register_by = argument_dict['register_by']
            pvcode = argument_dict['pvcode']

            if register_by not in [
                _REGISTER_SET_PAYPD_EMAIL,
                _REGISTER_SET_PAYPD_MOBILE,
            ]:
                self.return_error(30223)

            send_type = _VCODE_SET_PAY_PD
            service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)

            # 校验图形验证码
            service.check_vcode_picture(pvcode, user_type=_USER_TYPE_INVEST, vcode_type=_VCODE_SET_PAY_PD)

            # 校验是否已经注册
            result = service.send_vcode_by_register_type(send_type, user_id, user_type=user_type,
                                                         register_by=register_by)

            return result, aes_share_key, aes_nonce
        else:
            self.return_error(10004)


class InvestUserGetLoginPictureVCodeController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormateOutput(default_value=30050, return_type='return_error_by_header')
    def post(self):
        """
        发送验证码
        :return:
        """
        service = VcodeService()
        result, vcode_str = service.make_vcode_picture()
        resp = Response(result)
        service.set_vcode_picture(vcode_str, user_type=_USER_TYPE_INVEST, vcode_type=_REQUEST_TYPE_LOGINING)
        return resp


class InvestUserSendLoginVCodeController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30051, return_type='return_error')
    def post(self):
        """
        发送验证码
          :param user_mobile: 手机号码
        :return:
        """
        user_type = _USER_TYPE_INVEST
        if check_use_source(_USE_SOURCE_TYPE_1):
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_mobile', 'pvcode', 'mobile_country_code'], check_token=False,
                invariable_key=False, api_type=user_type, request_type=_REQUEST_TYPE_REGISTER)

            user_mobile = str(argument_dict['user_mobile'])
            pvcode = str(argument_dict['pvcode'])
            mobile_country_code = argument_dict['mobile_country_code']
            send_type = _VCODE_LOGIN
            service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)

            # 校验图形验证码
            service.check_vcode_picture(pvcode, user_type=_USER_TYPE_INVEST, vcode_type=_REQUEST_TYPE_LOGINING)

            # 校验是否已经注册
            result = service.send_vcode_by_register_type(send_type, user_mobile, user_type=user_type,
                                                         register_by=_REGISTER_BY_MOBILE,
                                                         mobile_country_code=mobile_country_code)
            return result, aes_share_key, aes_nonce
        else:
            self.return_error(10004)


class InvestUserGetPictureVCodeSetMobileController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormateOutput(default_value=30050, return_type='return_error_by_header')
    def post(self):
        """
        发送验证码
        :return:
        """
        service = VcodeService()
        result, vcode_str = service.make_vcode_picture()
        resp = Response(result)
        service.set_vcode_picture(vcode_str, user_type=_USER_TYPE_INVEST, vcode_type=_VCODE_SET_MOBILE)
        return resp


class InvestUserSendSetMobileVCodeController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30051, return_type='return_error')
    def post(self):
        """
        发送验证码
          :param user_mobile: 手机号码
        :return:
        """
        user_type = _USER_TYPE_INVEST
        if check_use_source(_USE_SOURCE_TYPE_1):
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_id', 'mobile', 'pvcode', 'mobile_country_code'],
                api_type=user_type,
                request_type=_REQUEST_TYPE_LOGIN
            )

            user_id = str(argument_dict['user_id'])
            user_mobile = argument_dict['mobile']
            mobile_country_code = argument_dict['mobile_country_code']
            pvcode = argument_dict['pvcode']

            register_by = _REGISTER_SET_MOBILE

            send_type = _VCODE_SET_MOBILE
            vcode_service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)

            # 校验图形验证码
            vcode_service.check_vcode_picture(pvcode, user_type=_USER_TYPE_INVEST, vcode_type=_VCODE_SET_MOBILE)

            # 校验是否已经注册
            result = vcode_service.send_vcode_by_register_type(
                send_type,
                user_mobile,
                user_type=user_type,
                register_by=register_by,
                mobile_country_code=mobile_country_code,
                check_user_id=user_id,
            )

            return result, aes_share_key, aes_nonce
        else:
            self.return_error(10004)


class InvestUserGetPictureVCodeSetEmailController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormateOutput(default_value=30050, return_type='return_error_by_header')
    def post(self):
        """
        发送验证码
        :return:
        """
        service = VcodeService()
        result, vcode_str = service.make_vcode_picture()
        resp = Response(result)
        service.set_vcode_picture(vcode_str, user_type=_USER_TYPE_INVEST, vcode_type=_VCODE_SET_EMAIL)
        return resp


class InvestUserSendSetEmailVCodeController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @AESOutput()
    @FormateOutput(default_value=30051, return_type='return_error')
    def post(self):
        """
        发送验证码
          :param user_mobile: 手机号码
        :return:
        """
        user_type = _USER_TYPE_INVEST
        if check_use_source(_USE_SOURCE_TYPE_1):
            argument_dict, aes_share_key, aes_nonce = self.get_argument_dict(
                must_keys=['user_id', 'email', 'pvcode'],
                api_type=user_type,
                request_type=_REQUEST_TYPE_LOGIN
            )

            user_id = str(argument_dict['user_id'])
            email = argument_dict['email']
            pvcode = argument_dict['pvcode']

            register_by = _REGISTER_SET_EMAIL

            send_type = _VCODE_SET_EMAIL
            vcode_service = VcodeService(aes_share_key=aes_share_key, aes_nonce=aes_nonce)

            # 校验图形验证码
            vcode_service.check_vcode_picture(pvcode, user_type=_USER_TYPE_INVEST, vcode_type=_VCODE_SET_EMAIL)

            # 校验是否已经注册
            result = vcode_service.send_vcode_by_register_type(
                send_type,
                email,
                user_type=user_type,
                register_by=register_by,
                check_user_id=user_id,
            )

            return result, aes_share_key, aes_nonce
        else:
            self.return_error(10004)


class InvestUserGetPictureVCodeResetPayPDController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormateOutput(default_value=30050, return_type='return_error_by_header')
    def post(self):
        """
        发送验证码
        :return:
        """
        service = VcodeService()
        result, vcode_str = service.make_vcode_picture()
        resp = Response(result)
        service.set_vcode_picture(vcode_str, user_type=_USER_TYPE_INVEST, vcode_type=_VCODE_RESET_PAY_PD)
        return resp


class InvestUserGetPictureVCodeSetPayPDController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormateOutput(default_value=30050, return_type='return_error_by_header')
    def post(self):
        """
        发送验证码
        :return:
        """
        service = VcodeService()
        result, vcode_str = service.make_vcode_picture()
        resp = Response(result)
        service.set_vcode_picture(vcode_str, user_type=_USER_TYPE_INVEST, vcode_type=_VCODE_SET_PAY_PD)
        return resp






