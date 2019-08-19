import random
from decimal import Decimal
import logging

from services.base_service import BaseService
from tools.mysql_tool import MysqlTools
from common_settings import *
from models.user_account_model import UserAccountModel
from models.user_account_token_model import UserAccountTokenModel
from models.token_coin_model import TokenCoinModel
from models.account_recharge_record_model import AccountRechargeRecordModel
from models.account_change_record_model import AccountChangeRecordModel
from models.account_withdraw_record_model import AccountWithdrawRecordModel
from models.wallet_btc_model import WalletBtcModel
from models.wallet_eth_model import WalletEthModel
from models.wallet_eos_model import WalletEosModel
from utils.util import get_decimal, decimal_to_client, get_offset_by_page, get_page_by_offset
from services.wallet_foreign_service import WalletForeignService
import time
import datetime
from utils.crypto_utils import get_bcrypt_salt, urandom, sha512, slow_is_equal
from utils.exchange_rate_util import get_exchange_rate
from config import get_env
from sqlalchemy import desc
from models.account_login_message_model import AccountLoginMessageModel
from models.robot_account_model import RobotAccountModel

SOURCE_LIST = {
    1: "pc",
    2: "wap",
    3: "iphone",
    4: "android"
}

BITCOIN_LIST = ['BTC', 'ETH']

COIN_SHOW_LIST = ['USDT', 'ETH', 'BTC', 'USDT_EXPERIENCE', 'EOS']

USDT_EXPERIENCE_NAME = 'USDT_EXPERIENCE'

USDT_EXPERIENCE_ID = '236'

bitcoin_min_price = {
    "60": 0.05,
    "0": 0.001,
    "194": 1
}


class AccountService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # 生成下一个邀请码
    @staticmethod
    def generate_inviter_code(inviter_code):
        code_int = int(inviter_code, 16)
        code_next_int = code_int + 1
        code_next_hex = format(code_next_int, 'x')
        return code_next_hex.zfill(6)

    def user_generate_account(self, user_id, code, nick_name="", user_mobile="", email="", mobile_country_code="",
                              user_name="",
                              source=UserAccountModel.source_type_1, score=_NEW_USER_SCORE, user_type=_USER_TYPE_INVEST,
                              register_ip="", profile_picture=""):
        """
        创建账户
        :param user_id:
        :param nick_name:
        :param user_mobile:
        :param email:
        :param mobile_country_code:
        :param score:
        :param user_type:
        :return:
        """

        with MysqlTools().session_scope() as session:

            if user_type == _USER_TYPE_INVEST:
                user_model = UserAccountModel
                user = session.query(user_model).filter(user_model.user_id == user_id,
                                                        user_model.deleted == False, ).first()
            else:
                self.return_error(10017)

            # 1.0 判断用户是否存在,如果已经存在则用户已经注册
            if user:
                self.return_error(20018)

            logging.info('用户 ' + user_id + ' 不存在')
            # 查询目前最大的邀请码
            user_code = session.query(
                UserAccountModel.inviter_code
            ).filter(
                UserAccountModel.deleted == False
            ).order_by(
                UserAccountModel.inviter_code.desc()
            ).first()
            # 生成邀请码
            if user_code.inviter_code:
                inviter_code = 'LK' + self.generate_inviter_code(user_code.inviter_code.split('K')[1])
            else:
                inviter_code = 'LK000001'

            logging.info('生成的验证码为 ' + inviter_code)
            logging.info('+' * 20)
            logging.info('用户类型为 ' + str(user_type))
            logging.info('邀请码为 ' + str(code))

            if user_type == _USER_TYPE_INVEST:
                if not code:
                    user = UserAccountModel(
                        user_id=user_id,
                        score=score,
                        nick_name=nick_name,
                        user_mobile=user_mobile,
                        email=email,
                        mobile_country_code=mobile_country_code,
                        user_name=user_name,
                        source=source,
                        register_ip=register_ip,
                        inviter_code=inviter_code,
                        profile_picture=profile_picture
                    )
                    session.add(user)
                    session.commit()
                else:
                    user = UserAccountModel(
                        user_id=user_id,
                        score=score,
                        nick_name=nick_name,
                        user_mobile=user_mobile,
                        email=email,
                        mobile_country_code=mobile_country_code,
                        user_name=user_name,
                        source=source,
                        register_ip=register_ip,
                        inviter_code=inviter_code,
                        invitee_code=code,
                        profile_picture=profile_picture
                    )
                    session.add(user)
                    session.commit()

                    logging.info('用户注册成功')

                    # 添加邀请人 usdt 体验金
                    # 校验 code 是否存在，如果不存在，返回错误，如果存在，添加邀请人体验金
                    # 金额和记录
                    q = session.query(
                        UserAccountModel
                    ).filter(
                        UserAccountModel.inviter_code == code,
                        UserAccountModel.deleted == False,
                    ).first()

                    if not q:
                        self.return_error(30041)

                    # 如果用户为被邀请用户，给邀请人奖励 usdt
                    now_time = datetime.datetime.utcnow()

                    user_q = session.query(
                        UserAccountModel.account_id
                    ).filter(
                        UserAccountModel.inviter_code == code,
                        UserAccountModel.deleted == False,
                        UserAccountModel.status == UserAccountModel.status_on
                    ).first()

                    user_token_q = session.query(
                        UserAccountTokenModel
                    ).filter(
                        UserAccountTokenModel.account_id == user_q.account_id,
                        UserAccountTokenModel.token_id == USDT_EXPERIENCE_ID
                    ).with_for_update().first()
                    balance = float(user_token_q.balance)
                    user_token_q.recharge(1)
                    session.commit()

                    logging.info('修改用户金额成功')

                    # 添加记录
                    account_change_record = AccountChangeRecordModel(
                        account_id=user_q.account_id,
                        token_id=USDT_EXPERIENCE_ID,
                        change_type=AccountChangeRecordModel.change_type_22,
                        change_amount=1,
                        balance=balance + 1,
                        frozon_amount=0,
                        investment_amount=0,
                        account_token_id=user_token_q.account_token_id,
                        begin_time=now_time,
                        finish_time=now_time,
                    )
                    session.add(account_change_record)
                    session.commit()

                    logging.info('添加用户记录成功')

            else:
                self.return_error(10017)

            return {
                "status": "true"
            }

    def get_user_account_info(self, user_id, user_type=_USER_TYPE_INVEST):
        """
        获取用户详情
        :param user_id:
        :param user_type:
        :return:
        """
        result_dict = {
            'score': 0,
            'transaction_password': '',
            'nick_name': '',
            'avatar': '',
            'user_name': '',
            'total_account': decimal_to_client('0'),
            'first_recharge': 0,
            'account': {
                "BTC": {
                    'coin_id': "0",
                    'coin_name': "BTC",
                    'coin_des': "Bitcoin",
                    'total_recharge': decimal_to_client('0'),
                    'total_withdraw': decimal_to_client('0'),
                    'total_withdraw_fee': decimal_to_client('0'),
                    'balance': decimal_to_client('0'),
                    'balance_USDT': decimal_to_client('0', digits=2),
                    'frozon_amount': decimal_to_client('0'),
                    'investment_amount': decimal_to_client('0'),
                },
                "ETH": {
                    'coin_id': "60",
                    'coin_name': "ETH",
                    'coin_des': "Ether",
                    'total_recharge': decimal_to_client('0'),
                    'total_withdraw': decimal_to_client('0'),
                    'total_withdraw_fee': decimal_to_client('0'),
                    'balance': decimal_to_client('0'),
                    'balance_USDT': decimal_to_client('0', digits=2),
                    'frozon_amount': decimal_to_client('0'),
                    'investment_amount': decimal_to_client('0'),
                },
                "EOS": {
                    'coin_id': "194",
                    'coin_name': "EOS",
                    'coin_des': "EOS",
                    'total_recharge': decimal_to_client('0'),
                    'total_withdraw': decimal_to_client('0'),
                    'total_withdraw_fee': decimal_to_client('0'),
                    'balance': decimal_to_client('0'),
                    'balance_USDT': decimal_to_client('0', digits=2),
                    'frozon_amount': decimal_to_client('0'),
                    'investment_amount': decimal_to_client('0'),
                },
                "USDT_EXPERIENCE": {
                    'coin_id': "236",
                    'coin_name': "USDT 体验金",
                    'coin_des': "USDT_EXPERIENCE",
                    'total_recharge': decimal_to_client('0'),
                    'total_withdraw': decimal_to_client('0'),
                    'total_withdraw_fee': decimal_to_client('0'),
                    'balance': '0.0000',
                    'balance_USDT': decimal_to_client('0', digits=2),
                    'frozon_amount': decimal_to_client('0'),
                    'investment_amount': decimal_to_client('0'),
                },
                "USDT": {
                      'coin_id': "100000000",
                      'coin_name': "USDT",
                      'coin_des': "USDT",
                      'total_recharge': decimal_to_client('0', digits=4),
                      'total_withdraw': decimal_to_client('0', digits=4),
                      'total_withdraw_fee': decimal_to_client('0', digits=4),
                      'balance': '0.0000',
                      'balance_USDT': decimal_to_client('0', digits=4),
                      'frozon_amount': decimal_to_client('0', digits=4),
                      'investment_amount': decimal_to_client('0', digits=4),
                }
            },
        }

        with MysqlTools().session_scope() as session:

            if user_type == _USER_TYPE_INVEST:
                user_model = UserAccountModel
                token_model = UserAccountTokenModel
                user = session.query(user_model).filter(user_model.user_id == user_id,
                                                        user_model.deleted == False, ).first()
            else:
                return result_dict

            # 1.0 判断用户是否存在,如果已经存在则用户已经注册
            if not user:
                return result_dict

            result_dict['score'] = user.score
            result_dict['transaction_password'] = '******' if user.transaction_password else ''
            result_dict['nick_name'] = user.nick_name
            result_dict['avatar'] = user.avatar
            result_dict['user_name'] = user.user_name
            result_dict['profile_picture'] = user.profile_picture if user.profile_picture else ""
            if user.first_recharge_at != "0000-00-00 00:00:00":
                result_dict['first_recharge'] = 1

            user_token = session.query(
                token_model.total_recharge,
                token_model.total_withdraw,
                token_model.total_withdraw_fee,
                token_model.balance,
                token_model.frozon_amount,
                token_model.investment_amount,
                TokenCoinModel
            ).outerjoin(
                TokenCoinModel, token_model.token_id == TokenCoinModel.coin_id
            ).filter(
                token_model.user_id == user_id,
                token_model.deleted == False,
                token_model.account_id == user.account_id,
                TokenCoinModel.deleted == False,
            ).all()

            if user_token is not None:
                # Set total balance
                TOTAL_BALANCE = Decimal(0)
                for one_token in user_token:
                    if one_token.TokenCoinModel.coin_name in result_dict['account']:
                        result_dict['account'][one_token.TokenCoinModel.coin_name] = {
                            'coin_id': one_token.TokenCoinModel.coin_id,
                            'coin_name': one_token.TokenCoinModel.coin_name,
                            'coin_des': one_token.TokenCoinModel.coin_des,
                            'total_recharge': decimal_to_client(one_token.total_recharge),
                            'total_withdraw': decimal_to_client(one_token.total_withdraw),
                            'total_withdraw_fee': decimal_to_client(one_token.total_withdraw_fee),
                            'balance': decimal_to_client(one_token.balance),
                            'frozon_amount': decimal_to_client(one_token.frozon_amount),
                            'investment_amount': decimal_to_client(one_token.investment_amount),
                        }

                        # compute USDT price
                        if one_token.TokenCoinModel.coin_id == '236':
                            USDT_exchange_str = '0'
                            result_dict['account'][one_token.TokenCoinModel.coin_name]['balance'] = decimal_to_client(one_token.balance, digits=4)
                            result_dict['account'][one_token.TokenCoinModel.coin_name]['coin_name'] = "USDT 体验金"
                        elif one_token.TokenCoinModel.coin_id == _COIN_ID_USDT:
                            USDT_exchange_str = '1'
                            result_dict['account'][one_token.TokenCoinModel.coin_name]['balance'] = decimal_to_client(one_token.balance, digits=4)
                        else:
                            USDT_exchange_str = get_exchange_rate(one_token.TokenCoinModel.coin_id)['price']
                        USDT_exchange_decimal = Decimal(USDT_exchange_str) * one_token.balance
                        TOTAL_BALANCE += USDT_exchange_decimal
                        result_dict['account'][one_token.TokenCoinModel.coin_name]['balance_USDT'] = decimal_to_client(
                            USDT_exchange_decimal, digits=2)
                result_dict['total_account'] = decimal_to_client(TOTAL_BALANCE, digits=2)
            return result_dict

    def apply_recharge(self, user_id, coin_id, do_reset=False):
        """
        获取充值地址
        :param user_id:
        :param coin_id:
        :param do_reset: 是否重置地址
        :return:
        """
        with MysqlTools().session_scope() as session:
            user_model = UserAccountModel
            user = session.query(user_model).filter(
                user_model.user_id == user_id,
                user_model.deleted == False,
                user_model.status == user_model.status_on,
            ).first()
            if not user:
                self.return_error(35005)

            account_id = user.account_id

            one_token_msg = session.query(TokenCoinModel).filter(
                TokenCoinModel.coin_id == coin_id,
            ).first()

            if not one_token_msg:
                self.return_error(35017)

            coin_name = one_token_msg.coin_name
            one_account_token = session.query(UserAccountTokenModel).filter(
                UserAccountTokenModel.account_id == user.account_id,
                UserAccountTokenModel.user_id == user_id,
                UserAccountTokenModel.token_id == coin_id,
                UserAccountTokenModel.status == UserAccountTokenModel.status_on,
                UserAccountTokenModel.deleted == False,
            ).first()

            if one_account_token is None:
                one_account_token = UserAccountTokenModel(
                    account_id=user.account_id,
                    user_id=user.user_id,
                    token_id=coin_id,
                    balance=get_decimal('0.000000000000000000', digits=18),
                )
                address_result = WalletForeignService().assign_account_addresses({
                    'account_id': account_id,
                    'coin_id': coin_id,
                    'reset': '',
                })
                if isinstance(address_result, int) and address_result != 0:
                    self.return_error(address_result)
                # one_account_token.sub_public_address = address_result['address']
                one_account_token.sub_public_address = address_result.get("address", "")
                one_account_token.memo = address_result.get('memo', '')
                session.add(one_account_token)
            elif not one_account_token.sub_public_address:
                # 获取地址
                address_result = WalletForeignService().assign_account_addresses({
                    'account_id': account_id,
                    'coin_id': coin_id,
                    'reset': '',
                })
                if isinstance(address_result, int) and address_result != 0:
                    self.return_error(address_result)
                one_account_token.sub_public_address = address_result.get("address", "")
                one_account_token.memo = address_result.get('memo', '')
            session.commit()

            if coin_id == USDT_EXPERIENCE_ID:
                coin_name = 'USDT 体验金'
            return {
                'token_address': one_account_token.sub_public_address,
                'memo': one_account_token.memo,
                'coin_name': coin_name,
                'coin_id': coin_id,
                'balance': decimal_to_client(one_account_token.balance),
                'balance_USDT': decimal_to_client(
                    one_account_token.balance * Decimal(get_exchange_rate(coin_id)['price']),
                    digits=2),
            }

    def do_recharge(self, session, account_id, token_amount, coin_id,
                    token_address, transaction_id, source=None, memo=""):
        """
        实现充值功能
        :param session: 事物session
        :param account_id: 账户id
        :param token_amount: 金额
        :param coin_id: 币种
        :param token_address: 充值地址
        :param transaction_id: 交易号
        :param source 来源
        :param memo
        :return:
        """

        token_amount = get_decimal(token_amount, digits=18, decimal_type='up')
        if token_amount < 0:
            return 35018

        one_account = session.query(UserAccountModel).filter(
            UserAccountModel.account_id == account_id,
            UserAccountModel.deleted == False,
            UserAccountModel.status == UserAccountModel.status_on,
        ).with_for_update().first()

        if not one_account:
            return 35005

        one_account_token = session.query(UserAccountTokenModel).filter(
            UserAccountTokenModel.account_id == one_account.account_id,
            UserAccountTokenModel.user_id == one_account.user_id,
            UserAccountTokenModel.token_id == coin_id,
            UserAccountTokenModel.status == UserAccountTokenModel.status_on,
            UserAccountTokenModel.deleted == False,
        ).with_for_update().first()

        if not one_account_token:
            with MysqlTools().session_scope() as session1:
                one_account_token = UserAccountTokenModel(
                    account_id=one_account.account_id,
                    user_id=one_account.user_id,
                    token_id=coin_id,
                )
                session1.add(one_account_token)
                session1.commit()

                # 修改用户账户金额
                account_q = session1.query(
                    UserAccountTokenModel
                ).filter(
                    UserAccountTokenModel.account_id == one_account.account_id,
                    UserAccountTokenModel.user_id == one_account.user_id,
                    UserAccountTokenModel.token_id == coin_id,
                    UserAccountTokenModel.status == UserAccountTokenModel.status_on,
                    UserAccountTokenModel.deleted == False,
                ).with_for_update().first()
                recharge_result = account_q.recharge(token_amount)
                if not recharge_result:
                    return 35020
                session1.commit()
        else:
            recharge_result = one_account_token.recharge(token_amount)
            if not recharge_result:
                return 35020
            session.commit()

        now_time = datetime.datetime.utcnow()

        if source:
            one_account_change_record = AccountChangeRecordModel(
                account_id=one_account.account_id,
                token_id=one_account_token.token_id,
                change_type=AccountChangeRecordModel.change_type_1,
                change_amount=token_amount,
                balance=one_account_token.balance,
                frozon_amount=one_account_token.frozon_amount,
                investment_amount=one_account_token.investment_amount,
                account_token_id=one_account_token.account_token_id,
                token_address=token_address,
                memo=memo,
                begin_time=now_time,
                finish_time=now_time,
                transaction_id=transaction_id,
                source=source
            )
            session.add(one_account_change_record)
            session.commit()

            one_account_recharge_record = AccountRechargeRecordModel(
                account_id=one_account.account_id,
                user_id=one_account_token.token_id,
                account_change_record_id=one_account_change_record.account_change_record_id,
                token_address=token_address,
                memo=memo,
                receive_token=token_amount,
                transaction_id=transaction_id,
                token_id=coin_id,
                status=AccountRechargeRecordModel.status_2,
                begin_time=now_time,
                finish_time=now_time,
                total_recharge=one_account_token.total_recharge,
                total_withdraw=one_account_token.total_withdraw,
                total_withdraw_fee=one_account_token.total_withdraw_fee,
                balance=one_account_token.balance,
                frozon_amount=one_account_token.frozon_amount,
                investment_amount=one_account_token.investment_amount,
                source=source
            )
            session.add(one_account_recharge_record)
            session.commit()

            logging.info('+' * 20 + ' 520')

            if one_account.first_recharge_at == '0000-00-00 00:00:00':
                one_account.first_recharge_at = now_time
                session.commit()

                # 首充奖励
                with MysqlTools().session_scope() as session2:
                    account_token_q = session2.query(
                        UserAccountTokenModel
                    ).filter(
                        UserAccountTokenModel.account_id == one_account.account_id,
                        UserAccountTokenModel.user_id == one_account.user_id,
                        UserAccountTokenModel.token_id == USDT_EXPERIENCE_ID,
                        UserAccountTokenModel.status == UserAccountTokenModel.status_on,
                        UserAccountTokenModel.deleted == False,
                    ).with_for_update().first()

                    balance = float(account_token_q.balance)
                    account_token_q.recharge(10)
                    session2.commit()

                    account_change_record = AccountChangeRecordModel(
                        account_id=account_token_q.account_id,
                        token_id=account_token_q.token_id,
                        change_type=AccountChangeRecordModel.change_type_21,
                        change_amount=10,
                        balance=balance + 10,
                        frozon_amount=0,
                        investment_amount=0,
                        account_token_id=account_token_q.account_token_id,
                        begin_time=now_time,
                        finish_time=now_time,
                    )
                    session2.add(account_change_record)
                    session2.commit()

                    # --------------------------------------------------------------
                    #                              邀请充值
                    # 判断是否为邀请注册用户
                    #        |
                    #        |—————————> 不做任何修改
                    #    yes |     no
                    #        v
                    #  邀请人的 usdt 奖励金 += 5
                    # --------------------------------------------------------------
                    if one_account.invitee_code:
                        # 根据受邀请码反查邀请人
                        inviter = session2.query(
                            UserAccountModel
                        ).filter(
                            UserAccountModel.inviter_code == one_account.invitee_code,
                            UserAccountModel.deleted == False,
                            UserAccountModel.status == UserAccountModel.status_on,
                        ).first()

                        # 增加邀请人的 usdt 奖励金
                        inviter_token_q = session2.query(
                            UserAccountTokenModel
                        ).filter(
                            UserAccountTokenModel.account_id == inviter.account_id,
                            UserAccountTokenModel.user_id == inviter.user_id,
                            UserAccountTokenModel.token_id == USDT_EXPERIENCE_ID,
                            UserAccountTokenModel.status == UserAccountTokenModel.status_on,
                            UserAccountTokenModel.deleted == False,
                        ).with_for_update().first()

                        balance_23 = float(inviter_token_q.balance)
                        inviter_token_q.recharge(5)
                        session2.commit()

                        account_change_record_23 = AccountChangeRecordModel(
                            account_id=inviter_token_q.account_id,
                            token_id=inviter_token_q.token_id,
                            change_type=AccountChangeRecordModel.change_type_23,
                            change_amount=5,
                            balance=balance_23 + 5,
                            frozon_amount=0,
                            investment_amount=0,
                            account_token_id=inviter_token_q.account_token_id,
                            begin_time=now_time,
                            finish_time=now_time,
                        )
                        session2.add(account_change_record_23)
                        session2.commit()

            return 0
        else:
            one_account_change_record = AccountChangeRecordModel(
                account_id=one_account.account_id,
                token_id=one_account_token.token_id,
                change_type=AccountChangeRecordModel.change_type_1,
                change_amount=token_amount,
                balance=one_account_token.balance,
                frozon_amount=one_account_token.frozon_amount,
                investment_amount=one_account_token.investment_amount,
                account_token_id=one_account_token.account_token_id,
                token_address=token_address,
                memo=memo,
                begin_time=now_time,
                finish_time=now_time,
                transaction_id=transaction_id,
            )
            session.add(one_account_change_record)
            session.commit()

            one_account_recharge_record = AccountRechargeRecordModel(
                account_id=one_account.account_id,
                user_id=one_account_token.token_id,
                account_change_record_id=one_account_change_record.account_change_record_id,
                token_address=token_address,
                memo=memo,
                receive_token=token_amount,
                transaction_id=transaction_id,
                token_id=coin_id,
                status=AccountRechargeRecordModel.status_2,
                begin_time=now_time,
                finish_time=now_time,
                total_recharge=one_account_token.total_recharge,
                total_withdraw=one_account_token.total_withdraw,
                total_withdraw_fee=one_account_token.total_withdraw_fee,
                balance=one_account_token.balance,
                frozon_amount=one_account_token.frozon_amount,
                investment_amount=one_account_token.investment_amount,
            )
            session.add(one_account_recharge_record)
            session.commit()

            logging.info('+' * 20 + ' 647')

            if one_account.first_recharge_at == '0000-00-00 00:00:00':
                one_account.first_recharge_at = now_time
                session.commit()

                # 首充奖励
                with MysqlTools().session_scope() as session2:
                    account_token_q = session2.query(
                        UserAccountTokenModel
                    ).filter(
                        UserAccountTokenModel.account_id == one_account.account_id,
                        UserAccountTokenModel.user_id == one_account.user_id,
                        UserAccountTokenModel.token_id == USDT_EXPERIENCE_ID,
                        UserAccountTokenModel.status == UserAccountTokenModel.status_on,
                        UserAccountTokenModel.deleted == False,
                    ).with_for_update().first()

                    balance = float(account_token_q.balance)
                    account_token_q.recharge(10)
                    session2.commit()

                    account_change_record = AccountChangeRecordModel(
                        account_id=account_token_q.account_id,
                        token_id=account_token_q.token_id,
                        change_type=AccountChangeRecordModel.change_type_21,
                        change_amount=10,
                        balance=balance + 10,
                        frozon_amount=0,
                        investment_amount=0,
                        account_token_id=account_token_q.account_token_id,
                        begin_time=now_time,
                        finish_time=now_time,
                    )
                    session2.add(account_change_record)
                    session2.commit()

                    # --------------------------------------------------------------
                    #                              邀请充值
                    # 判断是否为邀请注册用户
                    #        |
                    #        |—————————> 不做任何修改
                    #    yes |     no
                    #        v
                    #  邀请人的 usdt 奖励金 += 5
                    # --------------------------------------------------------------
                    if one_account.invitee_code:
                        # 根据受邀请码反查邀请人
                        inviter = session2.query(
                            UserAccountModel
                        ).filter(
                            UserAccountModel.inviter_code == one_account.invitee_code,
                            UserAccountModel.deleted == False,
                            UserAccountModel.status == UserAccountModel.status_on,
                        ).first()

                        # 增加邀请人的 usdt 奖励金
                        inviter_token_q = session2.query(
                            UserAccountTokenModel
                        ).filter(
                            UserAccountTokenModel.account_id == inviter.account_id,
                            UserAccountTokenModel.user_id == inviter.user_id,
                            UserAccountTokenModel.token_id == USDT_EXPERIENCE_ID,
                            UserAccountTokenModel.status == UserAccountTokenModel.status_on,
                            UserAccountTokenModel.deleted == False,
                        ).with_for_update().first()

                        balance_23 = float(inviter_token_q.balance)
                        inviter_token_q.recharge(5)
                        session2.commit()

                        account_change_record_23 = AccountChangeRecordModel(
                            account_id=inviter_token_q.account_id,
                            token_id=inviter_token_q.token_id,
                            change_type=AccountChangeRecordModel.change_type_23,
                            change_amount=5,
                            balance=balance_23 + 5,
                            frozon_amount=0,
                            investment_amount=0,
                            account_token_id=inviter_token_q.account_token_id,
                            begin_time=now_time,
                            finish_time=now_time,
                        )
                        session2.add(account_change_record_23)
                        session2.commit()

            return 0

    def get_pay_salt(self, user_id, user_type=_USER_TYPE_INVEST):
        with MysqlTools().session_scope() as session:

            if user_type == _USER_TYPE_INVEST:
                user_model = UserAccountModel
                user = session.query(user_model).filter(user_model.user_id == user_id,
                                                        user_model.deleted == False, ).first()
            else:
                self.return_error(10017)

            if user is None:
                self.return_error(20001)

            if not user.transaction_bcrypt_salt:
                user.transaction_bcrypt_salt = get_bcrypt_salt().decode("utf-8")
                session.commit()

            return {
                'bcrypt_salt': user.transaction_bcrypt_salt,
            }

    def reset_pay_password(self, user_id, password, user_type=_USER_TYPE_INVEST):
        with MysqlTools().session_scope() as session:

            if user_type == _USER_TYPE_INVEST:
                user_model = UserAccountModel
                user = session.query(user_model).filter(user_model.user_id == user_id,
                                                        user_model.deleted == False, ).first()
            else:
                self.return_error(10017)

            if user is None:
                self.return_error(20001)

            user.transaction_passwd_salt = urandom(12)

            user.transaction_password = sha512(str(password), str(user.transaction_passwd_salt))

            session.commit()
            return {
                "status": "true",
            }

    def set_nick_name(self, user_id, nick_name, user_type=_USER_TYPE_INVEST):
        with MysqlTools().session_scope() as session:

            if user_type == _USER_TYPE_INVEST:
                user_model = UserAccountModel
                one_nick = session.query(user_model).filter(
                    user_model.nick_name == nick_name,
                    user_model.deleted == False,
                ).first()
                if one_nick is not None:
                    self.return_error(30038)
                one_nick = session.query(RobotAccountModel).filter(
                    user_model.nick_name == nick_name,
                    user_model.deleted == False,
                ).first()
                if one_nick is not None:
                    self.return_error(30039)

                user = session.query(user_model).filter(user_model.user_id == user_id,
                                                        user_model.deleted == False, ).first()
            else:
                self.return_error(10017)

            if user is None:
                self.return_error(20001)

            user.nick_name = nick_name
            session.commit()
            return {
                "status": "true",
            }

    def set_avatar(self, user_id, avatar, user_type=_USER_TYPE_INVEST):
        with MysqlTools().session_scope() as session:

            if user_type == _USER_TYPE_INVEST:
                user_model = UserAccountModel
                user = session.query(user_model).filter(user_model.user_id == user_id,
                                                        user_model.deleted == False, ).first()
            else:
                self.return_error(10017)

            if user is None:
                self.return_error(20001)

            user.avatar = avatar
            session.commit()
            return {
                "status": "true",
            }

    def set_mobile(self, user_id, user_mobile, mobile_country_code, user_type=_USER_TYPE_INVEST):
        with MysqlTools().session_scope() as session:

            if user_type == _USER_TYPE_INVEST:
                user_model = UserAccountModel
                user = session.query(user_model).filter(user_model.user_id == user_id,
                                                        user_model.deleted == False, ).first()
            else:
                self.return_error(10017)

            if user is None:
                self.return_error(20001)

            user.user_mobile = user_mobile
            user.mobile_country_code = mobile_country_code

            session.commit()
            return {
                "status": "true",
            }

    def set_email(self, user_id, email, user_type=_USER_TYPE_INVEST):
        with MysqlTools().session_scope() as session:

            if user_type == _USER_TYPE_INVEST:
                user_model = UserAccountModel
                user = session.query(user_model).filter(user_model.user_id == user_id,
                                                        user_model.deleted == False, ).first()
            else:
                self.return_error(10017)

            if user is None:
                self.return_error(20001)

            user.email = email

            session.commit()
            return {
                "status": "true",
            }

    def get_inner_user_account_info(self, session, user_id, user_type=_USER_TYPE_INVEST):
        """
        事务内获取用户详情
        :param session: 所属事务
        :param user_id: 用户id
        :param user_type: 用户类型
        :return:
        """
        result_dict = {
            'score': 0,
            'account': [],
            'transaction_password': '',
            'nick_name': '',
            'avatar': '',
        }

        if user_type == _USER_TYPE_INVEST:
            user_model = UserAccountModel
            token_model = UserAccountTokenModel
            user = session.query(user_model).filter(user_model.user_id == user_id,
                                                    user_model.deleted == False, ).first()
        else:
            return result_dict

        # 1.0 判断用户是否存在,如果已经存在则用户已经注册
        if not user:
            return result_dict

        result_dict['score'] = user.score
        result_dict['transaction_password'] = '******' if user.transaction_password else ''
        result_dict['nick_name'] = user.nick_name
        result_dict['avatar'] = user.avatar
        result_dict['profile_picture'] = user.profile_picture if user.profile_picture else ""

        user_token = session.query(
            token_model.total_recharge,
            token_model.total_withdraw,
            token_model.total_withdraw_fee,
            token_model.balance,
            token_model.frozon_amount,
            token_model.investment_amount,
            TokenCoinModel
        ).outerjoin(
            TokenCoinModel, token_model.token_id == TokenCoinModel.coin_id
        ).filter(
            token_model.user_id == user_id,
            token_model.deleted == False,
            token_model.account_id == user.account_id,
            TokenCoinModel.deleted == False,
        ).all()

        if user_token is not None:
            for one_token in user_token:
                response = {
                    'coin_id': one_token.TokenCoinModel.coin_id,
                    'coin_name': one_token.TokenCoinModel.coin_name,
                    'coin_des': one_token.TokenCoinModel.coin_des,
                    'total_recharge': '%.18f' % one_token.total_recharge,
                    'total_withdraw': '%.18f' % one_token.total_withdraw,
                    'total_withdraw_fee': '%.18f' % one_token.total_withdraw_fee,
                    'balance': '%.18f' % one_token.balance,
                    'frozon_amount': '%.18f' % one_token.frozon_amount,
                    'investment_amount': '%.18f' % one_token.investment_amount,
                }
                if one_token.TokenCoinModel.coin_id == USDT_EXPERIENCE_ID:
                    response['coin_name'] = 'USDT 体验金'
                result_dict['account'].append(response)

        return result_dict

    def get_inner_user_account_by_token(self, session, user_id, token_id, user_type=_USER_TYPE_INVEST):
        """
        事务内获取用户详情
        :param session: 所属事务
        :param user_id: 用户id
        :param user_type: 用户类型
        :param token_id: 币种类型
        :return:
        """

        if user_type == _USER_TYPE_INVEST:
            user_model = UserAccountModel
            token_model = UserAccountTokenModel
            user = session.query(user_model).filter(user_model.user_id == user_id,
                                                    user_model.deleted == False, ).first()
        else:
            return 10017

        # 1.0 判断用户是否存在,如果已经存在则用户已经注册
        if not user:
            return 20001

        result_dict = {
            'user_id': user_id,
            'coin_id': token_id,
            'coin_name': '',
            'balance': '%.18f' % get_decimal('0'),
        }
        user_token = session.query(
            # token_model.total_recharge,
            # token_model.total_withdraw,
            # token_model.total_withdraw_fee,
            token_model.balance,
            # token_model.frozon_amount,
            # token_model.investment_amount,
            TokenCoinModel.coin_id,
            TokenCoinModel.coin_name,
        ).outerjoin(
            TokenCoinModel, token_model.token_id == TokenCoinModel.coin_id
        ).filter(
            token_model.user_id == user_id,
            token_model.deleted == False,
            token_model.account_id == user.account_id,
            TokenCoinModel.deleted == False,
            token_model.token_id == token_id,
        ).first()

        if user_token is not None:
            result_dict['coin_name'] = user_token.coin_name
            result_dict['balance'] = '%.18f' % user_token.balance
            if user_token.coin_id == USDT_EXPERIENCE_ID:
                result_dict['coin_name'] = 'USDT 体验金'
            if user_token.coin_id == _COIN_ID_USDT:
                result_dict['balance'] = '%.4f' % user_token.balance

        return result_dict

    def do_bet(self, session, user_id, token_id, amount, transaction_id, bet_num, game_serial, source=None, change_type=None):
        """
        下注
        :param session: 所属事务
        :param user_id: 用户id
        :param token_id: 币种id
        :param amount: 下注金额
        :param transaction_id: 交易单号
        :param bet_num: 下注量
        :param game_serial: 期号
        :param source: 操作渠道
        :return: 操作正常则返回0，异常则返回错误码，其对应error_code_utils的对应描述
        """
        user_model = UserAccountModel
        token_model = UserAccountTokenModel
        user = session.query(user_model).filter(user_model.user_id == user_id,
                                                user_model.deleted == False, ).first()

        # 1.0 判断用户是否存在,如果已经存在则用户已经注册
        if not user:
            return 20001
        one_token = session.query(token_model).filter(
            token_model.user_id == user_id,
            token_model.deleted == False,
            token_model.account_id == user.account_id,
            token_model.token_id == token_id,
        ).with_for_update().first()

        if one_token is None:
            return 35017

        bet_result = one_token.bet(amount)

        if not bet_result:
            return 35021

        if change_type is None:
            one_account_change_record = AccountChangeRecordModel(
                account_id=user.account_id,
                account_token_id=one_token.account_token_id,
                token_id=token_id,
                change_type=AccountChangeRecordModel.change_type_3,
                change_amount=amount,
                change_fee=get_decimal('0'),
                balance=one_token.balance,
                frozon_amount=one_token.frozon_amount,
                investment_amount=one_token.investment_amount,
                begin_time=datetime.datetime.utcnow(),
                finish_time=datetime.datetime.utcnow(),
                transaction_id=transaction_id,
                change_number=bet_num,
                token_address=game_serial,
            )
        else:
            one_account_change_record = AccountChangeRecordModel(
                account_id=user.account_id,
                account_token_id=one_token.account_token_id,
                token_id=token_id,
                change_type=change_type,
                change_amount=amount,
                change_fee=get_decimal('0'),
                balance=one_token.balance,
                frozon_amount=one_token.frozon_amount,
                investment_amount=one_token.investment_amount,
                begin_time=datetime.datetime.utcnow(),
                finish_time=datetime.datetime.utcnow(),
                transaction_id=transaction_id,
                change_number=bet_num,
                token_address=game_serial,
            )
        if source is not None:
            one_account_change_record.source = source

        session.add(one_account_change_record)
        return 0

    def do_cancel_bet(self, session, user_id, token_id, amount, transaction_id, bet_num, game_serial, source=None, change_type=None):
        """
        取消下注
        :param session: 所属事务
        :param user_id: 用户id
        :param token_id: 币种id
        :param amount: 下注金额
        :param transaction_id: 交易单号
        :param bet_num: 下注量
        :param game_serial: 期号
        :param source: 操作渠道
        :return: 操作正常则返回0，异常则返回错误码，其对应error_code_utils的对应描述
        """
        user_model = UserAccountModel
        token_model = UserAccountTokenModel
        user = session.query(user_model).filter(user_model.user_id == user_id,
                                                user_model.deleted == False, ).first()

        # 1.0 判断用户是否存在,如果已经存在则用户已经注册
        if not user:
            return 20001
        one_token = session.query(token_model).filter(
            token_model.user_id == user_id,
            token_model.deleted == False,
            token_model.account_id == user.account_id,
            token_model.token_id == token_id,
        ).with_for_update().first()

        if one_token is None:
            return 35017

        bet_result = one_token.cancel_bet(amount)

        if not bet_result:
            return 35021

        if change_type is None:
            one_account_change_record = AccountChangeRecordModel(
                account_id=user.account_id,
                account_token_id=one_token.account_token_id,
                token_id=token_id,
                change_type=AccountChangeRecordModel.change_type_13,
                change_amount=amount,
                change_fee=get_decimal('0'),
                balance=one_token.balance,
                frozon_amount=one_token.frozon_amount,
                investment_amount=one_token.investment_amount,
                begin_time=datetime.datetime.utcnow(),
                finish_time=datetime.datetime.utcnow(),
                transaction_id=transaction_id,
                change_number=bet_num,
                token_address=game_serial,
            )
        else:
            one_account_change_record = AccountChangeRecordModel(
                account_id=user.account_id,
                account_token_id=one_token.account_token_id,
                token_id=token_id,
                change_type=change_type,
                change_amount=amount,
                change_fee=get_decimal('0'),
                balance=one_token.balance,
                frozon_amount=one_token.frozon_amount,
                investment_amount=one_token.investment_amount,
                begin_time=datetime.datetime.utcnow(),
                finish_time=datetime.datetime.utcnow(),
                transaction_id=transaction_id,
                change_number=bet_num,
                token_address=game_serial,
            )
        if source is not None:
            one_account_change_record.source = source

        session.add(one_account_change_record)
        return 0

    def do_win_new_session(self, user_id, token_id, amount, transaction_id, bet_num, game_serial):
        """
        游戏胜利加钱
        :param session: 所属事务
        :param user_id: 用户id
        :param token_id: 币种id
        :param amount: 下注金额
        :param transaction_id: 交易单号
        :param bet_num: 下注量
        :param game_serial: 期号
        :return: 操作正常则返回0，异常则返回错误码，其对应error_code_utils的对应描述
        """
        user_model = UserAccountModel
        token_model = UserAccountTokenModel
        with MysqlTools().session_scope() as session:
            user = session.query(user_model).filter(
                user_model.user_id == user_id,
                user_model.deleted == False,
            ).with_for_update().first()

            # 1.0 判断用户是否存在,如果已经存在则用户已经注册
            if not user:
                session.rollback()
                return 20001
            one_token = session.query(token_model).filter(
                token_model.user_id == user_id,
                token_model.deleted == False,
                token_model.account_id == user.account_id,
                token_model.token_id == token_id,
            ).with_for_update().first()

            if one_token is None:
                # 用户还没有该币种的账户，故而先创建该账户
                one_token = UserAccountTokenModel(
                    account_id=user.account_id,
                    user_id=user.user_id,
                    token_id=token_id,
                    balance=get_decimal('0.0'),
                )
                session.add(one_token)

            win_result = one_token.increase_amount(amount)

            if not win_result:
                session.rollback()
                return 35022

            one_account_change_record = AccountChangeRecordModel(
                account_id=user.account_id,
                account_token_id=one_token.account_token_id,
                token_id=token_id,
                change_type=AccountChangeRecordModel.change_type_5,
                change_amount=amount,
                change_fee=get_decimal('0'),
                balance=one_token.balance,
                frozon_amount=one_token.frozon_amount,
                investment_amount=one_token.investment_amount,
                begin_time=datetime.datetime.utcnow(),
                finish_time=datetime.datetime.utcnow(),
                transaction_id=transaction_id,
                change_number=bet_num,
                token_address=game_serial,
            )

            session.add(one_account_change_record)
            session.commit()
        return 0

    def do_win(self, session, user_id, token_id, amount, transaction_id, bet_num, game_serial, change_type=None):
        """
        游戏胜利加钱
        :param session: 所属事务
        :param user_id: 用户id
        :param token_id: 币种id
        :param amount: 下注金额
        :param transaction_id: 交易单号
        :param bet_num: 下注量
        :param game_serial: 期号
        :return: 操作正常则返回0，异常则返回错误码，其对应error_code_utils的对应描述
        """
        user_model = UserAccountModel
        token_model = UserAccountTokenModel
        user = session.query(user_model).filter(
            user_model.user_id == user_id,
            user_model.deleted == False,
        ).with_for_update().first()

        # 1.0 判断用户是否存在,如果已经存在则用户已经注册
        if not user:
            return 20001
        one_token = session.query(token_model).filter(
            token_model.user_id == user_id,
            token_model.deleted == False,
            token_model.account_id == user.account_id,
            token_model.token_id == token_id,
        ).with_for_update().first()

        if one_token is None:
            # 用户还没有该币种的账户，故而先创建该账户
            one_token = UserAccountTokenModel(
                account_id=user.account_id,
                user_id=user.user_id,
                token_id=token_id,
                balance=get_decimal('0.0'),
            )
            session.add(one_token)

        win_result = one_token.increase_amount(amount)

        if not win_result:
            return 35022
        if change_type is None:
            one_account_change_record = AccountChangeRecordModel(
                account_id=user.account_id,
                account_token_id=one_token.account_token_id,
                token_id=token_id,
                change_type=AccountChangeRecordModel.change_type_5,
                change_amount=amount,
                change_fee=get_decimal('0'),
                balance=one_token.balance,
                frozon_amount=one_token.frozon_amount,
                investment_amount=one_token.investment_amount,
                begin_time=datetime.datetime.utcnow(),
                finish_time=datetime.datetime.utcnow(),
                transaction_id=transaction_id,
                change_number=bet_num,
                token_address=game_serial,
            )
        else:
            one_account_change_record = AccountChangeRecordModel(
                account_id=user.account_id,
                account_token_id=one_token.account_token_id,
                token_id=token_id,
                change_type=change_type,
                change_amount=amount,
                change_fee=get_decimal('0'),
                balance=one_token.balance,
                frozon_amount=one_token.frozon_amount,
                investment_amount=one_token.investment_amount,
                begin_time=datetime.datetime.utcnow(),
                finish_time=datetime.datetime.utcnow(),
                transaction_id=transaction_id,
                change_number=bet_num,
                token_address=game_serial
            )

        session.add(one_account_change_record)
        return 0

    def check_pay_password(self, user_id, password, user_type=_USER_TYPE_INVEST):
        """
        校验支付密码
        :param user_id: 用户id
        :param password: 前端加密后的密码
        :param user_type: 用户类型
        :return:
        """
        # if get_env() == 'dev' and password:
        #     return True
        with MysqlTools().session_scope() as session:

            if user_type == _USER_TYPE_INVEST:
                user_model = UserAccountModel
                user = session.query(user_model).filter(user_model.user_id == user_id,
                                                        user_model.deleted == False, ).first()
            else:
                self.return_error(10017)

            if user is None:
                self.return_error(20001)

            if not user.transaction_password:
                self.return_error(35023)

            check_result = slow_is_equal(user.transaction_password,
                                         sha512(str(password), str(user.transaction_passwd_salt)))

            if not check_result:
                self.return_error(35024)

            return True

    def apply_withdraw(self, user_id, coin_id, withdraw_amount, withdraw_fee, withdraw_address, source, memo=""):
        """
        提现申请
        :param user_id: 用户id
        :param coin_id:
        :param withdraw_amount: 提现金额
        :param withdraw_fee: 提现服务费
        :param withdraw_address: 提现收款地址
        :param memo
        :return:
        """
        withdraw_amount_float = float(withdraw_amount)
        withdraw_amount = get_decimal(withdraw_amount, digits=18)
        withdraw_fee = get_decimal(withdraw_fee, digits=18)
        if withdraw_amount < 0:
            self.return_error(35025, error_msg="最小提现金额为---" + str(bitcoin_min_price.get(coin_id, 0.1)))
        if withdraw_fee < 0:
            self.return_error(35026)

        # 校验提现费用
        # EOS
        if coin_id == _COIN_ID_EOS:
            if get_env() == 'dev':
                logging.info('dev env')
                if withdraw_amount_float < 0.01:
                    self.return_error(35025, error_msg="最小提现金额为 -- 0.01")
            else:
                logging.info('product env')
                if withdraw_amount_float < 1:
                    self.return_error(35025, error_msg="最小提现金额为 -- 1")
        # BTC
        elif coin_id == _COIN_ID_BTC:
            if withdraw_amount_float < 0.001:
                self.return_error(35025, error_msg="最小提现金额为 -- 0.001")
        elif coin_id == _COIN_ID_ETH:
            if withdraw_amount_float < 0.01:
                self.return_error(35025, error_msg="最小提现金额为 -- 0.01")

        # 前端输入的提现金额，代表着用户到手金额+费用
        real_withdraw_amount = withdraw_amount - withdraw_fee

        with MysqlTools().session_scope() as session:
            user_model = UserAccountModel
            one_account = session.query(user_model).filter(
                user_model.user_id == user_id,
                user_model.deleted == False,
                user_model.status == user_model.status_on,
            ).with_for_update().first()
            if not one_account:
                self.return_error(35005)

            one_token_msg = session.query(TokenCoinModel).filter(
                TokenCoinModel.coin_id == coin_id,
            ).first()

            if not one_token_msg:
                self.return_error(35017)

            one_account_token = session.query(UserAccountTokenModel).filter(
                UserAccountTokenModel.account_id == one_account.account_id,
                UserAccountTokenModel.user_id == user_id,
                UserAccountTokenModel.token_id == coin_id,
                UserAccountTokenModel.status == UserAccountTokenModel.status_on,
                UserAccountTokenModel.deleted == False,
            ).with_for_update().first()
            if one_account_token is None:
                self.return_error(35027)

            apply_result = one_account_token.apply_withdraw(real_withdraw_amount, withdraw_fee)
            if not apply_result:
                self.return_error(35025, error_msg="最小提现金额为---" + str(
                    bitcoin_min_price.get(coin_id, 0.1)))

            # 如果币种为 eos，扣除 wallet_eos 金额
            if coin_id == _COIN_ID_EOS:
                wallet_eos_q = session.query(
                    WalletEosModel
                ).filter(
                    WalletEosModel.deleted == False,
                    WalletEosModel.account_id == one_account.account_id,
                ).first()
                wallet_eos_q.amount -= Decimal(withdraw_amount)

            one_account_change_record = AccountChangeRecordModel(
                account_id=one_account.account_id,
                token_id=one_account_token.token_id,
                change_type=AccountChangeRecordModel.change_type_2,
                change_amount=real_withdraw_amount,
                change_fee=withdraw_fee,
                balance=one_account_token.balance,
                frozon_amount=one_account_token.frozon_amount,
                investment_amount=one_account_token.investment_amount,
                account_token_id=one_account_token.account_token_id,
                token_address=withdraw_address,
                memo=memo,
                begin_time=datetime.datetime.utcnow(),
                source=source,
            )

            withdraw_order = WalletForeignService().generate_withdraw_order({
                "req_no": one_account_change_record.account_change_record_id,
                "account_id": one_account.account_id,
                "coin_id": one_account_token.token_id,
                "withdraw_address": withdraw_address,
                "withdraw_amount": withdraw_amount,
                "withdraw_fee": withdraw_fee,
                "withdraw_type": "0",  # 用户提现
                "memo": memo
            })

            if isinstance(withdraw_order, int):
                self.return_error(withdraw_order)

            account_apply_withdraw_result, account_apply_withdraw_transaction_id = withdraw_order["withdraw_status"], \
                                                                                   withdraw_order["order_no"]

            if not account_apply_withdraw_result:
                self.return_error(35029)

            session.add(one_account_change_record)

            one_account_withdraw_record = AccountWithdrawRecordModel(
                account_id=one_account.account_id,
                account_change_record_id=one_account_change_record.account_change_record_id,
                user_id=user_id,
                token_address=withdraw_address,
                memo=memo,
                withdraw_amount=real_withdraw_amount,
                withdraw_fee=withdraw_fee,
                transaction_id=account_apply_withdraw_transaction_id,
                token_id=one_account_token.token_id,
                status=AccountWithdrawRecordModel.status_1,
                begin_time=datetime.datetime.utcnow(),
                total_recharge=one_account_token.total_recharge,
                total_withdraw=one_account_token.total_withdraw,
                total_withdraw_fee=one_account_token.total_withdraw_fee,
                balance=one_account_token.balance,
                frozon_amount=one_account_token.frozon_amount,
                investment_amount=one_account_token.investment_amount,
            )
            session.add(one_account_withdraw_record)

            session.commit()
            return {
                'token_address': withdraw_address,
                'memo': memo,
                'coin_name': one_token_msg.coin_name,
                'coin_id': coin_id,
                'balance': decimal_to_client(one_account_token.balance),
            }

    def do_withdraw(self, account_change_record_id, transaction_id, withdraw_result, withdraw_actual_amount,
                    withdraw_actual_fee, withdraw_return_balance=0, session=None):
        """
        外部调用实施提现，若不传事务，则本方法起一个事务，否则，调用入参的事务
        :param session: 所处的事务
        :param account_change_record_id: 账户变换表的id
        :param transaction_id: 交易id
        :param withdraw_result: 提现结果，只能是AccountChangeRecordModel的 change_type_4 或者 change_type_6
        :param withdraw_actual_amount: 提现 实际到账金额
        :param withdraw_actual_fee: 提现 实际花费手续费 withdraw_amount = withdraw_actual_amount + withdraw_actual_fee
        :param withdraw_return_balance: 提现 返还给用户的余额
        :return:
        """
        if session is None:
            with MysqlTools().session_scope() as session:
                do_withdraw_result = self.__do_withdraw(
                    session,
                    account_change_record_id,
                    transaction_id,
                    withdraw_result,
                    withdraw_actual_amount,
                    withdraw_actual_fee,
                    withdraw_return_balance=withdraw_return_balance,
                )
                if isinstance(do_withdraw_result, int) and do_withdraw_result != 0:
                    self.return_error(do_withdraw_result)
                else:
                    session.commit()
                return True
        else:
            do_withdraw_result = self.__do_withdraw(
                session,
                account_change_record_id,
                transaction_id,
                withdraw_result,
                withdraw_actual_amount,
                withdraw_actual_fee,
                withdraw_return_balance=withdraw_return_balance,
            )
            if isinstance(do_withdraw_result, int) and do_withdraw_result != 0:
                self.return_error(do_withdraw_result)
            else:
                return do_withdraw_result

    def __do_withdraw(self, session, account_change_record_id, transaction_id, withdraw_result, withdraw_actual_amount,
                      withdraw_actual_fee, withdraw_return_balance=0):
        """
        提现成功或者失败
        :param session: 所处的事务
        :param account_change_record_id: 账户变换表的id
        :param transaction_id: 交易id
        :param withdraw_result: 提现结果，只能是AccountChangeRecordModel的 change_type_4 或者 change_type_6
        :param withdraw_actual_amount: 实际用户到账数
        :param withdraw_actual_fee: 实际手续费
        :param withdraw_return_balance: 提现后返还给用户的余额
        :return: 操作正常则返回0，异常则返回错误码，其对应error_code_utils的对应描述
        """
        one_account_change_record = session.query(AccountChangeRecordModel).filter(
            AccountChangeRecordModel.account_change_record_id == account_change_record_id,
            AccountChangeRecordModel.change_type == AccountChangeRecordModel.change_type_2,
            AccountChangeRecordModel.deleted == False,
        ).with_for_update().first()
        if one_account_change_record is None:
            return 35030

        one_account_token = session.query(UserAccountTokenModel).filter(
            UserAccountTokenModel.account_token_id == one_account_change_record.account_token_id,
            UserAccountTokenModel.deleted == False,
        ).with_for_update().first()
        if one_account_token is None:
            return 35027

        if one_account_change_record.change_amount + one_account_change_record.change_fee != (
                withdraw_actual_amount + withdraw_actual_fee + withdraw_return_balance):
            return 35033

        if withdraw_result in [
            AccountChangeRecordModel.change_type_4,
            AccountChangeRecordModel.change_type_7,
        ]:
            one_account_change_record.change_type = withdraw_result
            # 提现记录需要把投资额刨回来,考虑到提现申请后账户可能有其他操作，故而此时直接取账户表中的字段是不准确的
            one_account_change_record.frozon_amount -= (
                    one_account_change_record.change_amount + one_account_change_record.change_fee + withdraw_return_balance)
            one_account_change_record.finish_time = datetime.datetime.utcnow()
            one_account_change_record.transaction_id = transaction_id
            one_account_change_record.change_amount = withdraw_actual_amount
            one_account_change_record.change_fee = withdraw_actual_fee
            one_account_change_record.balance += withdraw_return_balance
            withdraw_record_status = AccountWithdrawRecordModel.status_2
            one_account_token.do_withdraw(
                withdraw_actual_amount, withdraw_actual_fee, withdraw_return_balance
            )
        elif withdraw_result == AccountChangeRecordModel.change_type_6:
            one_account_change_record.change_type = withdraw_result
            # 提现记录需要把投资额刨回来,考虑到提现申请后账户可能有其他操作，故而此时直接取账户表中的字段是不准确的
            one_account_change_record.frozon_amount -= (
                    one_account_change_record.change_amount + one_account_change_record.change_fee + withdraw_return_balance)
            one_account_change_record.finish_time = datetime.datetime.utcnow()
            one_account_change_record.transaction_id = transaction_id
            one_account_change_record.change_amount = withdraw_actual_amount
            one_account_change_record.change_fee = withdraw_actual_fee
            one_account_change_record.balance += withdraw_return_balance
            withdraw_record_status = AccountWithdrawRecordModel.status_3
            one_account_token.refuse_withdraw(
                withdraw_actual_amount, withdraw_actual_fee, withdraw_return_balance
            )
        else:
            return 35031

        one_account_change_record.finish_time = datetime.datetime.utcnow()

        one_account_withdraw_record = AccountWithdrawRecordModel(
            account_id=one_account_token.account_id,
            account_change_record_id=one_account_change_record.account_change_record_id,
            user_id=one_account_token.user_id,
            token_address=one_account_change_record.token_address,
            memo=one_account_change_record.memo,
            withdraw_amount=one_account_change_record.change_amount,
            withdraw_fee=one_account_change_record.change_fee,
            transaction_id=transaction_id,
            token_id=one_account_token.token_id,
            status=withdraw_record_status,
            begin_time=one_account_change_record.begin_time,
            finish_time=datetime.datetime.utcnow(),
            total_recharge=one_account_token.total_recharge,
            total_withdraw=one_account_token.total_withdraw,
            total_withdraw_fee=one_account_token.total_withdraw_fee,
            balance=one_account_token.balance,
            frozon_amount=one_account_token.frozon_amount,
            investment_amount=one_account_token.investment_amount,
        )
        session.add(one_account_withdraw_record)
        return 0

    def get_user_account_info_list(self, session, user_id_list, user_type=_USER_TYPE_INVEST):
        """
        事务内获取用户详情
        :param session: 所属事务
        :param user_id: 用户id
        :param user_type: 用户类型
        :return:
        """
        result_dict = {
        }

        if user_type == _USER_TYPE_INVEST:
            user_model = UserAccountModel
            user_list = session.query(user_model).filter(
                user_model.user_id.in_(user_id_list),
                user_model.deleted == False,
            ).all()
        else:
            return result_dict

        # 1.0 判断用户是否存在,如果已经存在则用户已经注册
        if not user_list:
            return result_dict

        for one_user in user_list:
            result_dict[one_user.user_id] = {
                'user_id': one_user.user_id,
                'nick_name': one_user.nick_name,
            }

        return result_dict

    def get_account_water(self, user_id, change_type=None, page_num=1, page_limit=10, start_id=None):
        """
        获取用户账户流水
        :param user_id: 用户id
        :param change_type: 流水类型，详见AccountChangeRecordModel，不区分类型则不传
        :param page_num: 所查询的页
        :param page_limit: 每页信息条数
        :param start_id: 开始查询id
        :return:
        """
        page_offset = get_offset_by_page(page_num, page_limit)
        page_limit = str(page_limit)
        if change_type and change_type not in AccountChangeRecordModel.get_all_show_change_type():
            self.return_error(35032)
        result_dict = {
            'limit': page_limit,
            'offset': page_num,
            'count': 0,
            'content': [
            ]
        }

        logging.info('用户 ID 为: ' + user_id)
        logging.info('change_type 为: ' + str(change_type))
        logging.info('start_id 为: ' + str(start_id))

        with MysqlTools().session_scope() as session:
            user_model = UserAccountModel
            one_account = session.query(user_model).filter(
                user_model.user_id == user_id,
                user_model.deleted == False,
                user_model.status == user_model.status_on,
            ).with_for_update().first()
            if not one_account:
                self.return_error(35005)

            record_condition = session.query(AccountChangeRecordModel, TokenCoinModel.coin_name).join(
                TokenCoinModel, AccountChangeRecordModel.token_id == TokenCoinModel.coin_id
            ).filter(
                AccountChangeRecordModel.deleted == False,
                AccountChangeRecordModel.account_id == one_account.account_id,
            )

            if change_type == AccountChangeRecordModel.change_type_withdraw_all:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.change_type.in_(AccountChangeRecordModel.get_all_withdraw_change_type())
                )
            elif change_type == AccountChangeRecordModel.change_type_1:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.change_type.in_([
                        AccountChangeRecordModel.change_type_1,
                        AccountChangeRecordModel.change_type_51
                    ])
                )
            elif change_type == AccountChangeRecordModel.change_type_3:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.change_type.in_([
                        AccountChangeRecordModel.change_type_3,
                        AccountChangeRecordModel.change_type_42
                    ])
                )
            elif change_type == AccountChangeRecordModel.change_type_5:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.change_type.in_([
                        AccountChangeRecordModel.change_type_5,
                        AccountChangeRecordModel.change_type_41
                    ])
                )
            elif change_type == AccountChangeRecordModel.change_type_gold_experience:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.change_type.in_(
                        AccountChangeRecordModel.get_all_gold_experience_type())
                )
            elif change_type == AccountChangeRecordModel.change_type_31:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.change_type == AccountChangeRecordModel.change_type_31
                )
            elif change_type == AccountChangeRecordModel.change_type_32:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.change_type == AccountChangeRecordModel.change_type_32
                )
            elif change_type == AccountChangeRecordModel.change_type_33:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.change_type == AccountChangeRecordModel.change_type_33
                )

            # record_condition = record_condition.order_by(desc(AccountChangeRecordModel.created_at))
            # 认为id最大的就是最新生成的，所以id排序和created排序是一样的，且id有索引，所以用id排序
            record_condition = record_condition.order_by(desc(AccountChangeRecordModel._id))

            # 计算不分页的总页数
            record_count = record_condition.count()
            result_dict['count'] = get_page_by_offset(record_count, page_limit)

            if start_id is not None:
                start_id = str(start_id)
                record_condition = record_condition.filter(AccountChangeRecordModel._id < start_id)

            record_condition = record_condition.limit(page_limit).offset(page_offset)

            record_list = record_condition.all()

            for one_record in record_list:
                tmp_amount = one_record.AccountChangeRecordModel.change_amount
                if str(
                        one_record.AccountChangeRecordModel.change_type) in AccountChangeRecordModel.get_all_withdraw_change_type():
                    tmp_amount += one_record.AccountChangeRecordModel.change_fee
                response = {
                    'id': one_record.AccountChangeRecordModel._id,
                    'token_id': one_record.AccountChangeRecordModel.token_id,
                    'change_amount': decimal_to_client(tmp_amount),
                    'change_type': one_record.AccountChangeRecordModel.change_type,
                    'created_at': str(one_record.AccountChangeRecordModel.created_at),
                    'change_fee': decimal_to_client(one_record.AccountChangeRecordModel.change_fee),
                    'token_name': one_record.coin_name,
                    'token_address': one_record.AccountChangeRecordModel.token_address,
                    'memo': one_record.AccountChangeRecordModel.memo,
                }
                if one_record.AccountChangeRecordModel.token_id == USDT_EXPERIENCE_ID:
                    response['token_name'] = 'USDT 体验金'
                    response['change_amount'] = decimal_to_client(tmp_amount, digits=4)
                if one_record.AccountChangeRecordModel.token_id == _COIN_ID_USDT:
                    response['change_amount'] = decimal_to_client(tmp_amount, digits=4)
                if response['token_address'].startswith('1548'):
                    response['token_address'] = response['token_address'][4:]
                if (response['change_type'] == '31') or (response['change_type'] == '32'):
                    response['change_amount']: decimal_to_client(tmp_amount, digits=4)
                if response['change_type'] == '33':
                    response['change_amount']: decimal_to_client(tmp_amount, digits=6)
                result_dict['content'].append(response)

            return result_dict

    def get_account_token_water(
            self, user_id, coin_id, page_num=1, page_limit=10, start_id=None):
        """ 获取账户资产流水 """
        page_offset = get_offset_by_page(page_num, page_limit)
        page_limit = str(page_limit)

        # response dict
        result_dict = {
            'limit': page_limit,
            'offset': page_num,
            'count': 0,
            'content': [
            ]
        }

        with MysqlTools().session_scope() as session:
            # query user's account id
            account = session.query(
                UserAccountModel
            ).filter(
                UserAccountModel.user_id == user_id,
                UserAccountModel.deleted == False,
                UserAccountModel.status == UserAccountModel.status_on
            ).first()
            # check account is exist
            if not account:
                self.return_error(35005)

            # use account id and token id query balance
            account_token_balance = session.query(
                UserAccountTokenModel.balance
            ).filter(
                UserAccountTokenModel.account_id == account.account_id,
                UserAccountTokenModel.token_id == coin_id,
                UserAccountTokenModel.deleted == False
            ).first()

            # check balance is exist
            if not account_token_balance:
                result_dict['balance'] = decimal_to_client(Decimal(0))
                result_dict['balance_USDT'] = decimal_to_client(Decimal(0), digits=2)
                if coin_id == USDT_EXPERIENCE_ID:
                    result_dict['balance'] = str(0)
                return result_dict

            # add balance
            result_dict['balance'] = decimal_to_client(account_token_balance.balance)
            if coin_id == USDT_EXPERIENCE_ID:
                result_dict['balance'] = decimal_to_client(account_token_balance.balance, digits=4)
            result_dict['balance_USDT'] = decimal_to_client(
                account_token_balance.balance * Decimal(get_exchange_rate(coin_id)['price']),
                digits=2
            )

            # use account id and token id query water
            account_token_query = session.query(
                AccountChangeRecordModel, TokenCoinModel.coin_name
            ).join(
                TokenCoinModel,
                AccountChangeRecordModel.token_id == TokenCoinModel.coin_id
            ).filter(
                AccountChangeRecordModel.deleted == False,
                AccountChangeRecordModel.account_id == account.account_id,
                AccountChangeRecordModel.token_id == coin_id
            ).order_by(
                AccountChangeRecordModel.created_at.desc()
            )

            # 计算不分页的总页数
            record_count = account_token_query.count()
            result_dict['count'] = get_page_by_offset(record_count, page_limit)

            if start_id is not None:
                start_id = str(start_id)
                account_token_query = account_token_query.filter(
                    AccountChangeRecordModel._id < start_id)

            result_list = account_token_query.limit(page_limit).offset(page_offset).all()

            for result in result_list:
                tmp_amount = result.AccountChangeRecordModel.change_amount
                if str(
                        result.AccountChangeRecordModel.change_type) in AccountChangeRecordModel.get_all_withdraw_change_type():
                    tmp_amount += result.AccountChangeRecordModel.change_fee
                response = {
                    'id': result.AccountChangeRecordModel._id,
                    'token_id': result.AccountChangeRecordModel.token_id,
                    'change_amount': decimal_to_client(tmp_amount),
                    'change_type': result.AccountChangeRecordModel.change_type,
                    'created_at': str(
                        result.AccountChangeRecordModel.created_at),
                    'change_fee': decimal_to_client(
                        result.AccountChangeRecordModel.change_fee),
                    'token_name': result.coin_name,
                    'token_address': result.AccountChangeRecordModel.token_address,
                    'memo': result.AccountChangeRecordModel.memo,
                }
                if coin_id == USDT_EXPERIENCE_ID:
                    response['change_amount'] = decimal_to_client(tmp_amount, digits=4)
                    response['token_name'] = 'USDT 体验金'
                if coin_id == _COIN_ID_USDT:
                    response['change_amount'] = decimal_to_client(tmp_amount, digits=4)
                result_dict['content'].append(response)
        return result_dict

    # 新用户注册抽奖
    def lottery(self, user_id):
        # get price
        _LOTTERY_PRICE_LIST = [1, 5, 10, 20, 50, 66, 88, 99, 100]
        random_number = random.randint(1, 10000)
        if random_number < 6000:
            price = _LOTTERY_PRICE_LIST[0]
        elif random_number < 7000:
            price = _LOTTERY_PRICE_LIST[1]
        elif random_number < 8000:
            price = _LOTTERY_PRICE_LIST[2]
        elif random_number < 9000:
            price = _LOTTERY_PRICE_LIST[3]
        elif random_number < 9500:
            price = _LOTTERY_PRICE_LIST[4]
        elif random_number < 9700:
            price = _LOTTERY_PRICE_LIST[5]
        elif random_number < 9800:
            price = _LOTTERY_PRICE_LIST[6]
        elif random_number < 9900:
            price = _LOTTERY_PRICE_LIST[7]
        else:
            price = _LOTTERY_PRICE_LIST[-1]

        # 由于产品设计调整，将抽奖调整为赠送固定额度的 USDT 体验币
        # 2019-01 调整为 100
        # 2019-02-19 调整为 1
        price = 1

        # 储存用户的抽奖金额
        with MysqlTools().session_scope() as session:
            # query account id
            user_account_query = session.query(
                UserAccountModel
            ).filter(
                UserAccountModel.user_id == user_id,
                UserAccountModel.deleted == False,
                UserAccountModel.status == UserAccountModel.status_on
            ).first()
            if not user_account_query:
                self.return_error(20001)

            coin_query = session.query(
                TokenCoinModel.coin_id
            ).filter(
                TokenCoinModel.coin_name == USDT_EXPERIENCE_NAME,
                TokenCoinModel.deleted == False
            ).first()

            user_token_usdt_q = session.query(
                UserAccountTokenModel
            ).filter(
                UserAccountTokenModel.account_id == user_account_query.account_id,
                UserAccountTokenModel.user_id == user_id,
                UserAccountTokenModel.token_id == coin_query.coin_id,
                UserAccountTokenModel.deleted == False
            ).first()

            if user_token_usdt_q:
                self.return_error(30040)

            # usdt 体验金的 token_id 为 256
            user_token_usdt_experience = UserAccountTokenModel(
                account_id=user_account_query.account_id,
                user_id=user_id,
                token_id=coin_query.coin_id,
                total_recharge=price,
                balance=price
            )
            session.add(user_token_usdt_experience)
            session.commit()

            # 生成流水时间
            now_time = datetime.datetime.utcnow()

            user_token_query = session.query(
                UserAccountTokenModel.account_token_id
            ).filter(
                UserAccountTokenModel.account_id == user_account_query.account_id,
                UserAccountTokenModel.token_id == coin_query.coin_id,
                UserAccountTokenModel.deleted == False
            ).first()

            # 记录账户流水
            one_account_change_record = AccountChangeRecordModel(
                account_id=user_account_query.account_id,
                token_id=coin_query.coin_id,
                change_type=AccountChangeRecordModel.change_type_20,
                change_amount=price,
                balance=price,
                frozon_amount=0,
                investment_amount=0,
                account_token_id=user_token_query.account_token_id,
                begin_time=now_time,
                finish_time=now_time,
            )
            session.add(one_account_change_record)
            session.commit()

            # 修改用户首次充值状态
            user_account_query.first_lottery = 1
            session.commit()

        return {"price": price}

    # 获取用户的邀请码
    def get_inviter_code(self, user_id):
        with MysqlTools().session_scope() as session:
            # query account id
            user_account_query = session.query(
                UserAccountModel
            ).filter(
                UserAccountModel.user_id == user_id,
                UserAccountModel.deleted == False,
                UserAccountModel.status == UserAccountModel.status_on
            ).first()
            if not user_account_query:
                self.return_error(20001)

            # 如果用户是之前注册的用户
            if user_account_query.inviter_code:
                return user_account_query.inviter_code
            else:
                user_code = session.query(
                    UserAccountModel.inviter_code
                ).filter(
                    UserAccountModel.deleted == False
                ).order_by(
                    UserAccountModel.inviter_code.desc()
                ).first()

                # 生成邀请码
                if user_code.inviter_code:
                    inviter_code = 'LK' + self.generate_inviter_code(
                        user_code.inviter_code.split('K')[1])
                else:
                    inviter_code = 'LK000001'

                user_account_query.inviter_code = inviter_code
                session.commit()
                return inviter_code

    # 获取中奖列表
    @staticmethod
    def get_user_winnings():
        result_dict = {'content': []}
        with MysqlTools().session_scope() as session:
            user_record = session.query(
                AccountChangeRecordModel.change_amount,
                AccountChangeRecordModel.created_at,
                UserAccountModel.nick_name
            ).join(
                UserAccountModel,
                AccountChangeRecordModel.account_id == UserAccountModel.account_id
            ).filter(
                AccountChangeRecordModel.change_type == AccountChangeRecordModel.change_type_20,
                AccountChangeRecordModel.deleted == False
            ).order_by(
                AccountChangeRecordModel.created_at.desc()
            ).limit(10).all()

            if user_record:
                for i in user_record:
                    result_dict['content'].append(
                        {
                            "nick_name": i.nick_name,
                            "change_amount": int(i.change_amount),
                            "created_at": i.created_at.strftime("%Y-%m-%d %H:%M:%S")
                        }
                    )
                return result_dict
            else:
                return result_dict

    def update_user_profile_picture(self, user_id, profile_picture):
        with MysqlTools().session_scope() as session:
            # query user
            user_account_query = session.query(
                UserAccountModel
            ).filter(
                UserAccountModel.user_id == user_id,
                UserAccountModel.deleted == False,
                UserAccountModel.status == UserAccountModel.status_on
            ).first()
            if not user_account_query:
                self.return_error(20001)

            user_account_query.profile_picture = profile_picture
            session.commit()
            return {"status": True}

    def list_all_account_water(self, user_id=None, change_type=None, page_num=1, page_limit=10, token_id=None,
                               water_id=None, finish_time_start=None, user_name=None, finish_time_end=None):
        """
        后台用户查看用户流水
        :param user_id: 用户id
        :param change_type: 流水类型
        :param page_num: 页号
        :param page_limit: 页条数
        :param token_id: 币种id
        :param water_id:  AccountChangeRecordModel 号
        :param finish_time_start: 结束时间起始
        :param user_name: 用户名
        :param finish_time_end:  结束时间截止
        :return:
        """
        page_offset = get_offset_by_page(page_num, page_limit)
        page_limit = str(page_limit)
        if change_type \
                and change_type not in AccountChangeRecordModel.get_all_show_change_type() \
                and change_type not in AccountChangeRecordModel.get_all_withdraw_change_type():
            self.return_error(35032)
        result_dict = {
            'limit': page_limit,
            'offset': page_num,
            'count': 0,
            'content': [
            ]
        }
        with MysqlTools().session_scope() as session:
            user_model = UserAccountModel

            record_condition = session.query(
                AccountChangeRecordModel,
                TokenCoinModel.coin_name,
                user_model.user_id,
                user_model.user_name
            ).join(
                TokenCoinModel,
                AccountChangeRecordModel.token_id == TokenCoinModel.coin_id
            ).join(
                user_model,
                AccountChangeRecordModel.account_id == user_model.account_id,
            ).filter(
                AccountChangeRecordModel.deleted == False,
                TokenCoinModel.deleted == False,
                user_model.deleted == False,
                user_model.status == user_model.status_on,
            )

            # 1 拼接搜索条件的账户号
            if user_id is not None:
                record_condition = record_condition.filter(
                    user_model.user_id == user_id,
                )
            if user_name is not None:
                record_condition = record_condition.filter(
                    user_model.user_name.like("%" + str(user_name) + "%"),
                )

            # 2 拼接币种
            if token_id is not None:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.token_id == token_id,
                )

            # 3 拼接单号
            if water_id is not None:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.account_change_record_id == water_id,
                )

            # 4 拼接入账时间
            if finish_time_start is not None:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.finish_time >= finish_time_start,
                )

            if finish_time_end is not None:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.finish_time < finish_time_end,
                )

            # 5 拼接订单类型
            if change_type and change_type == AccountChangeRecordModel.change_type_withdraw_all:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.change_type.in_(
                        AccountChangeRecordModel.get_all_withdraw_change_type())
                )
            elif change_type and change_type == AccountChangeRecordModel.change_type_withdraw_success:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.change_type.in_(
                        AccountChangeRecordModel.get_all_withdraw_success_type())
                )
            elif change_type:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.change_type == change_type
                )

            # record_condition = record_condition.order_by(desc(AccountChangeRecordModel.created_at))
            # 认为id最大的就是最新生成的，所以id排序和created排序是一样的，且id有索引，所以用id排序
            record_condition = record_condition.order_by(desc(AccountChangeRecordModel._id))

            # 计算不分页的总页数
            record_count = record_condition.count()
            # result_dict['count'] = get_page_by_offset(record_count, page_limit)
            result_dict['count'] = record_count

            # 6 拼接分页
            record_condition = record_condition.limit(page_limit).offset(
                page_offset)

            record_list = record_condition.all()

            for one_record in record_list:
                tmp_amount = one_record.AccountChangeRecordModel.change_amount
                if str(
                        one_record.AccountChangeRecordModel.change_type) in AccountChangeRecordModel.get_all_withdraw_change_type():
                    tmp_amount += one_record.AccountChangeRecordModel.change_fee
                response = {
                    'change_type': one_record.AccountChangeRecordModel.change_type,
                    'id': one_record.AccountChangeRecordModel._id,
                    'water_id': one_record.AccountChangeRecordModel.account_change_record_id,
                    'user_id': one_record.user_id,
                    'user_name': one_record.user_name,
                    'token_id': one_record.AccountChangeRecordModel.token_id,
                    'token_name': one_record.coin_name,
                    'change_amount': decimal_to_client(
                        tmp_amount),
                    'change_fee': decimal_to_client(
                        one_record.AccountChangeRecordModel.change_fee),
                    'change_number': one_record.AccountChangeRecordModel.change_number,
                    'begin_time': str(
                        one_record.AccountChangeRecordModel.begin_time),
                    'finish_time': str(
                        one_record.AccountChangeRecordModel.finish_time),
                    'address': one_record.AccountChangeRecordModel.token_address,
                    'memo': one_record.AccountChangeRecordModel.memo,
                }
                if one_record.AccountChangeRecordModel.token_id == USDT_EXPERIENCE_ID:
                    response['token_name'] = 'USDT 体验金'
                if one_record.AccountChangeRecordModel.token_id == _COIN_ID_USDT:
                    response['change_amount'] = decimal_to_client(tmp_amount, digits=4)
                result_dict['content'].append(response)

            return result_dict

    def get_operating_activities(self, user_name, inviter_code, invitee_code,
                                 change_type, page_num, page_limit,
                                 finish_time_start, finish_time_end, ):

        page_offset = get_offset_by_page(page_num, page_limit)
        page_limit = str(page_limit)
        if change_type \
                and change_type not in AccountChangeRecordModel.get_all_gold_experience_type():
            self.return_error(35032)
        result_dict = {
            'limit': page_limit,
            'offset': page_num,
            'count': 0,
            'content': [
            ]
        }
        with MysqlTools().session_scope() as session:
            records_q = session.query(
                AccountChangeRecordModel,
                UserAccountModel
            ).join(
                UserAccountModel,
                AccountChangeRecordModel.account_id == UserAccountModel.account_id
            ).filter(
                AccountChangeRecordModel.change_type.in_(AccountChangeRecordModel.get_all_gold_experience_type()),
                AccountChangeRecordModel.deleted == False,
                UserAccountModel.deleted == False,
                UserAccountModel.status == UserAccountModel.status_on,
            ).order_by(
                AccountChangeRecordModel.created_at.desc()
            )

            # 1 拼接搜索条件的账户号
            if user_name is not None:
                records_q = records_q.filter(
                    UserAccountModel.user_name.like("%" + str(user_name) + "%"),
                )

            # 4 拼接入账时间
            if finish_time_start is not None:
                records_q = records_q.filter(
                    AccountChangeRecordModel.created_at >= finish_time_start,
                )

            if finish_time_end is not None:
                records_q = records_q.filter(
                    AccountChangeRecordModel.created_at < finish_time_end,
                )

            if change_type is not None:
                records_q = records_q.filter(
                    AccountChangeRecordModel.change_type == change_type
                )

            if inviter_code is not None:
                records_q = records_q.filter(
                    UserAccountModel.inviter_code == inviter_code
                )

            if invitee_code is not None:
                records_q = records_q.filter(
                    UserAccountModel.invitee_code == invitee_code
                )

            record_count = records_q.count()
            result_dict['count'] = record_count

            records_q = records_q.limit(page_limit).offset(
                page_offset)
            record_list = records_q.all()

            for one_record in record_list:
                response = {
                    'id': one_record.AccountChangeRecordModel._id,
                    'user_name': one_record.UserAccountModel.user_name,
                    'inviter_code': one_record.UserAccountModel.inviter_code,
                    'invitee_code': one_record.UserAccountModel.invitee_code,
                    'change_type': one_record.AccountChangeRecordModel.change_type,
                    'change_number': str(int(one_record.AccountChangeRecordModel.change_amount)) + ' USDT体验金',
                    'created_at': one_record.AccountChangeRecordModel.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
                if one_record.AccountChangeRecordModel.token_id == USDT_EXPERIENCE_ID:
                    response['token_name'] = 'USDT 体验金'
                result_dict['content'].append(response)

            return result_dict

    def update_token_coin_message(self):
        """
        更新token_coin表的方法
        :return:
        """
        with open("更新文件路径", "r", encoding="utf-8") as f:
            content = f.read()
            content = content.split("\n")
            for j in range(len(content)):
                one = content[j].split("|")
                for i in range(len(one)):
                    one[i] = one[i].strip()
                    if '[' in one[i]:
                        one[i] = one[i].split("[")[1].split("]")[0]
                content[j] = one
            with MysqlTools().session_scope() as session:
                for one_coin in content:
                    one_model = TokenCoinModel(
                        coin_id=one_coin[0],
                        coin_name=one_coin[2],
                        coin_des=one_coin[3],
                    )
                    session.add(one_model)
                session.commit()
            return content

    @staticmethod
    def get_user_list(search_user_id, user_name, email, user_mobile,
                      register_time_start, register_time_end, source,
                      recharge_time_start, recharge_time_end, page_num,
                      page_limit):
        """
        获取用户列表
        :param search_user_id:
        :param user_name:
        :param email:
        :param user_mobile:
        :param register_time_start:
        :param register_time_end:
        :param source:
        :param recharge_time_start:
        :param recharge_time_end:
        :param page_num:
        :param page_limit:
        :return:
        """

        # result dict
        result_dict = {
            'limit': page_limit,
            'offset': page_num,
            'count': 0,
            'content': [
            ]
        }

        page_offset = get_offset_by_page(page_num, page_limit)
        page_limit = str(page_limit)

        with MysqlTools().session_scope() as session:
            user_model = UserAccountModel
            record_condition = session.query(
                user_model
            ).filter(
                user_model.deleted == False,
                user_model.status == user_model.status_on,
            ).order_by(
                UserAccountModel.created_at.desc()
            )

            # 1 拼接搜索条件的账户号
            if search_user_id is not None:
                record_condition = record_condition.filter(
                    user_model.user_id == search_user_id,
                )
            if user_name is not None:
                record_condition = record_condition.filter(
                    user_model.nick_name.like("%" + user_name + "%"),
                )
            if email is not None:
                record_condition = record_condition.filter(
                    user_model.email == email,
                )
            if user_mobile is not None:
                record_condition = record_condition.filter(
                    user_model.user_mobile == user_mobile,
                )
            if source is not None:
                record_condition = record_condition.filter(
                    user_model.source == source,
                )
            if register_time_start is not None:
                record_condition = record_condition.filter(
                    user_model.created_at >= register_time_start,
                )
            if register_time_end is not None:
                record_condition = record_condition.filter(
                    user_model.created_at <= register_time_end,
                )
            if recharge_time_start is not None:
                record_condition = record_condition.filter(
                    user_model.first_recharge_at >= recharge_time_start,
                )
            if recharge_time_end is not None:
                record_condition = record_condition.filter(
                    user_model.first_recharge_at <= recharge_time_end,
                )

            # 计算不分页的总页数
            record_count = record_condition.count()
            # result_dict['count'] = get_page_by_offset(record_count, page_limit)
            result_dict['count'] = record_count

            # 2 拼接分页
            record_condition = record_condition.limit(page_limit).offset(
                page_offset)

            # get all result
            record_list = record_condition.all()

            # restructure return information
            for one_record in record_list:
                created_at = one_record.created_at
                first_recharge_at = one_record.first_recharge_at
                if isinstance(created_at, str):
                    created_at_str = ""
                else:
                    created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S")

                if isinstance(first_recharge_at, str):
                    first_recharge_at_str = ""
                else:
                    first_recharge_at_str = first_recharge_at.strftime(
                        "%Y-%m-%d %H:%M:%S")
                result_dict['content'].append({
                    "id": one_record._id,
                    "user_mobile": one_record.user_mobile,
                    "email": one_record.email,
                    "nick_name": one_record.nick_name,
                    "create_at": created_at_str,
                    "source": SOURCE_LIST[one_record.source],
                    "first_recharge_at": first_recharge_at_str,
                    "user_name": one_record.user_name,
                })
        return result_dict

    @staticmethod
    def get_user_token_list(search_user_id, user_name, page_num, page_limit, recharge_time_start=None,
                            recharge_time_end=None):
        # result dict
        result_dict = {
            'limit': page_limit,
            'offset': page_num,
            'count': 0,
            'content': [
            ]
        }

        page_offset = get_offset_by_page(page_num, page_limit)
        page_limit = str(page_limit)

        with MysqlTools().session_scope() as session:
            # -------------------------- FIRST --------------------------
            # Query user information and get limited information
            # And generate user set
            # -------------------------- FIRST --------------------------
            user_model = UserAccountModel
            record_condition = session.query(
                user_model.user_id,
                user_model.user_mobile,
                user_model.user_name,
                user_model.first_recharge_at,
                user_model.email,
            ).filter(
                user_model.deleted == False,
                user_model.status == user_model.status_on,
            )

            # 1 拼接搜索条件的账户号
            if search_user_id is not None:
                record_condition = record_condition.filter(
                    user_model.user_id == search_user_id,
                )
            if user_name is not None:
                record_condition = record_condition.filter(
                    user_model.nick_name.like("%" + user_name + "%"),
                )
            if recharge_time_start is not None:
                record_condition = record_condition.filter(
                    user_model.first_recharge_at >= recharge_time_start,
                )
            if recharge_time_end is not None:
                record_condition = record_condition.filter(
                    user_model.first_recharge_at <= recharge_time_end,
                )

            # 计算不分页的总页数
            record_count = record_condition.count()
            # result_dict['count'] = get_page_by_offset(record_count, page_limit)
            result_dict['count'] = record_count

            # 2 拼接分页
            record_condition = record_condition.limit(page_limit).offset(
                page_offset)

            # get all result
            record_list = record_condition.all()

            # generate user set
            user_list = set([i.user_id for i in record_list])

            # -------------------------- SECOND --------------------------
            # Query user's token information which in user list
            # -------------------------- SECOND --------------------------
            query_token = session.query(
                UserAccountTokenModel.user_id,
                UserAccountTokenModel.balance,
                TokenCoinModel.coin_id,
                TokenCoinModel.coin_name,
            ).join(
                TokenCoinModel,
                UserAccountTokenModel.token_id == TokenCoinModel.coin_id
            ).filter(
                UserAccountTokenModel.status == UserAccountTokenModel.status_on,
                UserAccountTokenModel.user_id.in_(user_list)
            ).all()

            # restructure return information
            for one_record in record_list:
                # new list store bitcoin name value in query
                __EXIST_BITCOIN_LIST = []
                if isinstance(one_record.first_recharge_at, str):
                    first_recharge_at_str = ""
                else:
                    first_recharge_at_str = one_record.first_recharge_at.strftime(
                        "%Y-%m-%d %H:%M:%S")
                user_info = {
                    "user_mobile": one_record.user_mobile,
                    "email": one_record.email,
                    "user_name": one_record.user_name,
                    "user_id": one_record.user_id,
                    "first_recharge_at": first_recharge_at_str,
                    # "bitcoin_prices": {}
                }
                # for token_info in query_token:
                #     if token_info.user_id == one_record.user_id:
                #         if token_info.coin_name in BITCOIN_LIST:
                #             # __EXIST_BITCOIN_LIST store coin name
                #             __EXIST_BITCOIN_LIST.append(token_info.coin_name)
                #             token_price = float(token_info.balance)
                #             user_info["bitcoin_prices"][token_info.coin_id] = {
                #                 "id": token_info.coin_id,
                #                 "key": token_info.coin_name,
                #                 "value": token_price
                #             }
                #
                #
                # # compute different set
                # # Eg:
                # # >>> set1 = ['a', 'b', 'c']
                # # >>> set2 = ['a', 'b']
                # # >>> list(set(set1).difference(set(set2)))
                # # ['c']
                # __DIFFERENT_BITCOIN_LIST = list(
                #     set(BITCOIN_LIST).difference(set(__EXIST_BITCOIN_LIST)))
                # # get user need but not in database information
                # if __DIFFERENT_BITCOIN_LIST:
                #     diff_q = session.query(
                #         TokenCoinModel.coin_id,
                #         TokenCoinModel.coin_name
                #     ).filter(
                #         TokenCoinModel.coin_name.in_(__DIFFERENT_BITCOIN_LIST)
                #     ).all()
                #     for i in diff_q:
                #         user_info["bitcoin_prices"][i.coin_id] = {
                #             "id": i.coin_id,
                #             "key": i.coin_name,
                #             "value": 0
                #         }
                for i in COIN_SHOW_LIST:
                    user_info[i] = 0
                for one_token_info in query_token:
                    if one_token_info.user_id == one_record.user_id and one_token_info.coin_name in user_info:
                        user_info[one_token_info.coin_name] = decimal_to_client(one_token_info.balance)
                result_dict['content'].append(user_info)
        return result_dict

    def get_user_token_detail(self, user_id):
        with MysqlTools().session_scope() as session:
            query_user_info = session.query(
                UserAccountModel.user_id,
                UserAccountModel.user_mobile,
                UserAccountModel.email,
                UserAccountModel.created_at,
                UserAccountModel.source
            ).filter(
                UserAccountModel.deleted == False,
                UserAccountModel.status == UserAccountModel.status_on,
                UserAccountModel.user_id == user_id,
            ).first()

            query_token = session.query(
                UserAccountTokenModel.balance,
                UserAccountTokenModel.created_at,
                UserAccountTokenModel.account_id,
                TokenCoinModel.coin_name,
            ).join(
                TokenCoinModel,
                UserAccountTokenModel.token_id == TokenCoinModel.coin_id
            ).filter(
                UserAccountTokenModel.status == UserAccountTokenModel.status_on,
                UserAccountTokenModel.user_id == user_id
            ).all()

            # check data type
            if not query_user_info:
                self.return_error(20001)
            user_info_create = query_user_info.created_at

            if isinstance(user_info_create, str):
                user_info_create = ""
            else:
                user_info_create = user_info_create.strftime("%Y-%m-%d %H:%M:%S")

            result = {
                "user_info": {
                    "user_id": query_user_info.user_id,
                    "user_mobile": query_user_info.user_mobile,
                    "email": query_user_info.email,
                    "created_at": user_info_create,
                    "source": SOURCE_LIST[query_user_info.source]
                },

                "token_info": []
            }

            for token in query_token:
                token_create = token.created_at
                if isinstance(token_create, str):
                    token_create = ""
                else:
                    token_create = token_create.strftime("%Y-%m-%d %H:%M:%S")

                token_name = token.coin_name
                if token_name == "":
                    token_name = "error"

                if token_name == "BTC":
                    query_address = session.query(
                        WalletBtcModel.sub_public_address
                    ).filter(
                        WalletBtcModel.account_id == token.account_id
                    ).first()
                    if query_address:
                        address = query_address.sub_public_address
                    else:
                        address = ""
                    result["token_info"].append({
                        "token_name": token_name,
                        "balance": float(token.balance),
                        "create_at": token_create,
                        "address": address,
                        "memo": ""
                    })
                elif token_name == "ETH":
                    query_address = session.query(
                        WalletEthModel.sub_public_address
                    ).filter(
                        WalletEthModel.account_id == token.account_id
                    ).first()
                    if query_address:
                        address = query_address.sub_public_address
                    else:
                        address = ""
                    result["token_info"].append({
                        "token_name": token_name,
                        "balance": float(token.balance),
                        "create_at": token_create,
                        "address": address,
                        "memo": ""
                    })
                elif token_name == "EOS":
                    query_address = session.query(
                        UserAccountTokenModel.sub_public_address,
                        UserAccountTokenModel.memo
                    ).filter(
                        UserAccountTokenModel.account_id == token.account_id
                    ).first()
                    if query_address:
                        address = query_address.sub_public_address
                        memo = query_address.memo
                    else:
                        address = ""
                        memo = ""
                    result["token_info"].append({
                        "token_name": token_name,
                        "balance": float(token.balance),
                        "create_at": token_create,
                        "address": address,
                        "memo": memo
                    })
                else:
                    result["token_info"].append({
                        "token_name": token_name,
                        "balance": float(token.balance),
                        "create_at": token_create,
                        "address": ""
                    })

            return result

    def user_login(self, user_id, source=AccountLoginMessageModel.source_type_1, login_ip="",
                   user_type=_USER_TYPE_INVEST):
        """
        创建账户
        :param user_id:
        :param nick_name:
        :param user_mobile:
        :param email:
        :param mobile_country_code:
        :param score:
        :param user_type:
        :return:
        """

        with MysqlTools().session_scope() as session:
            if user_type == _USER_TYPE_INVEST:
                user = AccountLoginMessageModel(
                    user_id=user_id,
                    source=source,
                    login_ip=login_ip,
                )
                session.add(user)
                session.commit()

                user_q = session.query(
                    UserAccountModel
                ).filter(
                    UserAccountModel.user_id == user_id,
                    UserAccountModel.deleted == False
                ).first()

                return {
                    "status": "true",
                    "first_lottery": user_q.first_lottery,
                    "user_id": user_id,
                    "nick_name": user_q.nick_name
                }

    # 场外交易所充值 USDT
    def user_account_add_token(self, user_id, token_id, price):
        with MysqlTools().session_scope() as session:
            account = session.query(
                UserAccountModel
            ).filter(
                UserAccountModel.deleted == False,
                UserAccountModel.user_id == user_id
            ).first()
            if not account:
                return {
                    "status": False,
                    "debugmsg": "user_id 有误"
                }

            user_account_token = session.query(
                UserAccountTokenModel
            ).filter(
                UserAccountTokenModel.deleted == False,
                UserAccountTokenModel.user_id == user_id,
                UserAccountTokenModel.token_id == token_id
            ).with_for_update().first()

            if user_account_token:
                user_account_token.balance += price
                user_account_token.total_recharge += price
                session.flush()

                # 添加账户流水
                now_time = datetime.datetime.utcnow()
                account_change_record = AccountChangeRecordModel(
                    account_id=account.account_id,
                    token_id=token_id,
                    change_type=AccountChangeRecordModel.change_type_51,
                    change_amount=price,
                    balance=user_account_token.balance,
                    frozon_amount=0,
                    investment_amount=0,
                    account_token_id=user_account_token.account_token_id,
                    begin_time=now_time,
                    finish_time=now_time,
                )
                session.add(account_change_record)
                session.commit()
            else:
                token = UserAccountTokenModel(
                    user_id=user_id,
                    account_id=account.account_id,
                    token_id=token_id,
                    total_recharge=price,
                    balance=price
                )
                session.add(token)
                session.flush()

                # 添加账户流水
                now_time = datetime.datetime.utcnow()
                account_change_record = AccountChangeRecordModel(
                    account_id=account.account_id,
                    token_id=token_id,
                    change_type=AccountChangeRecordModel.change_type_51,
                    change_amount=price,
                    balance=price,
                    frozon_amount=0,
                    investment_amount=0,
                    account_token_id=token.account_token_id,
                    begin_time=now_time,
                    finish_time=now_time,
                )
                session.add(account_change_record)
                session.commit()
        return {
            "status": True,
        }


if __name__ == '__main__':
    print(AccountService().get_user_token_list('17ff9cd11b6c460eb7964f667b40c9b9', None, 1, 10))
