# 投资用户相关
from decimal import Decimal

from flask import request

from controllers.base_controller import BaseController
from tools.decorator_tools import FormatOutput
from services.account_service import AccountService
from common_settings import *
from utils.util import get_intranet_IP


# 投资用户注册
class UserGenerateAccountController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self, inviter_code=None):
        request_data = self.get_argument_dict(must_keys=['user_id'])
        user_id = request_data['user_id']
        nick_name = request_data.get("nick_name", "")
        user_mobile = request_data.get("user_mobile", "")
        mobile_country_code = request_data.get("mobile_country_code", "")
        email = request_data.get("email", "")
        user_name = request_data.get("user_name", "")
        source = request_data.get("register_source", "")
        register_ip = request_data.get("register_ip", "")
        inviter_code = request_data.get("inviter_code", None)
        profile_picture = request_data.get("profile_picture", "")

        account_service = AccountService()
        result = account_service.user_generate_account(
            user_id,
            nick_name=nick_name,
            user_mobile=user_mobile,
            email=email,
            mobile_country_code=mobile_country_code,
            user_name=user_name,
            source=source,
            register_ip=register_ip,
            code=inviter_code,
            profile_picture=profile_picture
        )

        return result


class UserAccountInfoController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id'])
        account_service = AccountService()
        response_data = account_service.get_user_account_info(request_data['user_id'])
        return response_data


class UserGeneratePayKeySaltController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id'])
        account_service = AccountService()
        response_data = account_service.get_pay_salt(request_data['user_id'])
        return response_data


class UserResetPayPasswordController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id', 'password'])
        user_id = request_data['user_id']
        password = request_data['password']

        account_service = AccountService()
        response_data = account_service.reset_pay_password(user_id, password)
        return response_data


class UserNickNameController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id', 'nick_name'])
        user_id = request_data['user_id']
        nick_name = request_data['nick_name']

        account_service = AccountService()
        response_data = account_service.set_nick_name(user_id, nick_name)
        return response_data


class UserAvatarController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id', 'avatar'])
        user_id = request_data['user_id']
        avatar = request_data['avatar']

        account_service = AccountService()
        response_data = account_service.set_avatar(user_id, avatar)
        return response_data


class UserSetMobileController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id', 'user_mobile', 'mobile_country_code'])
        user_id = request_data['user_id']
        user_mobile = request_data['user_mobile']
        mobile_country_code = request_data['mobile_country_code']

        account_service = AccountService()
        response_data = account_service.set_mobile(user_id, user_mobile, mobile_country_code)
        return response_data


class UserSetEmailController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id', 'email'])
        user_id = request_data['user_id']
        email = request_data['email']

        account_service = AccountService()
        response_data = account_service.set_email(user_id, email)
        return response_data


class UserListController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict()

        # query information
        search_user_id = request_data.get("search_user_id", None)
        user_name = request_data.get("user_name", None)
        email = request_data.get("email", None)
        user_mobile = request_data.get("user_mobile", None)
        register_time_start = request_data.get("register_time_start", None)
        register_time_end = request_data.get("register_time_end", None)
        source = request_data.get("user_source", None)
        recharge_time_start = request_data.get("recharge_time_start", None)
        recharge_time_end = request_data.get("recharge_time_end", None)

        # page information
        page_num = request_data.get("offset", 1)
        page_limit = request_data.get("limit", 10)

        service = AccountService()
        result = service.get_user_list(
            search_user_id, user_name, email, user_mobile, register_time_start,
            register_time_end, source, recharge_time_start, recharge_time_end,
            page_num, page_limit)
        return self.utctime_to_localtime(result)


class UserTokenListController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict()

        # query information
        search_user_id = request_data.get("search_user_id", None)
        user_name = request_data.get("user_name", None)
        recharge_time_start = request_data.get("recharge_time_start", None)
        recharge_time_end = request_data.get("recharge_time_end", None)

        # page information
        page_num = request_data.get("offset", 1)
        page_limit = request_data.get("limit", 10)

        service = AccountService()
        result = service.get_user_token_list(
            search_user_id,
            user_name,
            page_num,
            page_limit,
            recharge_time_start=recharge_time_start,
            recharge_time_end=recharge_time_end
        )
        return result


class UserTokenDetailController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['check_user_id'])

        service = AccountService()
        result = service.get_user_token_detail(request_data["check_user_id"])
        return self.utctime_to_localtime(result)


# 投资用户登陆
class UserLoginController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id'])
        user_id = request_data['user_id']
        source = request_data.get("source", "")
        login_ip = request_data.get("login_ip", "")

        account_service = AccountService()
        result = account_service.user_login(
            user_id,
            source=source,
            login_ip=login_ip,
        )

        return result


# OTC 充值
class UserAddTokenController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(
            must_keys=['user_id', 'token_id', 'price', 'random_key'])
        user_id = request_data['user_id']
        token_id = request_data["token_id"]
        price = request_data["price"]
        random_key = request_data["random_key"]

        if not isinstance(price, str):
            return {
                "status": False,
                "debugmsg": "price 类型有误"
            }

        if request.remote_addr != get_intranet_IP():
            return {
                "status": False,
                "debugmsg": "ip 不可用"
            }
        if random_key != "b20a0f6923b3bb57f4535190aeec8434":
            return {
                "status": False,
                "debugmsg": "random key 有误"
            }

        price_decimal = Decimal(price)
        account_service = AccountService()
        result = account_service.user_account_add_token(
            user_id=user_id,
            token_id=token_id,
            price=price_decimal
        )

        return result
