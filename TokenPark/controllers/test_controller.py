from controllers.base_controller import BaseController
from tools.decorator_tools import FormatOutput
from config import get_config, get_env
from tools.mysql_tool import MysqlTools
from utils.util import get_decimal
from utils.log import raise_logger
from services.test_service import TestService


class TestController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # @FormatOutput()
    def get(self):
        result = "this is test"
        if get_env() != 'dev':
            return result
        """
        self.return_error(10000)
        """

        # from services.account_service import AccountService
        # account_service = AccountService()
        # with MysqlTools().session_scope() as session:
        #     print('***')
            # 实现真正对充值
            # result = account_service.do_recharge(session, '2018111309375761185989916621239257168264426978617039743301831998', 1, 1, 123, 123)
            # if result == 0:
            #     session.commit()
            # else:
            #     self.return_error(result)

            # 获取账户信息对接口
            # result = account_service.get_inner_user_account_info(session, 'b7996c045505422c8a44155a19f49e12')

            # 获取用户对应币种的余额
            # result = account_service.get_inner_user_account_by_token(session, 'b7996c045505422c8a44155a19f49e12', 1)

            # 用户下注
            # result = account_service.do_bet(session, 'b7996c045505422c8a44155a19f49e12', 1, get_decimal('0.1'), '123')
            # session.commit()

            # 用户赢钱
            # result = account_service.do_win(session, 'b7996c045505422c8a44155a19f49e12', 1, get_decimal('0.1'), '123')
            # session.commit()

            # 获取用户信息列表对接口
            # result = account_service.get_user_account_info_list(session, ['7507a61d22f64ae29b9ce36585bcc289', '7507a61d22f64ae29b9ce36585bcc287'])

        # 校验交易密码, 如果是测试环境则111111为必过密码！！！！
        # result = account_service.check_pay_password('b7996c045505422c8a44155a19f49e12', '$2a$12$wYNR0BQN5EXqNZy.57OLMuR/rSe75.XlZsOupEPG14HRgbNzs1s4W')

        # 提现申请
        # result = account_service.apply_withdraw('7507a61d22f64ae29b9ce36585bcc289', '1', get_decimal('0.1'), get_decimal('0.01'), '123456')
        # 提现结果实施
        # result = account_service.do_withdraw('20181113153610545304913763198044', '456789', '6')

        # 账户流水
        # result = account_service.get_account_water('7507a61d22f64ae29b9ce36585bcc289', change_type='999', page_limit='3', page_num='2')

        # from services.wallet_withdraw_service import WalletWithdrawService
        # wallet_withdraw_service = WalletWithdrawService()
        # result = wallet_withdraw_service.get_account_water('2018111309375761185989916621239257168264426978617039743301831998')

        # from services.vcode_service import VcodeService
        # vcode_service = VcodeService()
        # result = vcode_service.send_vcode_by_email('gather')
        # result = vcode_service.check_sms_email_vcode('gather', 'AHGmiMWo')

        return result

    @FormatOutput()
    def post(self):
        TestService().testing()
        # self.return_error(10000)
        a = [0, 1]
        print(a[2])
        # raise Exception("test log ")
        from models.token_node_conf_model import TokenNodeConfModel
        with MysqlTools().session_scope() as session:
            session.query(TokenNodeConfModel).all()
            session.commit()
        args = self.get_argument_dict()
        print(args)
        import datetime
        args["expect_at"] = str(datetime.datetime.utcnow()).split(".")[0]
        print(args["expect_at"])
        return self.utctime_to_localtime(args)

    def test_log(self):
        raise_logger("this is test", log_name='wallet', lv="info")
        raise_logger("this is test error ", log_name='wallet', lv="error")


if __name__ == "__main__":
    TestController().test_log()





