from controllers.base_controller import BaseController
from tools.decorator_tools import FormatOutput
from services.account_service import AccountService
from config import get_host_url


class AccountRechargeController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id', 'coin_id'])
        user_id = request_data['user_id']
        coin_id = request_data['coin_id']
        do_reset = request_data.get("do_reset", False)

        account_service = AccountService()
        result = account_service.apply_recharge(user_id, coin_id, do_reset)
        return result


class AccountWithdrawApplyController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(
            must_keys=['user_id', 'pay_password', 'coin_id', 'withdraw_amount', 'withdraw_fee', 'withdraw_address', 'source'],
            check_form_token=True
        )

        user_id = request_data['user_id']
        pay_password = request_data['pay_password']
        coin_id = request_data['coin_id']
        withdraw_amount = request_data['withdraw_amount']
        withdraw_fee = request_data['withdraw_fee']
        withdraw_address = request_data['withdraw_address']
        source = request_data['source']
        memo = request_data.get('memo', '')

        account_service = AccountService()
        # 校验支付密码
        account_service.check_pay_password(user_id, pay_password)

        result = account_service.apply_withdraw(user_id, coin_id, withdraw_amount, withdraw_fee, withdraw_address, source, memo=memo)
        return result


class AccountWaterController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=[
            'user_id',
        ])
        user_id = request_data['user_id']
        change_type = request_data.get("change_type", None)
        page_num = request_data.get("offset", 1)
        page_limit = request_data.get("limit", 10)
        start_id = request_data.get("start_id", None)

        account_service = AccountService()
        result = account_service.get_account_water(
            user_id,
            change_type=change_type,
            page_num=page_num,
            page_limit=page_limit,
            start_id=start_id
        )

        return self.utctime_to_localtime(result)


class AccountTokenWaterController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=[
            'user_id', 'coin_id'
        ])
        user_id = request_data['user_id']
        coin_id = str(request_data['coin_id'])
        page_num = request_data.get("offset", 1)
        page_limit = request_data.get("limit", 10)
        start_id = request_data.get("start_id", None)

        account_service = AccountService()
        result = account_service.get_account_token_water(
            user_id, coin_id, page_num, page_limit, start_id)

        return self.utctime_to_localtime(result)


class LotteryController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=[
            'user_id'
        ])
        user_id = request_data['user_id']

        account_service = AccountService()
        result = account_service.lottery(user_id)
        return result


class GetUserInviterCode(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=[
            'user_id'
        ])
        user_id = request_data['user_id']

        account_service = AccountService()
        result = account_service.get_inviter_code(user_id)
        return {
            "url": get_host_url() + '/login?inviter_code=' + result
        }


class UserWinningsController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        account_service = AccountService()
        result = account_service.get_user_winnings()
        return self.utctime_to_localtime(result)


class UserSetProfilePictureController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=[
            'user_id', 'profile_picture'
        ])
        user_id = request_data['user_id']
        profile_picture = request_data['profile_picture']
        account_service = AccountService()
        result = account_service.update_user_profile_picture(user_id, profile_picture)
        return result


class BgAccountWaterController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict()
        user_id = request_data.get("search_user_id", None)
        user_name = request_data.get("user_name", None)
        change_type = request_data.get("change_type", None)
        page_num = request_data.get("offset", 1)
        page_limit = request_data.get("limit", 10)
        token_id = request_data.get("token_id", None)
        water_id = request_data.get("water_id", None)
        finish_time_start = request_data.get("finish_time_start", None)
        finish_time_end = request_data.get("finish_time_end", None)

        account_service = AccountService()
        result = account_service.list_all_account_water(
            user_id=user_id,
            change_type=change_type,
            page_num=page_num,
            page_limit=page_limit,
            token_id=token_id,
            water_id=water_id,
            finish_time_start=finish_time_start,
            user_name=user_name,
            finish_time_end=finish_time_end,
        )

        return self.utctime_to_localtime(result)


class BgOperatingActivitiesController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict()
        user_name = request_data.get("user_name", None)
        inviter_code = request_data.get("inviter_code", None)
        invitee_code = request_data.get("invitee_code", None)
        change_type = request_data.get("change_type", None)
        page_num = request_data.get("offset", 1)
        page_limit = request_data.get("limit", 10)
        finish_time_start = request_data.get("finish_time_start", None)
        finish_time_end = request_data.get("finish_time_end", None)

        account_service = AccountService()
        result = account_service.get_operating_activities(
            user_name=user_name,
            inviter_code=inviter_code,
            invitee_code=invitee_code,
            change_type=change_type,
            page_num=page_num,
            page_limit=page_limit,
            finish_time_start=finish_time_start,
            finish_time_end=finish_time_end,
        )

        return self.utctime_to_localtime(result)
