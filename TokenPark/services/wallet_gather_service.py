import json

from sqlalchemy import or_

from common_settings import *
from models.foreign_gather_record_model import ForeignGatherRecordModel
from models.foreign_withdraw_order_record_model import ForeignWithdrawOrderRecordModel
from models.token_coin_model import TokenCoinModel
from models.token_conf_model import TokenConfModel
from models.user_account_model import UserAccountModel
from models.wallet_btc_gather_model import WalletBtcGatherModel
from models.wallet_btc_model import WalletBtcModel
from models.wallet_eos_gather_model import WalletEosGatherModel
from models.wallet_eth_gather_model import WalletEthGatherModel
from models.wallet_eth_model import WalletEthModel
from services.base_service import BaseService
from services.wallet_foreign_service import WalletForeignService
from tools.mysql_tool import MysqlTools
from utils.util import decimal_to_str
from utils.util import generate_order_no
from utils.util import get_offset_by_page
from services.vcode_service import VcodeService
from config import get_config
import datetime
from sqlalchemy import desc
from utils.time_util import get_utc_now


# 归集后台相关
class WalletGatherService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def gather_address_list(self, sub_public_address, coin_id, update_at_start, update_at_end, status, offset, limit):
        """
        归集地址列表
        :param sub_public_address: 地址
        :param coin_id: 币种(必填)
        :param update_at_start: 最近一次变动时间start
        :param update_at_end: 最近一次变动时间end
        :param status: 启用状态:0-停用, 1-启用
        :param offset: 当前页数
        :param limit: 每页条数
        :return:
        """
        filters = {}
        if sub_public_address:
            filters["sub_public_address"] = sub_public_address
        filters["coin_id"] = coin_id
        if not update_at_start:
            update_at_start = "0000-00-00"
        else:
            update_at_start = update_at_start
        if not update_at_end:
            update_at_end = "2999-12-31"
        else:
            update_at_end = update_at_end
        if status:
            filters["status"] = status
        with MysqlTools().session_scope() as session:
            if coin_id == _ZERO_S:
                model = WalletBtcGatherModel
            elif coin_id == _SIXTY_S:
                model = WalletEthGatherModel
            elif coin_id == _COIN_ID_EOS:
                model = WalletEosGatherModel
            g = session.query(model).filter_by(**filters).filter(
                model.update_at >= update_at_start,
                model.update_at <= update_at_end)
            count = g.count()
            if int(offset) == 0:
                gather_list = g
            else:
                gather_list = g.limit(
                    limit).offset(get_offset_by_page(offset, limit))
            result_list = []
            for g in gather_list:
                map = {}
                map["sub_public_address"] = str(g.sub_public_address)
                map["coin_id"] = str(coin_id)
                map["amount"] = decimal_to_str(g.amount)
                map["amount_change"] = decimal_to_str(g.amount_change)
                map["status"] = str(g.status)
                map["update_at"] = str(g.update_at)
                result_list.append(map)
            result_map = {}
            result_map["count"] = str(count)
            result_map["list"] = result_list
            return result_map

    def gather_address_record(self, sub_public_address, relevant_address, transfer_at_start, transfer_at_end,
                              operation_type, offset,
                              limit):
        """
        归集地址流水
        :param sub_public_address: 地址(必填)
        :param relevant_address: 相关地址
        :param transfer_at_start: 操作时间start
        :param transfer_at_end: 操作时间end
        :param operation_type: 操作类型:1-收款, 2-出款[提现类型: 0-用户提现, 1-用户中奖, 2-归集, 3-归集转归集]
        :param offset: 当前页数
        :param limit: 每页条数
        :return:
        """
        if not transfer_at_start:
            transfer_at_start = "0000-00-00"
        else:
            transfer_at_start = transfer_at_start
        if not transfer_at_end:
            transfer_at_end = "2999-12-31"
        else:
            transfer_at_end = transfer_at_end
        with MysqlTools().session_scope() as session:
            coin_id = _ZERO_S
            gather = session.query(WalletBtcGatherModel).filter(
                WalletBtcGatherModel.sub_public_address == sub_public_address).first()
            if gather is None:
                coin_id = _SIXTY_S
            f = session.query(ForeignWithdrawOrderRecordModel, UserAccountModel).filter(
                ForeignWithdrawOrderRecordModel.transfer_at >= transfer_at_start,
                ForeignWithdrawOrderRecordModel.transfer_at <= transfer_at_end)
            if relevant_address:
                f = f.filter(or_(
                    ForeignWithdrawOrderRecordModel.from_address == relevant_address,
                    ForeignWithdrawOrderRecordModel.withdraw_address == relevant_address))
            if not operation_type:  # 全部
                fw = f.outerjoin(
                    UserAccountModel,
                    ForeignWithdrawOrderRecordModel.account_id == UserAccountModel.account_id)
            elif operation_type == _ONE_S:  # 收款
                fw = f.filter(
                    ForeignWithdrawOrderRecordModel.withdraw_type == _TWO_S).outerjoin(
                    UserAccountModel,
                    ForeignWithdrawOrderRecordModel.account_id == UserAccountModel.account_id)
            elif operation_type == _TWO_S:  # 出款
                fw = f.filter(
                    ForeignWithdrawOrderRecordModel.withdraw_type == _ZERO_S).outerjoin(
                    UserAccountModel,
                    ForeignWithdrawOrderRecordModel.account_id == UserAccountModel.account_id)
            count = fw.count()
            record_list = fw.order_by(desc(ForeignWithdrawOrderRecordModel.transfer_at)).limit(
                limit).offset(get_offset_by_page(offset, limit))
            result_list = []
            for r in record_list:
                map = {}
                map["order_no"] = str(r.ForeignWithdrawOrderRecordModel.order_no)
                map["user_name"] = ""
                try:
                    map["user_name"] = str(r.UserAccountModel.user_name)
                except:
                    pass
                map["transfer_at"] = str(r.ForeignWithdrawOrderRecordModel.transfer_at)
                map["withdraw_amount"] = decimal_to_str(r.ForeignWithdrawOrderRecordModel.withdraw_amount)
                map["withdraw_fee"] = decimal_to_str(r.ForeignWithdrawOrderRecordModel.withdraw_fee)
                map["operation_type"] = ""
                map["relevant_address"] = ""
                withdraw_type = str(r.ForeignWithdrawOrderRecordModel.withdraw_type)
                from_address = str(r.ForeignWithdrawOrderRecordModel.from_address)
                withdraw_address = str(r.ForeignWithdrawOrderRecordModel.withdraw_address)
                if withdraw_type == _ZERO_S:  # 提现
                    map["operation_type"] = "2"  # 出款
                    map["relevant_address"] = withdraw_address
                elif withdraw_type == _TWO_S:  # 归集
                    map["operation_type"] = "1"  # 收款
                    map["relevant_address"] = from_address
                map["operation_user"] = str(r.ForeignWithdrawOrderRecordModel.operation_user)
                result_list.append(map)
            result_map = {}
            result_map["count"] = str(count)
            result_map["list"] = result_list
            return result_map

    def sub_address_list(self, user_name, sub_public_address, conditions, coin_id, offset, limit):
        """
        子账户地址列表
        :param user_name: 用户名
        :param sub_public_address: 钱包地址
        :param conditions: 归集条件(大于等于xx个单位)
        :param coin_id: 币种(必填)
        :param offset: 当前页数
        :param limit: 每页条数
        :return:
        """
        f_filters = {}
        u_filters = {}
        if user_name:
            u_filters["user_name"] = user_name
        if sub_public_address:
            f_filters["sub_public_address"] = sub_public_address
        if not conditions:
            conditions = 0
        with MysqlTools().session_scope() as session:
            model = None
            if coin_id == _ZERO_S:
                model = WalletBtcModel
            elif coin_id == _SIXTY_S:
                model = WalletEthModel
            w = session.query(model, UserAccountModel).filter(
                model.amount >= conditions, model.account_id != "").filter_by(**f_filters).outerjoin(
                UserAccountModel,
                model.account_id == UserAccountModel.account_id).filter_by(**u_filters)
            count = w.count()
            # 计算可归集总额
            total_amount = 0
            for o in w:
                amount = 0
                if coin_id == _ZERO_S:
                    amount = o.WalletBtcModel.amount
                elif coin_id == _SIXTY_S:
                    amount = o.WalletEthModel.amount
                total_amount = total_amount + amount

            wallet_list = w.limit(
                limit).offset(get_offset_by_page(offset, limit))
            result_list = []
            for w in wallet_list:
                map = {}
                map["user_name"] = ""
                try:
                    map["user_name"] = str(w.UserAccountModel.user_name)
                except:
                    pass
                map["coin_id"] = coin_id
                amount = 0
                if coin_id == _ZERO_S:
                    map["sub_public_address"] = str(w.WalletBtcModel.sub_public_address)
                    amount = w.WalletBtcModel.amount
                    map["amount"] = decimal_to_str(amount)
                    map["amount_frozen"] = decimal_to_str(w.WalletBtcModel.amount_frozen)
                elif coin_id == _SIXTY_S:
                    map["sub_public_address"] = str(w.WalletEthModel.sub_public_address)
                    amount = w.WalletEthModel.amount
                    map["amount"] = decimal_to_str(amount)
                    map["amount_frozen"] = decimal_to_str(w.WalletEthModel.amount_frozen)
                result_list.append(map)
            result_map = {}
            result_map["count"] = str(count)
            result_map["total_amount"] = decimal_to_str(total_amount)
            result_map["list"] = result_list
            return result_map

    def operation_gather(self, user_name, sub_public_address, conditions, coin_id, to_address, verification_code):
        """
        归集操作
        :param user_name: 用户名
        :param sub_public_address: 钱包地址
        :param conditions: 归集条件(大于等于xx个单位)
        :param coin_id: 币种(必填)
        :param to_address: 归集账户
        :param verification_code: 验证码
        :return:
        """
        conf = get_config()
        env = conf["env"]
        if env == "pd":
            vcode_service = VcodeService()
            result = vcode_service.check_sms_email_vcode('common', verification_code)
        f_filters = {}
        u_filters = {}
        if user_name:
            u_filters["user_name"] = user_name
        if sub_public_address:
            f_filters["sub_public_address"] = sub_public_address
        if not conditions:
            conditions = 0
        wfs = WalletForeignService()

        with MysqlTools().session_scope() as session:
            model = None
            if coin_id == _ZERO_S:
                model = WalletBtcModel
            elif coin_id == _SIXTY_S:
                model = WalletEthModel
            # token_conf = session.query(TokenConfModel).filter(TokenConfModel.coin_id == coin_id).first()
            # gather_minimum_amount = token_conf.gather_minimum_amount
            gather_minimum_amount = wfs.eth_get_gas()

            wallet_list = session.query(model, UserAccountModel).filter(
                model.amount >= conditions, model.account_id != "").filter_by(**f_filters).outerjoin(
                UserAccountModel,
                model.account_id == UserAccountModel.account_id).filter_by(**u_filters)
            total_amount = 0
            available_wallet_list = []
            for w in wallet_list:
                amount = 0
                if coin_id == _ZERO_S:
                    amount = w.WalletBtcModel.amount
                elif coin_id == _SIXTY_S:
                    amount = w.WalletEthModel.amount
                if gather_minimum_amount < amount:
                    available_wallet_list.append(w)
                    total_amount = total_amount + amount

            record_id = generate_order_no()
            foreign_gather_record = ForeignGatherRecordModel(
                record_id=record_id,
                coin_id=coin_id,
                public_address=to_address,
                conditions=conditions,
                purpose_amount=total_amount
            )
            session.add(foreign_gather_record)
            foreign_withdraw_order_record_list = []
            wallet_list = available_wallet_list
            if coin_id == _ZERO_S:
                for wallet in wallet_list:
                    if wallet.WalletBtcModel.amount > 0:
                        foreign_withdraw_order_record = ForeignWithdrawOrderRecordModel(
                            order_no=generate_order_no(),
                            relate_flow_no=foreign_gather_record.record_id,
                            account_id=wallet.WalletBtcModel.account_id,
                            coin_id=coin_id,
                            from_address=wallet.WalletBtcModel.sub_public_address,
                            withdraw_address=to_address,
                            withdraw_amount=wallet.WalletBtcModel.amount,
                            withdraw_type=_TWO,
                            withdraw_status=_ZERO,
                            audit_status=_ONE,
                            source_status=_ONE
                        )
                        foreign_withdraw_order_record_list.append(foreign_withdraw_order_record)
            elif coin_id == _SIXTY_S:
                for wallet in wallet_list:
                    if wallet.WalletEthModel.amount > 0:
                        foreign_withdraw_order_record = ForeignWithdrawOrderRecordModel(
                            order_no=generate_order_no(),
                            relate_flow_no=foreign_gather_record.record_id,
                            account_id=wallet.WalletEthModel.account_id,
                            coin_id=coin_id,
                            from_address=wallet.WalletEthModel.sub_public_address,
                            withdraw_address=to_address,
                            withdraw_amount=wallet.WalletEthModel.amount,
                            withdraw_type=_TWO,
                            withdraw_status=_ZERO,
                            audit_status=_ONE,
                            source_status=_ONE
                        )
                        foreign_withdraw_order_record_list.append(foreign_withdraw_order_record)
            session.add_all(foreign_withdraw_order_record_list)
            session.commit()

            if coin_id == _ZERO_S:  # 比特币
                for withdraw in foreign_withdraw_order_record_list:
                    wfs.btc_send_tx(withdraw)
            elif coin_id == _SIXTY_S:  # 以太坊
                for withdraw in foreign_withdraw_order_record_list:
                    wfs.eth_send_tx(withdraw)
            return

    def gather_record(self, public_address, coin_id, operate_at_start, operate_at_end, offset, limit):
        """
        归集操作记录
        :param public_address: 归集地址
        :param coin_id: 币种
        :param operate_at_start: 操作时间start
        :param operate_at_end: 操作时间end
        :param offset: 当前页数
        :param limit: 每页条数
        :return:
        """
        filters = {}
        if public_address:
            filters["public_address"] = public_address
        if coin_id:
            filters["coin_id"] = coin_id
        if not operate_at_start:
            operate_at_start = "0000-00-00"
        else:
            operate_at_start = operate_at_start
        if not operate_at_end:
            operate_at_end = "2999-12-31"
        else:
            operate_at_end = operate_at_end
        with MysqlTools().session_scope() as session:
            g = session.query(ForeignGatherRecordModel).filter_by(**filters).filter(
                ForeignGatherRecordModel.created_at >= operate_at_start,
                ForeignGatherRecordModel.created_at <= operate_at_end)
            count = g.count()
            gather_list = g.order_by(desc(ForeignGatherRecordModel._id)).limit(
                limit).offset(get_offset_by_page(offset, limit))
            result_list = []
            for g in gather_list:
                map = {}
                map["record_id"] = str(g.record_id)  # ID
                map["created_at"] = str(g.created_at)  # 操作时间
                map["coin_id"] = str(g.coin_id)  # 币种
                map["amount"] = decimal_to_str(g.purpose_amount)  # 数量
                map["fee"] = decimal_to_str(g.actual_fee)  # 归集手续费
                withdraw_list = session.query(ForeignWithdrawOrderRecordModel).filter(
                    ForeignWithdrawOrderRecordModel.relate_flow_no == g.record_id)
                map["number"] = str(withdraw_list.count())  # 操作账号数量
                map["public_address"] = str(g.public_address)  # 归集地址
                result_list.append(map)
            result_map = {}
            result_map["count"] = str(count)
            result_map["list"] = result_list
            return result_map

    def gather_record_details(self, record_id, user_name, from_address, operate_at_start, operate_at_end,
                              withdraw_status,
                              confirm_at_start, confirm_at_end, offset, limit):
        """
        归集操作记录详情
        :param record_id: record_id
        :param user_name: 用户名
        :param from_address: 用户钱包地址
        :param operate_at_start: 操作时间start
        :param operate_at_end: 操作时间end
        :param withdraw_status: 状态: 1-归集中, 2-成功, 3-失败
        :param confirm_at_start: 结束时间start
        :param confirm_at_end: 结束时间end
        :param offset: 当前页数
        :param limit: 每页条数
        :return:
        """
        u_filters = {}
        if user_name:
            u_filters["user_name"] = user_name

        f_filters = {}
        f_filters["relate_flow_no"] = record_id
        if from_address:
            f_filters["from_address"] = from_address
        if withdraw_status:
            f_filters["withdraw_status"] = withdraw_status
        if not operate_at_start:
            operate_at_start = "0000-00-00"
        else:
            operate_at_start = operate_at_start
        if not operate_at_end:
            operate_at_end = "2999-12-31"
        else:
            operate_at_end = operate_at_end
        if not confirm_at_start:
            confirm_at_start = "0000-00-00"
        else:
            confirm_at_start = confirm_at_start
        if not confirm_at_end:
            confirm_at_end = "2999-12-31"
        else:
            confirm_at_end = confirm_at_end
        with MysqlTools().session_scope() as session:
            gather_model = session.query(ForeignGatherRecordModel).filter(
                ForeignGatherRecordModel.record_id == record_id).first()
            result_map = {}
            info = {}
            info["coin_id"] = str(gather_model.coin_id)
            info["amount"] = decimal_to_str(gather_model.actual_amount)
            info["fee"] = decimal_to_str(gather_model.actual_fee)
            withdraw_list = session.query(ForeignWithdrawOrderRecordModel).filter(
                ForeignWithdrawOrderRecordModel.relate_flow_no == record_id)
            info["number"] = str(withdraw_list.count())  # 操作账号数量
            info["created_at"] = str(gather_model.created_at)
            info["public_address"] = str(gather_model.public_address)
            result_map["info"] = info
            g = session.query(ForeignWithdrawOrderRecordModel, UserAccountModel).filter_by(
                **f_filters).filter(
                ForeignWithdrawOrderRecordModel.created_at >= operate_at_start,
                ForeignWithdrawOrderRecordModel.created_at <= operate_at_end,
                ForeignWithdrawOrderRecordModel.confirm_at >= confirm_at_start,
                ForeignWithdrawOrderRecordModel.confirm_at <= confirm_at_end).outerjoin(
                UserAccountModel,
                ForeignWithdrawOrderRecordModel.account_id == UserAccountModel.account_id).filter_by(**u_filters)
            count = g.count()
            gather_list = g.limit(
                limit).offset(get_offset_by_page(offset, limit))
            list = []
            for g in gather_list:
                map = {}
                map["user_name"] = ""
                try:
                    map["user_name"] = str(g.UserAccountModel.user_name)  # 用户名
                except:
                    pass
                map["from_address"] = str(g.ForeignWithdrawOrderRecordModel.from_address)  # 用户钱包地址
                map["created_at"] = str(g.ForeignWithdrawOrderRecordModel.created_at)  # 操作时间
                map["coin_id"] = str(g.ForeignWithdrawOrderRecordModel.coin_id)  # 币种
                map["withdraw_amount"] = decimal_to_str(g.ForeignWithdrawOrderRecordModel.withdraw_amount)  # 数量
                map["withdraw_fee"] = decimal_to_str(g.ForeignWithdrawOrderRecordModel.withdraw_fee)  # 手续费
                map["confirm_at"] = str(g.ForeignWithdrawOrderRecordModel.confirm_at)  # 结束时间
                map["withdraw_address"] = str(g.ForeignWithdrawOrderRecordModel.withdraw_address)  # 归集地址
                map["withdraw_status"] = str(g.ForeignWithdrawOrderRecordModel.withdraw_status)  # 状态
                list.append(map)
            result_map["count"] = count
            result_map["list"] = list
            return result_map

    def gather_record_all(self, user_name, from_address, operate_at_start, operate_at_end, withdraw_address, coin_id,
                          confirm_at_start, confirm_at_end, withdraw_status, offset, limit):
        """
        归集操作记录详情
        :param user_name: 用户名
        :param from_address: 用户钱包地址
        :param operate_at_start: 操作时间start
        :param operate_at_end: 操作时间end
        :param withdraw_address: 归集地址
        :param coin_id: 币种
        :param confirm_at_start: 结束时间start
        :param confirm_at_end: 结束时间end
        :param withdraw_status: 状态: 1-归集中, 2-成功, 3-失败
        :param offset: 当前页数
        :param limit: 每页条数
        :return:
        """
        u_filters = {}
        if user_name:
            u_filters["user_name"] = user_name

        f_filters = {}
        f_filters["withdraw_type"] = _TWO_S
        if from_address:
            f_filters["from_address"] = from_address
        if withdraw_address:
            f_filters["withdraw_address"] = withdraw_address
        if coin_id:
            f_filters["coin_id"] = coin_id
        if withdraw_status:
            f_filters["withdraw_status"] = withdraw_status
        if not operate_at_start:
            operate_at_start = "0000-00-00"
        else:
            operate_at_start = operate_at_start
        if not operate_at_end:
            operate_at_end = "2999-12-31"
        else:
            operate_at_end = operate_at_end
        if not confirm_at_start:
            confirm_at_start = "0000-00-00"
        else:
            confirm_at_start = confirm_at_start
        if not confirm_at_end:
            confirm_at_end = "2999-12-31"
        else:
            confirm_at_end = confirm_at_end
        with MysqlTools().session_scope() as session:
            g = session.query(ForeignWithdrawOrderRecordModel, UserAccountModel).filter_by(
                **f_filters).filter(
                ForeignWithdrawOrderRecordModel.created_at >= operate_at_start,
                ForeignWithdrawOrderRecordModel.created_at <= operate_at_end,
                ForeignWithdrawOrderRecordModel.confirm_at >= confirm_at_start,
                ForeignWithdrawOrderRecordModel.confirm_at <= confirm_at_end).outerjoin(
                UserAccountModel,
                ForeignWithdrawOrderRecordModel.account_id == UserAccountModel.account_id).filter_by(**u_filters)
            count = g.count()
            gather_list = g.order_by(desc(ForeignWithdrawOrderRecordModel._id)).limit(
                limit).offset(get_offset_by_page(offset, limit))
            result_map = {}
            list = []
            for g in gather_list:
                map = {}
                map["user_name"] = ""
                try:
                    map["user_name"] = str(g.UserAccountModel.user_name)  # 用户名
                except:
                    pass
                map["order_no"] = str(g.ForeignWithdrawOrderRecordModel.order_no)
                map["from_address"] = str(g.ForeignWithdrawOrderRecordModel.from_address)  # 用户钱包地址
                map["created_at"] = str(g.ForeignWithdrawOrderRecordModel.created_at)  # 操作时间
                map["coin_id"] = str(g.ForeignWithdrawOrderRecordModel.coin_id)  # 归集币种
                map["withdraw_amount"] = decimal_to_str(g.ForeignWithdrawOrderRecordModel.withdraw_amount)  # 数量
                map["withdraw_fee"] = decimal_to_str(g.ForeignWithdrawOrderRecordModel.withdraw_fee)  # 手续费
                map["confirm_at"] = str(g.ForeignWithdrawOrderRecordModel.confirm_at)  # 结束时间
                map["withdraw_address"] = str(g.ForeignWithdrawOrderRecordModel.withdraw_address)  # 归集地址
                map["withdraw_status"] = str(g.ForeignWithdrawOrderRecordModel.withdraw_status)
                list.append(map)
            result_map["count"] = count
            result_map["list"] = list
            return result_map

    def gather_to_gather(self, coin_id, from_address, amount, to_address, verification_code):
        """
        归集转归集
        :param coin_id: 币种
        :param from_address: 待归集地址
        :param amount: 归集数量
        :param to_address: 收款地址
        :param verification_code: 验证码
        :return:
        """
        conf = get_config()
        env = conf["env"]
        if env == "pd":
            vcode_service = VcodeService()
            result = vcode_service.check_sms_email_vcode('common', verification_code)
        with MysqlTools().session_scope() as session:
            record_id = generate_order_no()
            foreign_gather_record = ForeignGatherRecordModel(
                record_id=record_id,
                public_address=to_address,
                purpose_amount=amount,
                gather_status=_FOUR_S
            )
            session.add(foreign_gather_record)
            gather_record_id = foreign_gather_record.record_id
            order_no = generate_order_no()
            withdraw = ForeignWithdrawOrderRecordModel(
                order_no=order_no,
                relate_flow_no=gather_record_id,
                coin_id=coin_id,
                from_address=from_address,
                withdraw_address=to_address,
                withdraw_amount=amount,
                withdraw_type=_THREE_S,
                withdraw_status=_ZERO_S,
                audit_status=_ONE_S,
                source_status=_ZERO_S,
                transfer_at=get_utc_now()
            )
            session.add(withdraw)
            session.commit()
            withdraw_order_no = withdraw.order_no
            withdraw = session.query(ForeignWithdrawOrderRecordModel).filter(
                ForeignWithdrawOrderRecordModel.order_no == order_no).first()
            wfs = WalletForeignService()
            send_result = None
            if coin_id == _ZERO_S:  # 比特币
                send_result = wfs.btc_send_tx(withdraw)
            elif coin_id == _SIXTY_S:  # 以太坊
                send_result = wfs.eth_send_tx(withdraw)

            if send_result is True:
                gather_record_model = session.query(ForeignGatherRecordModel).filter(ForeignGatherRecordModel.record_id == gather_record_id).first()
                gather_record_model.gather_status = _ONE_S
                withdraw_reocrd_model = session.query(ForeignWithdrawOrderRecordModel).filter(ForeignWithdrawOrderRecordModel.order_no == withdraw_order_no).first()
                withdraw_reocrd_model.withdraw_status = _ONE_S
                session.commit()
            return
