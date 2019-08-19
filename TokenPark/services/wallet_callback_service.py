from services.base_service import BaseService
from services.account_service import AccountService
from utils.util import get_decimal, send_aws_sms, coin_id_to_name, decimal_to_client
from common_settings import *
from tools.mysql_tool import MysqlTools
from models.user_account_model import UserAccountModel
from models.foreign_withdraw_order_record_model import ForeignWithdrawOrderRecordModel
from utils.log import raise_logger


class WalletCallbackService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def format_callback_result(result):
        if result is True:
            return _ZERO_S
        elif result is False:
            return ""
        elif result is None:
            return ""
        else:
            return str(result)

    # 充值到账回调
    @staticmethod
    def recharge_notify_callback(account_id, token_amount, coin_id, token_address, transaction_id):
        print("account_id, token_amount, coin_id, token_address, transaction_id ==")
        print(account_id, token_amount, coin_id, token_address, transaction_id)

        try:
            with MysqlTools().session_scope() as session:
                user_account = session.query(UserAccountModel).filter(UserAccountModel.account_id == account_id).first()
            content = "［LuckyPark］您本次充值" + decimal_to_client(token_amount) + coin_id_to_name(
                coin_id) + "，已成功到账。                                                                                                                             "
            send_aws_sms(user_account.user_mobile, content)
        except Exception as e:
            raise_logger("do_recharge err!!! duan xin!!!" + str(e), "wallet", "error")

        try:
            with MysqlTools().session_scope() as recharge_session:
                do_recharge_res = AccountService().do_recharge(recharge_session, account_id, token_amount, coin_id, token_address,
                                                               transaction_id)
                ret = WalletCallbackService.format_callback_result(do_recharge_res)
                recharge_session.commit()
            return ret
        except Exception as e:
            raise_logger("do_recharge err!!!" + str(e), "wallet", "error")
            return ""

    # 提现到账回调
    @staticmethod
    def withdraw_notify_callback(account_change_record_id, transaction_id, withdraw_result,
                                 withdraw_actual_amount, withdraw_actual_fee, withdraw_remain_fee=get_decimal("0")):
        """
        :param account_change_record_id: req_no
        :param transaction_id: order_no
        :param withdraw_result: "4" online "7" offline
        :param withdraw_actual_amount:
        :param withdraw_actual_fee:
        :param withdraw_remain_fee:
        :return:
        """
        print(
            "account_change_record_id, transaction_id, withdraw_result, withdraw_actual_amount, withdraw_actual_fee, withdraw_remain_fee ==")
        print((account_change_record_id, transaction_id, withdraw_result, withdraw_actual_amount, withdraw_actual_fee,
               withdraw_remain_fee))

        try:
            with MysqlTools().session_scope() as session:
                foreign_withdraw_order_record = session.query(ForeignWithdrawOrderRecordModel).filter(
                    ForeignWithdrawOrderRecordModel.order_no == transaction_id).first()
                user_account = session.query(UserAccountModel).filter(
                    UserAccountModel.account_id == foreign_withdraw_order_record.account_id).first()
            content = "［LuckyPark］您本次提现" + decimal_to_client(withdraw_actual_amount) + coin_id_to_name(
                foreign_withdraw_order_record.coin_id) + "，手续费" + decimal_to_client(
                withdraw_actual_fee) + "，请查收。                                                                                                                             "
            send_aws_sms(user_account.user_mobile, content)
        except Exception as e:
            raise_logger("do_withdraw err!!! duan xin!!!" + str(e), "wallet", "error")

        try:
            with MysqlTools().session_scope() as withdraw_session:
                do_withdraw_res = AccountService().do_withdraw(account_change_record_id, transaction_id, withdraw_result,
                                                               withdraw_actual_amount, withdraw_actual_fee,
                                                               withdraw_remain_fee, withdraw_session)
                ret = WalletCallbackService.format_callback_result(do_withdraw_res)
                withdraw_session.commit()
            return ret
        except Exception as e:
            raise_logger("do_withdraw err!!!" + str(e), "wallet", "error")
            return ""
