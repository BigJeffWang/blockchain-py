from controllers.base_controller import BaseController
from services.wallet_foreign_service import WalletForeignService
from services.wallet_withdraw_service import WalletWithdrawService
from services.wallet_gather_service import WalletGatherService

from tools.decorator_tools import FormatOutput


# 提现、归集后台
class WithdrawController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        return


# 提现列表
class WithdrawListController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        data = self.get_argument_dict()
        service = WalletWithdrawService()
        result = service.withdraw_list(data.get("coin_id"), data.get("withdraw_type"), data.get("withdraw_status"),
                                       data.get("audit_status"), data.get("source_status"), data.get("user_name"),
                                       data.get("withdraw_number"), data.get("apply_time_start"),
                                       data.get("apply_time_end"), data.get("from_address"),
                                       data.get("transfer_time_start"), data.get("transfer_time_end"),
                                       data.get("offset"),
                                       data.get("limit"), data.get("page_flag"))
        return self.utctime_to_localtime(result)


# 提现审核页面
class WithdrawApplyController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        data = self.get_argument_dict()
        service = WalletWithdrawService()
        result = service.withdraw_apply(data.get("order_no"))
        return self.utctime_to_localtime(result)


# 用户提现流水
class UserRecordController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        data = self.get_argument_dict()
        service = WalletWithdrawService()
        result = service.get_account_water(data.get("account_id"), data.get("start_at"), data.get("end_at"),
                                           data.get("coin_id"), data.get("change_type"), data.get("address"),
                                           page_num=data.get("offset"),
                                           page_limit=data.get("limit"))
        return result


# 提现审核
class AuditWithdrawController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        data = self.get_argument_dict()
        service = WalletWithdrawService()
        result = service.audit_withdraw(data.get("order_no"), data.get("audit_status"),
                                        data.get("remark"), data.get("audit_user"))
        return result


# 提现操作
class OperationWithdrawController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        data = self.get_argument_dict()
        service = WalletWithdrawService()
        result = service.operation_withdraw(data.get("order_nos"), data.get("source_status"), data.get("from_address"),
                                            data.get("verification_code"), data.get("coin_id"))
        return result


# 线下提现录入tx
class OfflineTxController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        data = self.get_argument_dict()
        service = WalletWithdrawService()
        result = service.offline_tx(data.get("order_no"), data.get("from_address"), data.get("txid"),
                                    data.get("transfer_at"), data.get("coin_id"), data.get("operation_user"))
        return result


# 查看提现详情
class WithdrawDetailsController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        data = self.get_argument_dict()
        service = WalletWithdrawService()
        result = service.withdraw_details(data.get("order_no"))
        return self.utctime_to_localtime(result)


#############################################################
# 归集地址列表
class GatherAddressListController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        data = self.get_argument_dict()
        service = WalletGatherService()
        result = service.gather_address_list(data.get("sub_public_address"), data.get("coin_id"),
                                             data.get("update_at_start"), data.get("update_at_end"),
                                             data.get("status"), data.get("offset"),
                                             data.get("limit"))
        return self.utctime_to_localtime(result)


# 归集地址流水
class GatherAddressRecordController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        data = self.get_argument_dict()
        service = WalletGatherService()
        result = service.gather_address_record(data.get("sub_public_address"), data.get("relevant_address"),
                                               data.get("transfer_at_start"),
                                               data.get("transfer_at_end"), data.get("operation_type"),
                                               data.get("offset"), data.get("limit"))
        return self.utctime_to_localtime(result)


# 子账户地址列表
class SubAddressListController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        data = self.get_argument_dict()
        service = WalletGatherService()
        result = service.sub_address_list(data.get("user_name"), data.get("sub_public_address"),
                                          data.get("conditions"), data.get("coin_id"),
                                          data.get("offset"), data.get("limit"))
        return result


# 归集操作
class OperationGatherController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        data = self.get_argument_dict()
        service = WalletGatherService()
        result = service.operation_gather(data.get("user_name"), data.get("sub_public_address"),
                                          data.get("conditions"), data.get("coin_id"),
                                          data.get("to_address"), data.get("verification_code"))
        return result


# 归集操作记录
class GatherRecordController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        data = self.get_argument_dict()
        service = WalletGatherService()
        result = service.gather_record(data.get("public_address"), data.get("coin_id"),
                                       data.get("operate_at_start"), data.get("operate_at_end"),
                                       data.get("offset"), data.get("limit"))
        return self.utctime_to_localtime(result)


# 归集操作记录详情
class GatherRecordDetailsController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        data = self.get_argument_dict()
        service = WalletGatherService()
        result = service.gather_record_details(data.get("record_id"), data.get("user_name"), data.get("from_address"),
                                               data.get("operate_at_start"), data.get("operate_at_end"),
                                               data.get("withdraw_status"),
                                               data.get("confirm_at_start"), data.get("confirm_at_end"),
                                               data.get("offset"), data.get("limit"))
        return self.utctime_to_localtime(result)


# 全部归集操作记录详情
class GatherRecordAllController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        data = self.get_argument_dict()
        service = WalletGatherService()
        result = service.gather_record_all(data.get("user_name"), data.get("from_address"),
                                           data.get("operate_at_start"), data.get("operate_at_end"),
                                           data.get("withdraw_address"), data.get("coin_id"),
                                           data.get("confirm_at_start"), data.get("confirm_at_end"),
                                           data.get("withdraw_status"), data.get("offset"), data.get("limit"))
        return self.utctime_to_localtime(result)


# 归集转归集
class GatherToGatherController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        data = self.get_argument_dict()
        service = WalletGatherService()
        result = service.gather_to_gather(data.get("coin_id"), data.get("from_address"),
                                          data.get("amount"), data.get("to_address"),
                                          data.get("verification_code"))
        return result


# ETH追加手续费
class AppendGasController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        data = self.get_argument_dict()
        service = WalletForeignService()
        result = service.append_gas(data.get("order_no"), data.get("verification_code"))
        return result


# 发送邮箱验证码
class SendCodeController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        data = self.get_argument_dict()
        service = WalletForeignService()
        result = service.send_code()
        return result


# app获取提现手续费接口
class GetGasController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        data = self.get_argument_dict()
        service = WalletForeignService()
        result = service.get_gas(data.get("coin_id"), data.get("user_id"), data.get("token_id"))
        print("result===============")
        print(result)
        return result


# 断提现地址是否为平台地址
class CheckAddressController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        data = self.get_argument_dict()
        service = WalletForeignService()
        result = service.check_address(data.get("coin_id"), data.get("user_id"), data.get("address"))
        return result


# 游戏数据统计
class GameStatisticalController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        service = WalletForeignService()
        return service.game_statistical()


# 用户数据分析
class UserStatisticalController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        service = WalletForeignService()
        return service.user_statistical()
