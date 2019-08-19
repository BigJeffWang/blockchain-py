from common_settings import *
from models.foreign_withdraw_order_record_model import ForeignWithdrawOrderRecordModel
from models.tx_listening_btc_model import TxListeningBtcModel
from models.tx_listening_eos_model import TxListeningEosModel
from models.tx_listening_eth_model import TxListeningEthModel
from models.user_account_model import UserAccountModel
from models.wallet_btc_gather_model import WalletBtcGatherModel
from models.wallet_eos_gather_model import WalletEosGatherModel
from models.wallet_eth_gather_model import WalletEthGatherModel
from services.base_service import BaseService
from services.wallet_foreign_service import WalletForeignService
from tools.mysql_tool import MysqlTools
from utils.util import decimal_to_str
from utils.util import generate_order_no
from utils.util import get_offset_by_page, get_now_time, get_page_by_offset, get_decimal, decimal_to_client
from models.account_change_record_model import AccountChangeRecordModel
from models.token_coin_model import TokenCoinModel
from sqlalchemy import desc
from services.vcode_service import VcodeService
from config import get_config


# 提现后台相关
class TxListeningEModel(object):
    pass


class WalletWithdrawService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def withdraw_list(self, coin_id, withdraw_type, withdraw_status, audit_status, source_status, user_name,
                      withdraw_number, apply_time_start, apply_time_end, from_address, transfer_time_start,
                      transfer_time_end, offset, limit, page_flag):
        """
        提现申请列表、提现处理列表、提现已完成列表
        :param coin_id: 币种
        :param withdraw_type: 提现状态: 提现类型: 0-用户提现, 1-用户中奖, 2-归集, 3-归集转归集
        :param withdraw_status: 提现状态: 0-未交易, 1-提现中, 2-提现成功, 3-提现失败, 4-交易失败, 5-提现拒绝(审核拒绝)
        :param audit_status: 审核状态: 0-待审核, 1-审核通过, 2-审核拒绝
        :param source_status: 来源: 0-线上, 1-线下
        :param user_name: 用户名
        :param withdraw_number: 最小提现数量
        :param apply_time_start: 申请时间start
        :param apply_time_end: 申请时间end
        :param from_address: 出账地址
        :param transfer_time_start: 转账时间start
        :param transfer_time_end: 转账时间end
        :param offset: 当前页数
        :param limit: 每页条数
        :param page_flag: page_flag
        :return:
        """
        f_filters = {}
        if coin_id:
            f_filters["coin_id"] = coin_id
        if withdraw_type:
            f_filters["withdraw_type"] = withdraw_type
        if withdraw_status:
            f_filters["withdraw_status"] = withdraw_status
        if audit_status:
            f_filters["audit_status"] = audit_status
        if source_status:
            f_filters["source_status"] = source_status
        if from_address:
            f_filters["from_address"] = from_address
        if page_flag == _ONE_S:
            f_filters["withdraw_status"] = _ZERO_S
        u_filters = {}
        if user_name:
            u_filters["user_name"] = user_name
        if not withdraw_number:
            withdraw_number = 0
        if not apply_time_start:
            apply_time_start = "0000-00-00"
        else:
            apply_time_start = apply_time_start
        if not apply_time_end:
            apply_time_end = "2999-12-31"
        else:
            apply_time_end = apply_time_end
        if not transfer_time_start:
            transfer_time_start = "0000-00-00"
        else:
            transfer_time_start = transfer_time_start
        if not transfer_time_end:
            transfer_time_end = "2999-12-31"
        else:
            transfer_time_end = transfer_time_end

        with MysqlTools().session_scope() as session:
            withdraw_list = None
            if page_flag == _THREE_S:  # 提现已完成列表
                w = session.query(ForeignWithdrawOrderRecordModel, UserAccountModel).filter_by(
                    **f_filters).filter(ForeignWithdrawOrderRecordModel.withdraw_amount >= withdraw_number,
                                        ForeignWithdrawOrderRecordModel.created_at >= apply_time_start,
                                        ForeignWithdrawOrderRecordModel.withdraw_type.in_([_ZERO_S, _ONE_S]),
                                        ForeignWithdrawOrderRecordModel.created_at <= apply_time_end,
                                        ForeignWithdrawOrderRecordModel.transfer_at >= transfer_time_start,
                                        ForeignWithdrawOrderRecordModel.transfer_at <= transfer_time_end).filter(
                    ForeignWithdrawOrderRecordModel.audit_status.in_([_ONE_S, _TWO_S])
                ).filter(
                    ForeignWithdrawOrderRecordModel.withdraw_status.in_(
                        [_TWO_S, _THREE_S, _FOUR_S, _FIVE_S])).outerjoin(
                    UserAccountModel,
                    ForeignWithdrawOrderRecordModel.account_id == UserAccountModel.account_id).filter_by(
                    **u_filters)
            elif page_flag == _TWO_S:  # 提现处理中
                w = session.query(ForeignWithdrawOrderRecordModel, UserAccountModel).filter_by(
                    **f_filters).filter(ForeignWithdrawOrderRecordModel.withdraw_amount >= withdraw_number,
                                        ForeignWithdrawOrderRecordModel.created_at >= apply_time_start,
                                        ForeignWithdrawOrderRecordModel.created_at <= apply_time_end,
                                        ForeignWithdrawOrderRecordModel.transfer_at >= transfer_time_start,
                                        ForeignWithdrawOrderRecordModel.transfer_at <= transfer_time_end).filter(
                    ForeignWithdrawOrderRecordModel.audit_status.in_([_ONE_S])
                ).filter(
                    ForeignWithdrawOrderRecordModel.withdraw_status.in_([_ONE_S])).outerjoin(
                    UserAccountModel,
                    ForeignWithdrawOrderRecordModel.account_id == UserAccountModel.account_id).filter_by(
                    **u_filters)
            elif page_flag == _ONE_S:  # 提现申请列表
                w = session.query(ForeignWithdrawOrderRecordModel, UserAccountModel).filter_by(
                    **f_filters).filter(ForeignWithdrawOrderRecordModel.withdraw_amount >= withdraw_number,
                                        ForeignWithdrawOrderRecordModel.created_at >= apply_time_start,
                                        ForeignWithdrawOrderRecordModel.created_at <= apply_time_end,
                                        ForeignWithdrawOrderRecordModel.transfer_at >= transfer_time_start,
                                        ForeignWithdrawOrderRecordModel.transfer_at <= transfer_time_end).filter(
                    ForeignWithdrawOrderRecordModel.audit_status.in_([_ZERO_S, _ONE_S])
                ).filter(
                    ForeignWithdrawOrderRecordModel.withdraw_status.in_([_ZERO_S])).outerjoin(
                    UserAccountModel,
                    ForeignWithdrawOrderRecordModel.account_id == UserAccountModel.account_id).filter_by(
                    **u_filters)

            withdraw_list = w.order_by(desc(ForeignWithdrawOrderRecordModel._id)).limit(limit).offset(
                get_offset_by_page(offset, limit))
            count = w.count()
            result_list = []
            for w in withdraw_list:
                map = {}
                map["order_no"] = str(w.ForeignWithdrawOrderRecordModel.order_no)
                map["coin_id"] = str(w.ForeignWithdrawOrderRecordModel.coin_id)
                map["withdraw_address"] = str(w.ForeignWithdrawOrderRecordModel.withdraw_address)
                map["withdraw_amount"] = decimal_to_str(w.ForeignWithdrawOrderRecordModel.withdraw_amount)
                map["withdraw_fee"] = decimal_to_str(w.ForeignWithdrawOrderRecordModel.withdraw_fee)
                map["audit_status"] = str(w.ForeignWithdrawOrderRecordModel.audit_status)
                map["withdraw_status"] = str(w.ForeignWithdrawOrderRecordModel.withdraw_status)
                map["user_name"] = ""
                try:
                    map["user_name"] = str(w.UserAccountModel.user_name)
                except:
                    pass
                map["apply_time"] = str(w.ForeignWithdrawOrderRecordModel.created_at)
                map["transfer_time"] = str(w.ForeignWithdrawOrderRecordModel.transfer_at)
                map["confirm_time"] = str(w.ForeignWithdrawOrderRecordModel.confirm_at)
                map["source_status"] = str(w.ForeignWithdrawOrderRecordModel.source_status)
                # map["withdraw_type"] = str(w.ForeignWithdrawOrderRecordModel.withdraw_type)
                map["from_address"] = str(w.ForeignWithdrawOrderRecordModel.from_address)
                map["account_id"] = str(w.ForeignWithdrawOrderRecordModel.account_id)
                result_list.append(map)
            result_map = {}
            result_map["count"] = str(count)
            result_map["list"] = result_list
            return result_map

    def withdraw_apply(self, order_no):
        """
        提现审核页面
        :param order_no: order_no
        :return:
        """
        with MysqlTools().session_scope() as session:
            w = session.query(ForeignWithdrawOrderRecordModel, UserAccountModel).filter(
                ForeignWithdrawOrderRecordModel.order_no == order_no).outerjoin(
                UserAccountModel,
                ForeignWithdrawOrderRecordModel.account_id == UserAccountModel.account_id).first()
            w2 = session.query(ForeignWithdrawOrderRecordModel).filter(
                ForeignWithdrawOrderRecordModel.order_no != order_no,
                ForeignWithdrawOrderRecordModel.account_id == w.ForeignWithdrawOrderRecordModel.account_id).order_by(
                ForeignWithdrawOrderRecordModel.created_at).first()
            map = {}
            map["order_no"] = str(w.ForeignWithdrawOrderRecordModel.order_no)
            map["coin_id"] = str(w.ForeignWithdrawOrderRecordModel.coin_id)
            map["withdraw_address"] = str(w.ForeignWithdrawOrderRecordModel.withdraw_address)
            map["user_name"] = ""
            try:
                map["user_name"] = str(w.UserAccountModel.user_name)
            except:
                pass
            map["withdraw_amount"] = decimal_to_str(w.ForeignWithdrawOrderRecordModel.withdraw_amount)
            map["audit_status"] = str(w.ForeignWithdrawOrderRecordModel.audit_status)
            map["expect_at"] = str(w.ForeignWithdrawOrderRecordModel.expect_at)
            map["apply_time"] = str(w.ForeignWithdrawOrderRecordModel.created_at)
            map["withdraw_fee"] = decimal_to_str(w.ForeignWithdrawOrderRecordModel.withdraw_fee)
            map["account_id"] = str(w.ForeignWithdrawOrderRecordModel.account_id)
            map["audit_status"] = str(w.ForeignWithdrawOrderRecordModel.audit_status)
            map["lately_time"] = ""
            try:
                map["lately_time"] = str(w2.created_at)
            except:
                pass
            return map

    def user_record(self, account_id, apply_time_start, apply_time_end, coin_id, withdraw_type, withdraw_address,
                    offset, limit):
        """
        用户提现流水
        :param apply_time_start: 操作时间start
        :param apply_time_end: 操作时间end
        :param coin_id: 币种
        :param withdraw_type: 提现类型
        :param withdraw_address: 收款地址
        :param offset: 当前页数
        :param limit: 每页条数
        :return:
        """
        # f_filters = {}
        # if account_id:
        #     f_filters["account_id"] = account_id
        # if coin_id:
        #     f_filters["coin_id"] = coin_id
        # if withdraw_type:
        #     f_filters["withdraw_type"] = withdraw_type
        # if withdraw_address:
        #     f_filters["withdraw_address"] = withdraw_address
        # if not apply_time_start:
        #     apply_time_start = "1970-01-01"
        # if not apply_time_end:
        #     apply_time_end = "2999-12-31"
        # with MysqlTools().session_scope() as session:
        #     withdraw_list = session.query(ForeignWithdrawOrderRecordModel, UserAccountModel).filter_by(
        #         **f_filters).filter(ForeignWithdrawOrderRecordModel.created_at >= apply_time_start,
        #                             ForeignWithdrawOrderRecordModel.created_at <= apply_time_end).outerjoin(
        #         UserAccountModel,
        #         ForeignWithdrawOrderRecordModel.account_id == UserAccountModel.account_id).limit(limit).offset(
        #         get_offset_by_page(offset, limit))
        #     count = withdraw_list.count()
        #     result_list = []
        #     for w in withdraw_list:
        #         map = {}
        #         map["order_no"] = str(w.ForeignWithdrawOrderRecordModel.order_no)
        #         map["user_name"] = ""
        #         try:
        #             map["user_name"] = str(w.UserAccountModel.user_name)
        #         except:
        #             pass
        #
        #         map["coin_id"] = str(w.ForeignWithdrawOrderRecordModel.coin_id)
        #         map["withdraw_address"] = str(w.ForeignWithdrawOrderRecordModel.withdraw_address)
        #         map["withdraw_amount"] = decimal_to_str(w.ForeignWithdrawOrderRecordModel.withdraw_amount)
        #         map["withdraw_fee"] = decimal_to_str(w.ForeignWithdrawOrderRecordModel.withdraw_fee)
        #         map["audit_status"] = str(w.ForeignWithdrawOrderRecordModel.audit_status)
        #         map["apply_time"] = str(w.ForeignWithdrawOrderRecordModel.created_at)
        #         map["account_id"] = str(w.ForeignWithdrawOrderRecordModel.account_id)
        #         result_list.append(map)
        #     result_map = {}
        #     result_map["count"] = str(count)
        #     result_map["list"] = result_list
        #     return result_map

    def audit_withdraw(self, order_no, audit_status, remark, audit_user):
        """
        提现审核接口
        :param order_no: order_no
        :param audit_status: 审核状态: 1-审核通过, 2-审核拒绝
        :param remark: 审核意见
        :param audit_user: 审核人账号
        :return:
        """
        with MysqlTools().session_scope() as session:
            q = session.query(ForeignWithdrawOrderRecordModel).filter(
                ForeignWithdrawOrderRecordModel.order_no == order_no)
            if audit_status == _ONE_S:
                q.update({
                    ForeignWithdrawOrderRecordModel.audit_status: audit_status,
                    ForeignWithdrawOrderRecordModel.remark: remark,
                    ForeignWithdrawOrderRecordModel.audit_user: audit_user,
                    ForeignWithdrawOrderRecordModel.audit_at: get_now_time()
                })
            else:
                q.update({
                    ForeignWithdrawOrderRecordModel.audit_status: audit_status,
                    ForeignWithdrawOrderRecordModel.remark: remark,
                    ForeignWithdrawOrderRecordModel.audit_user: audit_user,
                    ForeignWithdrawOrderRecordModel.audit_at: get_now_time(),
                    ForeignWithdrawOrderRecordModel.withdraw_status: _FIVE_S
                })
            session.commit()
            return

    def operation_withdraw(self, order_nos, source_status, from_address, verification_code, coin_id):
        """
        提现操作接口
        :param order_nos: 多个order_no使用","隔开
        :param source_status: 方式: 0-线上, 1-线下
        :param from_address: 出款地址: if (source_status == 0):{出款地址}else{空字符串}
        :param verification_code: 验证码: if (source_status == 0):{验证码}else{空字符串}
        :param coin_id: 币种: if (source_status == 0):{币种}else{空字符串}
        :return:
        """
        order_no_list = order_nos.split(",")
        with MysqlTools().session_scope() as session:
            if source_status == _ONE_S:  # 线下
                for order_no in order_no_list:
                    session.query(ForeignWithdrawOrderRecordModel).filter(
                        ForeignWithdrawOrderRecordModel.order_no == order_no).update({
                        ForeignWithdrawOrderRecordModel.source_status: source_status,
                        ForeignWithdrawOrderRecordModel.withdraw_status: _ONE_S
                    })
            elif source_status == _ZERO_S:  # 线上
                conf = get_config()
                env = conf["env"]
                if env == "pd":
                    vcode_service = VcodeService()
                    result = vcode_service.check_sms_email_vcode('common', verification_code)
                for order_no in order_no_list:
                    session.query(ForeignWithdrawOrderRecordModel).filter(
                        ForeignWithdrawOrderRecordModel.order_no == order_no).update({
                        ForeignWithdrawOrderRecordModel.source_status: source_status,
                        ForeignWithdrawOrderRecordModel.from_address: from_address
                    })
            session.commit()
            if source_status == _ZERO_S:  # 线上
                wfs = WalletForeignService()
                # 判断字符是否在db中
                model = None
                if coin_id == wfs.coin_id_btc:
                    model = WalletBtcGatherModel
                elif coin_id == wfs.coin_id_eth:
                    model = WalletEthGatherModel
                elif coin_id == wfs.coin_id_eos:
                    model = WalletEosGatherModel
                wallet = session.query(model).filter(model.sub_public_address == from_address).first()
                if wallet is None:
                    self.return_error(90005)
                withdraw = session.query(ForeignWithdrawOrderRecordModel).filter(
                    ForeignWithdrawOrderRecordModel.order_no.in_(order_no_list),
                    ForeignWithdrawOrderRecordModel.coin_id == coin_id,
                    ForeignWithdrawOrderRecordModel.withdraw_status == _ZERO_S,
                    ForeignWithdrawOrderRecordModel.audit_status == _ONE_S,
                    ForeignWithdrawOrderRecordModel.source_status == _ZERO_S
                )
                withdraw_list = withdraw.all()
                if len(withdraw_list) == 0:
                    self.return_error(90005)
                if coin_id == wfs.coin_id_btc:
                    wfs.btc_send_tx_multi(from_address, withdraw_list)
                elif coin_id == wfs.coin_id_eth:
                    wfs.eth_send_tx_multi(from_address, withdraw_list)
                elif coin_id == wfs.coin_id_eos:
                    wfs.eos_send_tx_multi(from_address, withdraw_list)
                session.commit()
            return

    def offline_tx(self, order_no, from_address, txid, transfer_at, coin_id, operation_user):
        """
        线下付款录入交易hash接口
        :param order_no: order_no
        :param from_address: 出账地址
        :param txid: 交易hash
        :param transfer_at: 转账时间
        :param coin_id: 币种
        :param operation_user: 操作人账号
        :return:
        """
        try:
            transfer_at = transfer_at
        finally:
            pass
        with MysqlTools().session_scope() as session:
            foreign_withdraw_order_record = session.query(ForeignWithdrawOrderRecordModel).filter(
                ForeignWithdrawOrderRecordModel.order_no == order_no).first()
            # 更新withdraw表状态
            foreign_withdraw_order_record.from_address = from_address
            foreign_withdraw_order_record.transfer_at = transfer_at
            foreign_withdraw_order_record.withdraw_status = _TWO_S
            foreign_withdraw_order_record.operation_user = operation_user
            model = None
            if coin_id == _ZERO_S:
                model = TxListeningBtcModel
            elif coin_id == _SIXTY_S:
                model = TxListeningEthModel
                txid = txid.strip()
                txid = txid[2:] if txid[:2] == "0x" else txid
            elif coin_id == _COIN_ID_EOS:
                model = TxListeningEosModel
                txid = txid.strip()
            tx_listening = model(
                order_no=generate_order_no(),
                record_no=foreign_withdraw_order_record.order_no,
                tx_no=txid,
                withdraw_type=foreign_withdraw_order_record.withdraw_type,
                source_status=foreign_withdraw_order_record.source_status,
                listen_flag=_ZERO
            )
            session.add(tx_listening)
            session.commit()

    def withdraw_details(self, order_no):
        """
        查看提现详情
        :param order_no: order_no
        :return:
        """
        with MysqlTools().session_scope() as session:
            q = session.query(ForeignWithdrawOrderRecordModel).filter(
                ForeignWithdrawOrderRecordModel.order_no == order_no).first()
            map = {}
            map["coin_id"] = str(q.coin_id)  # 币种
            map["withdraw_amount"] = str(q.withdraw_amount)  # 数量
            map["withdraw_fee"] = str(q.withdraw_fee)  # 手续费
            map["withdraw_address"] = str(q.withdraw_address)  # 提现地址
            map["created_at"] = str(q.created_at)  # 申请时间
            map["expect_at"] = str(q.expect_at)  # 期望到账时间
            map["audit_at"] = str(q.audit_at)  # 审核通过时间
            map["audit_user"] = str(q.audit_user)  # 审核人
            map["from_address"] = str(q.from_address)  # 出账地址`
            map["transfer_at"] = str(q.transfer_at)  # 出账时间
            map["confirm_at"] = str(q.confirm_at)  # 到账时间
            map["source_status"] = str(q.source_status)  # 转账方式
            map["withdraw_status"] = str(q.withdraw_status)  # 提现状态
            map["operation_user"] = str(q.operation_user)  # 操作人
            remark = ""
            memo = ""
            if q.remark:
                remark = q.remark
            map["remark"] = remark  # 备注
            if q.memo:
                memo = str(q.memo)  # 操作人
            map["memo"] = memo  # 备注

            q2 = None
            if str(q.coin_id) == _ZERO_S:  # BTC
                q2 = session.query(TxListeningBtcModel).filter(TxListeningBtcModel.record_no == order_no).first()
            elif str(q.coin_id) == _SIXTY_S:  # ETH
                q2 = session.query(TxListeningEthModel).filter(TxListeningEthModel.record_no == order_no).first()
            elif str(q.coin_id) == _COIN_ID_EOS:  # Eos
                q2 = session.query(TxListeningEosModel).filter(TxListeningEosModel.record_no == order_no).first()
            if q2 is not None:
                map["txid"] = str(q2.tx_no)  # 交易hash
            return map

    def get_account_water(self, account_id, start_at=None, end_at=None, coin_id=None, change_type=None, address=None,
                          page_num=1, page_limit=10):
        if change_type \
                and change_type not in AccountChangeRecordModel.get_all_show_change_type() \
                and change_type not in AccountChangeRecordModel.get_all_withdraw_change_type():
            self.return_error(35032)
        page_offset = get_offset_by_page(page_num, page_limit)
        page_limit = str(page_limit)
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
                AccountChangeRecordModel.account_id == account_id,
            )

            # 查询时间
            if start_at is not None:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.created_at >= start_at,
                )
            if end_at is not None:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.created_at <= end_at,
                )
            # 查询币种
            if coin_id is not None:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.token_id == coin_id,
                )
            # 操作类型
            if change_type and change_type == AccountChangeRecordModel.change_type_withdraw_all:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.change_type.in_(
                        AccountChangeRecordModel.get_all_withdraw_change_type())
                )
            elif change_type:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.change_type == change_type
                )
            # 查询地址
            if address is not None:
                record_condition = record_condition.filter(
                    AccountChangeRecordModel.token_address == address,
                )

            record_condition = record_condition.order_by(
                desc(AccountChangeRecordModel.created_at))

            # 计算不分页的总页数
            record_count = record_condition.count()
            result_dict['count'] = get_page_by_offset(record_count, page_limit)

            # 6 拼接分页
            record_condition = record_condition.limit(page_limit).offset(
                page_offset)

            record_list = record_condition.all()

            for one_record in record_list:
                show_change_amount = one_record.AccountChangeRecordModel.change_amount
                if one_record.AccountChangeRecordModel.change_type in AccountChangeRecordModel.get_all_withdraw_change_type():
                    show_change_amount += one_record.AccountChangeRecordModel.change_fee
                result_dict['content'].append({
                    'change_type': one_record.AccountChangeRecordModel.change_type,
                    'id': one_record.AccountChangeRecordModel._id,
                    'water_id': one_record.AccountChangeRecordModel.account_change_record_id,
                    # 'user_id': one_record.user_id,
                    'user_name': one_record.user_name,
                    # 'token_id': one_record.AccountChangeRecordModel.token_id,
                    'token_name': one_record.coin_name,
                    # 'change_amount': decimal_to_client(
                    #     one_record.AccountChangeRecordModel.change_amount),
                    # 'change_fee': decimal_to_client(
                    #     one_record.AccountChangeRecordModel.change_fee),
                    # 'change_number': one_record.AccountChangeRecordModel.change_number,
                    'finish_time': str(
                        one_record.AccountChangeRecordModel.finish_time),
                    'address': one_record.AccountChangeRecordModel.token_address,
                    'show_change_amount': decimal_to_client(show_change_amount),
                    'source': one_record.AccountChangeRecordModel.source,
                })

            return result_dict


def test_account_withdraw():
    wfs = WalletForeignService()

    # "req_no", "account_id", "coin_id", "withdraw_address", "withdraw_amount", "withdraw_gas_price", "withdraw_type"
    args = {
        "req_no": generate_order_no(),
        "account_id": "2018111309375761185989916621239257168264426978617039743301831998",
        "coin_id": "60",
        "withdraw_address": "0x74735BaeF98eA37749B19bBe58860A50A8122553",
        "withdraw_amount": get_decimal("0.000000001 "),
        "withdraw_fee": get_decimal("0.000021 ", 18) * get_decimal(21000),
        "withdraw_type": "0"
    }
    res = wfs.generate_withdraw_order(args)
    print(res)


def test_audit_withdraw():
    wws = WalletWithdrawService()
    # order_no = "20181211105701556657604297563053"
    order_no_list = ["20181211112408322855839592579970", "20181211112435595287049290915930",
                     "20181211112458558612738700404520"]
    audit_status = "1"
    remark = ""
    audit_user = "7507a61d22f64ae29b9ce36585bcc289"
    for order_no in order_no_list:
        wws.audit_withdraw(order_no, audit_status, remark, audit_user)
    print("success")


def test_operation_withdraw():
    wws = WalletWithdrawService()
    # order_nos = "20181211112408322855839592579970,20181211112435595287049290915930,20181211112458558612738700404520"
    order_nos = "20190107044612151059271579417969"
    source_status = "0"
    from_address = "0x0F9Df23deC74aD7afceDdC0af39b1FF00D868d2B"
    verification_code = "1"
    coin_id = "194"
    wws.operation_withdraw(order_nos, source_status, from_address, verification_code, coin_id)
    print("success")


def test_eth_get_gas_price():
    wws = WalletForeignService()
    gas_price = wws.eth_get_gas_price()
    gas = wws.eth_get_gas()
    print("gas_price")
    print(gas_price)
    print("gas")
    print(gas)


def test_operation_gather():
    wfs = WalletForeignService()
    order_list = [
        "20190107044612151059271579417969"
    ]
    with MysqlTools().session_scope() as session:
        foreign_withdraw_order_record_list = session.query(ForeignWithdrawOrderRecordModel).filter(
            ForeignWithdrawOrderRecordModel.order_no.in_(order_list)).all()
        for withdraw in foreign_withdraw_order_record_list:
            # res = wfs.eth_send_tx(withdraw)
            res = wfs.eos_send_tx(withdraw)
            print(res)
    return


if __name__ == "__main__":
    pass
    # 测试手续费
    # test_eth_get_gas_price()

    # 测试提现申请
    # test_account_withdraw()

    # 测试提现审核
    # test_audit_withdraw()

    # 测试批量提现
    test_operation_withdraw()

    # 用户归集操作
    test_operation_gather()
