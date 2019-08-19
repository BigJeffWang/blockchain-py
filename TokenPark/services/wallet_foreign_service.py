import decimal

from Crypto.Hash import keccak
from bitcoinrpc.authproxy import JSONRPCException
from sqlalchemy import desc
from sqlalchemy import or_

from common_settings import *
from config import get_config
from config import get_sms_email
from config import get_wallet_center
from models.account_change_record_model import AccountChangeRecordModel
from models.foreign_assign_address_record_model import ForeignAssignAddressRecordModel
from models.foreign_gather_record_model import ForeignGatherRecordModel
from models.foreign_multi_withdraw_record_model import ForeignMultiWithdrawRecordModel
from models.foreign_withdraw_order_record_model import ForeignWithdrawOrderRecordModel
from models.game_digital_instance_model import GameDigitalInstanceModel
from models.game_numbers_set_model import GameNumbersSetModel
from models.participate_in_model import ParticipateInModel
from models.token_coin_model import TokenCoinModel
from models.token_conf_model import TokenConfModel
from models.token_node_conf_model import TokenNodeConfModel
from models.tx_list_btc_model import TxListBtcModel
from models.tx_listening_btc_model import TxListeningBtcModel
from models.tx_listening_eos_model import TxListeningEosModel
from models.tx_listening_eth_model import TxListeningEthModel
from models.user_account_model import UserAccountModel
from models.user_account_token_model import UserAccountTokenModel
from models.wallet_btc_gather_model import WalletBtcGatherModel
from models.wallet_btc_model import WalletBtcModel
from models.wallet_eos_gather_model import WalletEosGatherModel
from models.wallet_eth_gather_model import WalletEthGatherModel
from models.wallet_eth_model import WalletEthModel
from models.wallet_eos_model import WalletEosModel
from services.base_service import BaseService
from services.vcode_service import VcodeService
from tools.mysql_tool import MysqlTools
from tools.tool import super_json_dumps
from utils.log import raise_logger
from utils.time_util import get_utc_now, get_datetime_now_offset
from utils.util import generate_order_no
from utils.util import get_decimal, do_post, get_now_time, decimal_to_str, decimal_to_client, \
    format_utc, decimal_two
from utils.util import send_mail
from config import get_env


class WalletEModel(object):
    pass


class WalletForeignService(BaseService):
    symbol_to_model = {
        _BTC: [WalletBtcModel],
        _ETH: [WalletEthModel],
        _EOS: [WalletEosModel],
        _COIN_ID_BTC: [WalletBtcModel],
        _COIN_ID_ETH: [WalletEthModel],
        _COIN_ID_EOS: [WalletEosModel],
    }
    coin_id_btc = _ZERO_S  # btc 0
    coin_id_eth = _SIXTY_S  # eth 60
    coin_id_eos = _COIN_ID_EOS  # eos 194
    withdraw_status_process_ing = _ONE_S  # 1 - 提现中
    withdraw_status_process_fail = _FOUR_S  # 4-交易失败
    withdraw_status_part_transaction_success = _SIX_S  # 6-部分交易成功
    eos_recharge_address = _EOS_RECHARGE_ADDRESS[get_env()]
    eos_unit = "EOS"
    eth_unit = "ether"  # 数据库以太坊计量单位手续费显示单位
    eth_block_time = 20  # eth 5秒生成一个区块
    token_conf = None
    gwei = 1e9
    account_withdraw_type_list = [_ZERO_S, _ONE_S]
    gather_withdraw_type_list = [_TWO_S, _THREE_S]
    private_url = get_wallet_center()["private_url"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rpc = None
        self.w3 = None
        with MysqlTools().session_scope() as session:
            self.token_conf = session.query(TokenConfModel).filter(TokenConfModel.coin_id == self.coin_id_eth).first()
            if not self.token_conf:
                raise Exception("TokenConfModel not have related configuration data")

    def block_chain_connect(self):
        # w3 = Web3(Web3.HTTPProvider(self.node_url))
        # w3.middleware_stack.inject(geth_poa_middleware, layer=0)
        w3 = TokenNodeConfModel.get_eth_node_server()
        return w3

    def assign_account_addresses(self, args):
        """
        分配用户地址,并把account_id 绑定到address
        :param args: account_id coin_id reset
        :return:
        """
        keys = ["account_id", "coin_id"]

        if not self.check_args(keys, args, True):
            return 10003

        account_id = str(args["account_id"])
        coin_id = str(args["coin_id"])
        reset = str(args.get("reset", ""))

        # 校验 coin_type是否合法 并且存请求记录
        with MysqlTools().session_scope() as session_address:
            coin = session_address.query(TokenCoinModel).filter(TokenCoinModel.coin_id == coin_id).first()
            if not coin:
                return 10003
            coin_type = coin.coin_name
            if coin_type not in self.symbol_to_model:
                return 10003
            chain_model = self.symbol_to_model[coin_type][_ZERO]

            # 无论分配地址成功与否,都记录请求流水
            new_assign_address_record = ForeignAssignAddressRecordModel(
                req_no=generate_order_no(),
                account_id=account_id,
                coin_id=coin_id
            )
            session_address.add(new_assign_address_record)
            session_address.commit()

            account_wallet = session_address.query(chain_model).filter(
                chain_model.account_id == account_id, chain_model.status == str(_ONE)).with_for_update().first()
            if not account_wallet or reset:
                # 绑定account_id到地址上,并把数据返回
                wallet = session_address.query(chain_model).filter(
                    chain_model.account_id == "").with_for_update().order_by(chain_model.sub_index,
                                                                             chain_model.sub_public_address).first()
                if not wallet:
                    return 90004
                wallet.account_id = account_id
                wallet.status = str(_ONE)
                session_address.add(wallet)
                # 求得分配地址
                assign_address = wallet.sub_public_address
                if reset and account_wallet:
                    account_wallet.status = str(_ZERO)
            else:
                assign_address = account_wallet.sub_public_address

            # 分配地址回写到流水表
            current_record = session_address.query(ForeignAssignAddressRecordModel).filter(
                ForeignAssignAddressRecordModel.req_no == new_assign_address_record.req_no).first()
            current_record.sub_public_address = assign_address

            session_address.commit()
            ret_account = {
                "account_id": account_id,
                "address": assign_address,
            }
            if coin_id == self.coin_id_eos:
                ret_account["address"] = self.eos_recharge_address
                ret_account["memo"] = assign_address
        return ret_account

    def generate_withdraw_order(self, args):
        """
        生成提现订单,需要账户和提现地址
        :param args: "req_no", "account_id", "coin_id", "withdraw_address", "withdraw_amount", "withdraw_gas_price", "withdraw_type"
        :return:
        """
        keys = ["req_no", "account_id", "coin_id", "withdraw_address", "withdraw_amount", "withdraw_fee",
                "withdraw_type"]

        if not self.check_args(keys, args, True) and \
                isinstance(args["withdraw_amount"], decimal.Decimal) and isinstance(args["withdraw_fee"],
                                                                                    decimal.Decimal):
            return 10003

        args["memo"] = args.get("memo", "").strip()

        if args["coin_id"] == self.coin_id_eth:
            right_address = CheckEthAddress.get_right_address(args["withdraw_address"])
            if right_address:
                args["withdraw_address"] = right_address
            else:
                self.return_error(90011)
        else:
            args["withdraw_address"] = args["withdraw_address"].strip()

        # 记录请求流水
        with MysqlTools().session_scope() as session_withdraw:
            record_withdraw = session_withdraw.query(ForeignWithdrawOrderRecordModel).filter(
                ForeignWithdrawOrderRecordModel.order_no == args["req_no"]).first()

            if args["coin_id"] not in self.symbol_to_model:
                return 10008
            if args["coin_id"] == self.coin_id_eth:
                args["withdraw_gas_price"] = get_decimal(
                    args["withdraw_fee"] / get_decimal(self.token_conf.gas_limit), 18)
            elif args["coin_id"] == self.coin_id_eos:
                args["withdraw_gas_price"] = args["withdraw_fee"]
            else:
                args["withdraw_gas_price"] = _ZERO
            if not record_withdraw:
                withdraw_record = ForeignWithdrawOrderRecordModel(
                    order_no=generate_order_no(),
                    req_no=args["req_no"],
                    account_id=args["account_id"],
                    coin_id=args["coin_id"],
                    withdraw_address=args["withdraw_address"],
                    withdraw_amount=args["withdraw_amount"],
                    withdraw_fee=args["withdraw_fee"],
                    withdraw_gas_price=args["withdraw_gas_price"],
                    withdraw_type=args["withdraw_type"],
                    memo=args["memo"]
                )
                session_withdraw.add(withdraw_record)
            else:
                withdraw_record = record_withdraw
                withdraw_record.account_id = args["account_id"],
                withdraw_record.coin_id = args["coin_id"],
                withdraw_record.withdraw_address = args["withdraw_address"],
                withdraw_record.withdraw_amount = args["withdraw_amount"],
                withdraw_record.withdraw_fee = args["withdraw_fee"],
                withdraw_record.withdraw_gas_price = args["withdraw_gas_price"],
                withdraw_record.withdraw_type = args["withdraw_type"]
                withdraw_record.memo = args["memo"]

            session_withdraw.commit()
            try:
                # 查询待处理为10的倍数发送邮件至管理员邮箱
                with MysqlTools().session_scope() as session:
                    withdraw_list = session.query(ForeignWithdrawOrderRecordModel).filter(
                        ForeignWithdrawOrderRecordModel.withdraw_type == _ZERO_S,
                        ForeignWithdrawOrderRecordModel.audit_status == _ZERO_S).order_by(
                        desc(ForeignWithdrawOrderRecordModel.created_at)).all()
                    withdraw_list_size = int(withdraw_list.count())
                    if withdraw_list_size != 0:
                        if withdraw_list_size % 10 == 0:
                            send_email_config = get_sms_email("send_email_config")
                            email_config = get_sms_email("withdraw_msg")
                            time = format_utc(withdraw_list[0].created_at)
                            conf = get_config()
                            env = conf["env"]
                            content = "当前待审核提现订单数量为：" + str(
                                withdraw_list_size) + "，距今最早的提现申请时间为：" + time + "。请您尽快处理。" + str(env)
                            send_mail(content, send_email_config['user'], send_email_config['pwd'],
                                      email_config['email'],
                                      email_config['email_subject'],
                                      send_email_config['smtp_server'], send_email_config['smtp_port'])
            except:
                pass

            withdraw_order_no = withdraw_record.order_no

        return {
            "order_no": withdraw_order_no,
            "withdraw_status": True,  # True 处理成功 False 失败
        }

    def eth_get_gas_price(self):
        w3 = self.block_chain_connect()
        return get_decimal(w3.fromWei(w3.eth.gasPrice, self.eth_unit), 18) * self.token_conf.gather_gas

    def eth_get_gas(self):
        return self.eth_get_gas_price() * get_decimal(self.token_conf.gas_limit)

    # eos 批量 发送交易:
    def eos_send_tx_multi(self, from_address, withdraw_list):
        if not withdraw_list:
            return
        with MysqlTools().session_scope() as session:
            multi_withdraw_record = ForeignMultiWithdrawRecordModel(
                record_id=generate_order_no(),
                coin_id=self.coin_id_eos,
                from_address=from_address,
                withdraw_status=self.withdraw_status_process_fail
            )
            session.add(multi_withdraw_record)
            session.commit()

            multi_withdraw_record_part_tran_status = _ZERO_S
            multi_withdraw_record_id = multi_withdraw_record.record_id
            for foreign_withdraw_order_record in withdraw_list:
                foreign_withdraw_order_record.relate_flow_no = multi_withdraw_record_id
                session.commit()
                multi_withdraw_record_now = session.query(ForeignMultiWithdrawRecordModel).filter(
                    ForeignMultiWithdrawRecordModel.record_id == multi_withdraw_record_id).first()
                # 交易 单笔
                send_result = self.eos_send_tx(foreign_withdraw_order_record)
                if send_result:
                    multi_withdraw_record_now.amount += foreign_withdraw_order_record.withdraw_amount
                    multi_withdraw_record_now.gas += foreign_withdraw_order_record.withdraw_fee
                    if multi_withdraw_record_part_tran_status == _ZERO_S:
                        multi_withdraw_record_now.withdraw_status = self.withdraw_status_part_transaction_success
                        multi_withdraw_record_part_tran_status = _ONE_S
                    else:
                        multi_withdraw_record_now.withdraw_status = self.withdraw_status_process_ing
                session.commit()

    # eth 批量 发送交易:
    def eth_send_tx_multi(self, from_address, withdraw_list):
        if not withdraw_list:
            return
        self.w3 = self.block_chain_connect()
        with MysqlTools().session_scope() as session:
            multi_withdraw_record = ForeignMultiWithdrawRecordModel(
                record_id=generate_order_no(),
                coin_id=self.coin_id_eth,
                from_address=from_address,
                withdraw_status=self.withdraw_status_process_fail
            )
            session.add(multi_withdraw_record)
            session.commit()

            multi_withdraw_record_part_tran_status = _ZERO_S
            multi_withdraw_record_id = multi_withdraw_record.record_id
            for foreign_withdraw_order_record in withdraw_list:
                foreign_withdraw_order_record.relate_flow_no = multi_withdraw_record_id
                session.commit()
                multi_withdraw_record_now = session.query(ForeignMultiWithdrawRecordModel).filter(
                    ForeignMultiWithdrawRecordModel.record_id == multi_withdraw_record_id).first()
                # 交易 单笔
                send_result = self.eth_send_tx(foreign_withdraw_order_record)
                if send_result:
                    multi_withdraw_record_now.amount += foreign_withdraw_order_record.withdraw_amount
                    multi_withdraw_record_now.gas += foreign_withdraw_order_record.withdraw_fee
                    if multi_withdraw_record_part_tran_status == _ZERO_S:
                        multi_withdraw_record_now.withdraw_status = self.withdraw_status_part_transaction_success
                        multi_withdraw_record_part_tran_status = _ONE_S
                    else:
                        multi_withdraw_record_now.withdraw_status = self.withdraw_status_process_ing
                session.commit()

    # eos 发送交易:
    def eos_send_tx(self, foreign_withdraw_order_record):
        foreign_withdraw_order_no = foreign_withdraw_order_record.order_no
        foreign_withdraw_type = foreign_withdraw_order_record.withdraw_type
        account_id = foreign_withdraw_order_record.account_id
        gas = foreign_withdraw_order_record.withdraw_fee
        data = {
            "from_address": foreign_withdraw_order_record.from_address,
            "to_address": foreign_withdraw_order_record.withdraw_address,
            "amount": foreign_withdraw_order_record.withdraw_amount,
            "memo": foreign_withdraw_order_record.memo,
            "gas": gas,
            "symbol": _ACCOUNT
        }

        # 判断交易先决条件
        err_msg = ""
        tx_hash = ""
        err_code = _ZERO
        ret = False
        foreign_multi_now = None
        gather_filters = {}

        # 判断 交易的条件 合法性
        with MysqlTools().session_scope() as legal_session:
            # 查询相应的表
            gather_filters["sub_public_address"] = data["from_address"]
            wallet_gather = legal_session.query(WalletEosGatherModel).filter_by(**gather_filters).first()
            if not wallet_gather:
                self.return_error(90013)
            if data["from_address"] == data["to_address"]:
                err_msg = "发送地址和提现地址相同"
                err_code = 90006
            if data["amount"] <= data["gas"]:
                err_msg = "提现金额(包括手续费)小于等于手续费"
                err_code = 90008
            if not wallet_gather:
                err_msg = "eos归集账户没有这个地址"
                err_code = 90003
            if not gas:
                err_msg = "EOS手续费不能为零"
                err_code = 90012
            else:
                if data["amount"] > wallet_gather.amount:
                    err_msg = "此交易地址余额不足:" + data["from_address"]
                    err_code = 90009
            if err_msg:
                foreign_withdraw_now = legal_session.query(ForeignWithdrawOrderRecordModel).filter(
                    ForeignWithdrawOrderRecordModel.order_no == foreign_withdraw_order_no).first()
                foreign_withdraw_now.process_record = err_msg
                if foreign_withdraw_type in self.account_withdraw_type_list:
                    foreign_multi_now = legal_session.query(ForeignMultiWithdrawRecordModel).filter(
                        ForeignMultiWithdrawRecordModel.record_id == foreign_withdraw_order_record.relate_flow_no).first()
                elif foreign_withdraw_type in self.gather_withdraw_type_list:
                    foreign_multi_now = legal_session.query(ForeignGatherRecordModel).filter(
                        ForeignGatherRecordModel.record_id == foreign_withdraw_order_record.relate_flow_no).first()
                if foreign_multi_now:
                    if not foreign_multi_now.process_record:
                        foreign_multi_now.process_record = ""
                    else:
                        foreign_multi_now.process_record += ", "
                    foreign_multi_now.process_record += "foreign_withdraw_order_no:" + foreign_withdraw_order_no + "err_msg:" + err_msg
                legal_session.commit()
                self.return_error(err_code)
        with MysqlTools().session_scope() as session:
            order_record = session.query(ForeignWithdrawOrderRecordModel).filter(
                ForeignWithdrawOrderRecordModel.order_no == foreign_withdraw_order_no).first()
            wallet_eos = session.query(WalletEosModel).filter(
                WalletEosModel.account_id == account_id).with_for_update().first()
            if not wallet_eos:
                self.return_error(90013)
            data["account_address"] = wallet_eos.sub_public_address
            if not err_msg:
                try:
                    tx_res = self.eos_send_transaction(data)
                    if tx_res:
                        if tx_res.get("status", ""):
                            tx_hash = tx_res.get("data", "")
                        else:
                            err_msg = tx_res.get("data", "")
                            if not err_msg:
                                err_msg = tx_res.get("msg", "WalletCenter返回异常")
                            raise_logger(err_msg, "wallet", "error")
                    else:
                        raise_logger("WalletCenter数据库无法连接或返回异常", "wallet", "error")
                except Exception as e:
                    err_msg = str(e)
                    raise_logger(err_msg, "wallet", "error")

                if tx_hash:
                    tx_listening_eos = TxListeningEosModel(
                        order_no=generate_order_no(),
                        record_no=foreign_withdraw_order_no,
                        tx_no=tx_hash,
                        withdraw_type=foreign_withdraw_type,
                        source_status=_ZERO_S
                    )
                    session.add(tx_listening_eos)

                    # 查询地址对应的钱包
                    wallet_eth_gather = session.query(WalletEosGatherModel).filter(
                        WalletEosGatherModel.sub_public_address == data["from_address"]).with_for_update().first()
                    if not wallet_eth_gather:
                        self.return_error(90013)
                    # 对应 wallet_eos 和 wallet_eos_gather 减少余额 和 增加冻结金额
                    wallet_eos.amount_frozen += data["amount"]
                    wallet_eos.amount -= data["amount"]
                    wallet_eth_gather.amount_frozen += data["amount"]
                    wallet_eth_gather.amount -= data["amount"]
                    order_record.withdraw_status = self.withdraw_status_process_ing
                    order_record.expect_at = get_utc_now()
                    order_record.transfer_at = get_utc_now()
                    ret = True

            # 如果没有tx_hash,记录提现处理失败
            if not tx_hash:
                order_record.withdraw_status = self.withdraw_status_process_fail
            order_record.process_record = err_msg
            session.commit()
        return ret

    # eth 发送交易:
    def eth_send_tx(self, foreign_withdraw_order_record):
        if not self.w3:
            self.w3 = self.block_chain_connect()
        foreign_withdraw_order_no = foreign_withdraw_order_record.order_no
        foreign_withdraw_type = foreign_withdraw_order_record.withdraw_type
        gas = foreign_withdraw_order_record.withdraw_fee
        gas_price = foreign_withdraw_order_record.withdraw_gas_price
        data = {
            "from_address": foreign_withdraw_order_record.from_address,
            "to_address": foreign_withdraw_order_record.withdraw_address,
            "amount": foreign_withdraw_order_record.withdraw_amount,
            "gas": gas if gas else self.eth_get_gas(),
            "gas_price": gas_price if gas_price else self.eth_get_gas_price(),
            "gas_limit": self.token_conf.gas_limit,
            "data": b'',
        }
        # 提现状态 0-用户提现, 1-用户中奖 3-归集转归集
        if foreign_withdraw_type in self.account_withdraw_type_list or foreign_withdraw_type == _THREE_S:
            data["symbol"] = _GATHER
            wallet_model = WalletEthGatherModel
        # 归集账户 归集转归集 2-子账户归集
        elif foreign_withdraw_type == _TWO_S:
            data["symbol"] = _ACCOUNT
            wallet_model = WalletEthModel

        else:
            wallet_model = None
            self.return_error(90010)

        # 补充 手续费 手续费单价 归集类型的提现流水
        if foreign_withdraw_type in self.gather_withdraw_type_list:
            with MysqlTools().session_scope() as gather_session:
                withdraw_gather_order = gather_session.query(ForeignWithdrawOrderRecordModel).filter(
                    ForeignWithdrawOrderRecordModel.order_no == foreign_withdraw_order_no).first()
                withdraw_gather_order.withdraw_fee = data["gas"]
                withdraw_gather_order.withdraw_gas_price = data["gas_price"]
                gather_session.commit()
        # 判断交易先决条件
        err_msg = ""
        tx_hash = ""
        err_code = _ZERO
        ret = False
        foreign_multi_now = None
        gather_filters = {}

        # 判断 交易的条件 合法性
        with MysqlTools().session_scope() as legal_session:
            # 查询相应的表
            gather_filters["sub_public_address"] = data["from_address"]
            wallet_gather = legal_session.query(wallet_model).filter_by(**gather_filters).first()
            if data["from_address"] == data["to_address"]:
                err_msg = "发送地址和提现地址相同"
                err_code = 90006
            if data["amount"] <= data["gas"]:
                err_msg = "提现金额(包括手续费)小于等于手续费"
                err_code = 90008
            if not wallet_gather:
                err_msg = "eth归集账户没有这个地址"
                err_code = 90003
            else:
                if data["amount"] > wallet_gather.amount:
                    err_msg = "此交易地址余额不足:" + data["from_address"]
                    err_code = 90009
            if err_msg:
                foreign_withdraw_now = legal_session.query(ForeignWithdrawOrderRecordModel).filter(
                    ForeignWithdrawOrderRecordModel.order_no == foreign_withdraw_order_no).first()
                foreign_withdraw_now.process_record = err_msg
                if foreign_withdraw_type in self.account_withdraw_type_list:
                    foreign_multi_now = legal_session.query(ForeignMultiWithdrawRecordModel).filter(
                        ForeignMultiWithdrawRecordModel.record_id == foreign_withdraw_order_record.relate_flow_no).first()
                elif foreign_withdraw_type in self.gather_withdraw_type_list:
                    foreign_multi_now = legal_session.query(ForeignGatherRecordModel).filter(
                        ForeignGatherRecordModel.record_id == foreign_withdraw_order_record.relate_flow_no).first()
                if foreign_multi_now:
                    if not foreign_multi_now.process_record:
                        foreign_multi_now.process_record = ""
                    else:
                        foreign_multi_now.process_record += ", "
                    foreign_multi_now.process_record += "foreign_withdraw_order_no:" + foreign_withdraw_order_no + "err_msg:" + err_msg
                legal_session.commit()
                self.return_error(err_code)
        with MysqlTools().session_scope() as session:
            order_record = session.query(ForeignWithdrawOrderRecordModel).filter(
                ForeignWithdrawOrderRecordModel.order_no == foreign_withdraw_order_no).first()
            if not err_msg:
                try:
                    tx_res = self.eth_send_transaction(data)
                    if tx_res:
                        if tx_res.get("status", ""):
                            tx_hash = tx_res.get("data", "")
                        else:
                            err_msg = tx_res.get("data", "")
                            if not err_msg:
                                err_msg = tx_res.get("msg", "WalletCenter返回异常")
                            raise_logger(err_msg, "wallet", "error")
                    else:
                        raise_logger("WalletCenter数据库无法连接或返回异常", "wallet", "error")
                    # wait_for_res = self.w3.eth.waitForTransactionReceipt("0x" + tx_hash, timeout=3600)
                except Exception as e:
                    # err_msg = super_json_dumps(e).replace('"', "").replace("'", "")
                    err_msg = str(e)
                    raise_logger(err_msg, "wallet", "error")

                if tx_hash:
                    tx_listening_eth = TxListeningEthModel(
                        order_no=generate_order_no(),
                        record_no=foreign_withdraw_order_no,
                        tx_no=tx_hash,
                        withdraw_type=foreign_withdraw_type,
                        source_status=_ZERO_S
                    )
                    session.add(tx_listening_eth)

                    # 查询地址对应的钱包
                    wallet_eth = session.query(wallet_model).filter(
                        wallet_model.sub_public_address == data["from_address"]).first()
                    # 对应 wallet_eth 和 wallet_eth 减少余额 和 增加冻结金额
                    wallet_eth.amount_frozen += data["amount"]
                    wallet_eth.amount -= data["amount"]
                    order_record.withdraw_status = self.withdraw_status_process_ing
                    order_record.expect_at = self.eth_expect_confirm_time()
                    order_record.transfer_at = get_utc_now()
                    ret = True

            # 如果没有tx_hash,记录提现处理失败
            if not tx_hash:
                order_record.withdraw_status = self.withdraw_status_process_fail
            order_record.process_record = err_msg
            session.commit()
        return ret

    def eos_send_transaction(self, data):
        quantity = decimal_to_str(data["amount"] - data["gas"], digits=4) + " " + self.eos_unit
        params = {
            "order_no": generate_order_no(),
            "parameter": {
                "coin_id": self.coin_id_eos,
                "address": data["account_address"],
                "symbol": data["symbol"]
            },
            "sign": {
                "from": data["from_address"],
                "to": data["to_address"],
                "quantity": quantity,
                "memo": data["memo"],
            }
        }
        tx_res = do_post(self.private_url, params)
        params["tx_res"] = super_json_dumps(tx_res)
        raise_logger(super_json_dumps(params), "wallet", "info")
        return tx_res

    def eth_send_transaction(self, data):
        transaction = self.eth_get_transaction_info(data)
        params = {
            "order_no": generate_order_no(),
            "parameter": {
                "coin_id": self.coin_id_eth,
                "address": data["from_address"],
                "symbol": data["symbol"]
            },
            "sign": transaction
        }
        tx_res = do_post(self.private_url, params)
        params["tx_res"] = super_json_dumps(tx_res)
        raise_logger(super_json_dumps(params), "wallet", "info")
        return tx_res
        # signed_txn = self.w3.eth.account.signTransaction(transaction, data["pk"])
        # tx_hash_hex_bytes = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        # return tx_hash_hex_bytes

    def eth_get_transaction_info(self, data):
        from_address = data["from_address"]
        to_address = data["to_address"]
        amount = self.w3.toWei(decimal_to_str(data["amount"] - data["gas"]), self.eth_unit)
        gas_price = int(self.w3.toWei(decimal_to_str(data["gas_price"]), self.eth_unit))
        gas_limit = data["gas_limit"]
        data = data["data"]

        tx_count = self.w3.eth.getTransactionCount(from_address)
        try:
            pending_transactions = len(self.w3.txpool.inspect.pending[from_address])
        except KeyError:
            pending_transactions = 0
        nonce = tx_count + pending_transactions
        transaction = {
            "from": from_address,
            "to": to_address,
            "value": amount,
            "data": data,
            "nonce": nonce,
            "gasPrice": gas_price,
            "gas": gas_limit,
        }
        return transaction

    def eth_expect_confirm_time(self):
        confirm_time = get_utc_now()
        if not self.eth_block_time:
            return confirm_time

        confirm_block_num = int(self.token_conf.confirm_last_block_num)
        last_confirm_time = confirm_block_num * self.eth_block_time  # sec 秒
        return get_datetime_now_offset("seconds", last_confirm_time)

    # btc 发送交易(归集)[1对1]:
    # 交易量小时允许只支付最小交易费,当交易量大到超出网络可处理时交易可能永远无法确认 0.00001 BTC/kb
    def btc_send_tx(self, foreign_withdraw_order_record):
        self.rpc = TokenNodeConfModel.get_btc_node_server()
        from_address = foreign_withdraw_order_record.from_address
        to_address = foreign_withdraw_order_record.withdraw_address
        amount = foreign_withdraw_order_record.withdraw_amount
        amount = get_decimal(amount, 18)
        with MysqlTools().session_scope() as session:
            # 计算所需手续费
            tx_list = session.query(TxListBtcModel).filter(TxListBtcModel.address == from_address,
                                                           TxListBtcModel.cost_flag == _ZERO).all()
            vin = []
            send_amount = 0
            if not tx_list:  # UTXO列表可用为空
                raise_logger("UTXO列表可用为空", "wallet", "error")
                return "UTXO列表可用为空"
            for tx in tx_list:
                send_amount = send_amount + get_decimal(tx.value, 18)
                send_tx = {"txid": tx.tx_no, "vout": tx.vout}
                vin.append(send_tx)
                session.query(TxListBtcModel).filter(TxListBtcModel.tx_id == tx.tx_id).update({
                    TxListBtcModel.cost_flag: _ONE
                })
                if send_amount >= amount:
                    break
            if to_address == from_address:  # 付款、收款是一个地址
                raise_logger("付款、收款是一个地址", "wallet", "error")
                return "付款、收款是一个地址"
            vout = None
            if send_amount == amount:  # 所用UTXO等于需转账金额
                vout = {to_address: amount}
            elif send_amount > amount:  # 所用UTXO大于需转账金额,设置找零地址
                vout = {to_address: amount, from_address: send_amount - amount}
            elif send_amount < amount:  # 所用UTXO小于需转账金额
                raise_logger("所用UTXO小于需转账金额", "wallet", "error")
                return "所用UTXO小于需转账金额"
            old_tx_encoded = self.rpc.createrawtransaction(vin, vout)

            withdraw_type = foreign_withdraw_order_record.withdraw_type
            # if withdraw_type == _ZERO_S or withdraw_type == _THREE_S:  # 提现/归集转归集,使用归集账户私钥
            #     private_map = {"order_no": generate_order_no(), "type": "btc",
            #                    "address": [from_address], "category": "gather"}
            # else:  # 归集,使用子账户私钥
            #     private_map = {"order_no": generate_order_no(), "type": "btc",
            #                    "address": [from_address]}
            # result_map = do_post(self.private_url, private_map)
            # public_key_aes = ""
            # for i in result_map:
            #     if i != "category":
            #         public_key_aes = i
            # if public_key_aes == "msg":
            #     self.return_error(30037)
            # token_salt = session.query(TokenSaltModel).filter(
            #     TokenSaltModel.public_key_aes == public_key_aes).first()
            # key = token_salt.key_aes
            # nonce = token_salt.nonce_aes
            # sub_private_key_aes = result_map[public_key_aes][0]["private_key_aes"]
            # sub_private_key = super_deAES(sub_private_key_aes, key, nonce)
            # priv = [sub_private_key]
            #
            # new_tx_encoded = self.rpc.signrawtransactionwithkey(old_tx_encoded, priv)
            # hex = new_tx_encoded.get("hex")
            symbol = _ACCOUNT
            if withdraw_type == _ZERO_S or withdraw_type == _THREE_S:  # 提现/归集转归集,使用归集账户私钥
                symbol = _GATHER
            params = {
                "order_no": generate_order_no(),
                "parameter": {
                    "coin_id": self.coin_id_btc,
                    "address": from_address,
                    "symbol": symbol,
                    "calc": True
                },
                "sign": old_tx_encoded
            }
            tx_res = do_post(self.private_url, params)
            if tx_res.get("status", ""):
                hex = tx_res.get("data", "")
            else:
                err_msg = tx_res.get("data", "")
                raise_logger(err_msg, "wallet", "error")
            tx_details = self.rpc.decoderawtransaction(hex)
            size_b = tx_details.get("size")
            size_k = size_b / 1024 + 1
            token_conf = session.query(TokenConfModel).filter(TokenConfModel.coin_id == _ZERO_S).first()
            withdraw_fee = token_conf.withdraw_fee  # 手续费单价
            gas = get_decimal(size_k, 18) * get_decimal(withdraw_fee, 18)  # bitcoind最低手续费单价为0.000011/kb
            # 构造"空白交易"(scriptSig留空),也称作待签名交易
            tx_no_list_str = ",".join(str(tx["txid"]) for tx in vin)
            amount_change = 0
            if send_amount == amount:  # 所用UTXO等于需转账金额
                vout = {to_address: amount - gas}
            elif send_amount > amount:  # 所用UTXO大于需转账金额,设置找零地址
                amount = amount - gas
                amount_change = send_amount - amount - gas
                vout = {to_address: amount, from_address: amount_change}
            elif gas > amount:  # 手续费大于需转账金额
                raise_logger("手续费大于需转账金额", "wallet", "error")
                return "手续费大于需转账金额"
            elif gas == 0:  # 手续费为0
                raise_logger("手续费为0", "wallet", "error")
                return "手续费为0"
            old_tx_encoded = self.rpc.createrawtransaction(vin, vout)
            params = {
                "order_no": generate_order_no(),
                "parameter": {
                    "coin_id": self.coin_id_btc,
                    "address": from_address,
                    "symbol": symbol,
                    "calc": False
                },
                "sign": old_tx_encoded
            }
            # new_tx_encoded = self.rpc.signrawtransactionwithkey(old_tx_encoded, priv)
            try:
                tx_res = do_post(self.private_url, params)
                tx_no = None
                if tx_res.get("status", ""):
                    tx_no = tx_res.get("data", "")
                else:
                    err_msg = tx_res.get("data", "")
                    raise_logger(err_msg, "wallet", "error")
                    self.return_error(10020)
                # tx_no = self.rpc.sendrawtransaction(new_tx_encoded.get("hex"), False)
                btc_tx_listening = TxListeningBtcModel(
                    order_no=generate_order_no(),
                    record_no=foreign_withdraw_order_record.order_no,
                    tx_no=tx_no,
                    tx_nos=tx_no_list_str,
                    withdraw_type=foreign_withdraw_order_record.withdraw_type,
                    source_status=foreign_withdraw_order_record.source_status,
                    listen_flag=_ONE,
                    multi_flag=_ZERO
                )
                session.add(btc_tx_listening)
                # 修改withdraw表
                session.query(ForeignWithdrawOrderRecordModel).filter(
                    ForeignWithdrawOrderRecordModel.order_no == foreign_withdraw_order_record.order_no).update({
                    ForeignWithdrawOrderRecordModel.amount_change: amount_change,
                    ForeignWithdrawOrderRecordModel.withdraw_gas_price: withdraw_fee,
                    ForeignWithdrawOrderRecordModel.withdraw_fee: gas,
                    ForeignWithdrawOrderRecordModel.withdraw_status: _ONE_S,
                    ForeignWithdrawOrderRecordModel.transfer_at: get_now_time()})
                if foreign_withdraw_order_record.withdraw_type == _TWO_S:  # 归集
                    # 修改wallet_btc表(from_address)
                    session.query(WalletBtcModel).filter(WalletBtcModel.sub_public_address == from_address).update({
                        WalletBtcModel.amount: WalletBtcModel.amount - amount,
                        WalletBtcModel.amount_change: WalletBtcModel.amount_change + amount_change,
                        WalletBtcModel.amount_frozen: WalletBtcModel.amount_frozen + amount - gas
                    })
                    # 修改gather表叠加手续费
                    session.query(ForeignGatherRecordModel).filter(
                        ForeignGatherRecordModel.record_id == foreign_withdraw_order_record.relate_flow_no).with_for_update().first()  # 锁行
                    session.query(ForeignGatherRecordModel).filter(
                        ForeignGatherRecordModel.record_id == foreign_withdraw_order_record.relate_flow_no).update(
                        {ForeignGatherRecordModel.actual_fee: ForeignGatherRecordModel.actual_fee + gas})
                elif foreign_withdraw_order_record.withdraw_type == _THREE_S:  # 归集转归集
                    # 修改wallet_btc_gather表(from_address)
                    session.query(WalletBtcGatherModel).filter(
                        WalletBtcGatherModel.sub_public_address == from_address).with_for_update().first()  # 锁行
                    session.query(WalletBtcGatherModel).filter(
                        WalletBtcGatherModel.sub_public_address == from_address).update({
                        WalletBtcGatherModel.amount: WalletBtcGatherModel.amount - send_amount,
                        WalletBtcGatherModel.amount_change: WalletBtcGatherModel.amount_change + amount_change,
                        WalletBtcGatherModel.amount_frozen: WalletBtcGatherModel.amount_frozen + amount
                    })
                session.commit()
                return True
            except JSONRPCException as err:
                self.return_error(10020)

    def gather_list(self, coin_id, conditions):
        """
        通过条件计算可归集地址list及总金额
        :param coin_id: 币种
        :param conditions: 归集条件(大于等于xx个单位)
        :return:
        """
        with MysqlTools().session_scope() as session:
            wallet_list = []
            if coin_id == _ZERO_S:
                wallet_list = session.query(WalletBtcModel).filter(WalletBtcModel.amount >= conditions).all()
            elif coin_id == _SIXTY_S:
                wallet_list = session.query(WalletEthModel).filter(WalletEthModel.amount >= conditions).all()
            address_list = []
            total_amount = 0
            for wallet in wallet_list:
                address = {}
                address["address"] = wallet.sub_public_address
                amount = wallet.amount
                total_amount = total_amount + amount
                address["amount"] = decimal_to_str(amount)
                address_list.append(address)
            result_map = {"address_list": address_list, "total_amount": decimal_to_str(total_amount)}
            return result_map

    def get_gas(self, coin_id, user_id, token_id):
        """
        app获取提现手续费单价接口
        :param coin_id: 币种
        :return:
        """
        result = {}
        with MysqlTools().session_scope() as session:
            q = session.query(TokenConfModel).filter(TokenConfModel.coin_id == coin_id).first()
            if coin_id == self.coin_id_btc:
                size = get_decimal(226 / 1024)
                result["gas_lag"] = decimal_to_client(q.gas_lag * size, decimal_type="up")  # 低
                result["gas_routine"] = decimal_to_client(q.gas_routine * size, decimal_type="up")  # 中
                result["gas_prior"] = decimal_to_client(q.gas_prior * size, decimal_type="up")  # 高
            elif coin_id == self.coin_id_eth:
                gas = self.eth_get_gas()
                result["gas_lag"] = decimal_to_client(q.gas_lag * gas, decimal_type="up")  # 低
                result["gas_routine"] = decimal_to_client(q.gas_routine * gas, decimal_type="up")  # 中
                result["gas_prior"] = decimal_to_client(q.gas_prior * gas,
                                                        decimal_type="up")  # 高elif coin_id == self.coin_id_eth:
            elif coin_id == self.coin_id_eos:
                gas = q.withdraw_fee
                result["gas_lag"] = decimal_to_client(q.gas_lag * gas, decimal_type="up")  # 低
                result["gas_routine"] = decimal_to_client(q.gas_routine * gas, decimal_type="up")  # 中
                result["gas_prior"] = decimal_to_client(q.gas_prior * gas, decimal_type="up")  # 高
            user_account_token = session.query(UserAccountTokenModel).filter(UserAccountTokenModel.user_id == user_id,
                                                                             UserAccountTokenModel.token_id == coin_id).first()
            if user_account_token:
                result["balance"] = decimal_to_client(user_account_token.balance)  # 用户余额
            else:
                result["balance"] = decimal_to_client("0")
            return result

    # btc 发送交易(用户提现)[批量]:
    def btc_send_tx_multi(self, from_address, withdraw_list):
        self.rpc = TokenNodeConfModel.get_btc_node_server()
        from_address = from_address  # 出款地址
        gas = 0
        amount = 0
        for w in withdraw_list:
            gas = gas + get_decimal(w.withdraw_fee, 18)
            amount = amount + get_decimal(w.withdraw_amount, 18)

        with MysqlTools().session_scope() as session:
            tx_list = session.query(TxListBtcModel).filter(TxListBtcModel.address == from_address,
                                                           TxListBtcModel.cost_flag == _ZERO).all()
            vin = []
            send_amount = 0
            if not tx_list:  # UTXO列表可用为空
                raise_logger("UTXO列表可用为空", "wallet", "error")
                self.return_error(10001)
            if gas > amount:  # 手续费大于需转账金额
                raise_logger("手续费大于需转账金额", "wallet", "error")
                self.return_error(10001)
            if gas == 0:  # 手续费为0
                raise_logger("手续费为0", "wallet", "error")
                self.return_error(10001)
            for tx in tx_list:
                send_amount = send_amount + get_decimal(tx.value, 18)
                send_tx = {"txid": tx.tx_no, "vout": tx.vout}
                vin.append(send_tx)
                session.query(TxListBtcModel).filter(TxListBtcModel.tx_id == tx.tx_id).update({
                    TxListBtcModel.cost_flag: _ONE
                })
                if send_amount >= amount:
                    break
            if send_amount >= amount:  # 所用UTXO等于需转账金额
                vout = {}
                for w in withdraw_list:
                    vout_amount = vout.get(w.withdraw_address)
                    if vout_amount is None:
                        vout[w.withdraw_address] = w.withdraw_amount - w.withdraw_fee
                    else:
                        vout[w.withdraw_address] = vout_amount + (w.withdraw_amount - w.withdraw_fee)
                amount_change = 0
                if send_amount > amount:  # 所用UTXO大于需转账金额,设置找零地址
                    vout_amount = vout.get(from_address)
                    amount_change = send_amount - amount
                    if vout_amount is None:
                        vout[from_address] = amount_change
                    else:
                        vout[from_address] = vout_amount + amount_change
            elif send_amount < amount:  # 所用UTXO小于需转账金额
                raise_logger("所用UTXO小于需转账金额", "wallet", "error")
                self.return_error(10001)
            old_tx_encoded = self.rpc.createrawtransaction(vin, vout)

            # private_map = {"order_no": generate_order_no(), "type": "btc",
            #                "address": [from_address], "category": "gather"}
            # result_map = do_post(self.private_url, private_map)
            # public_key_aes = ""
            # for i in result_map:
            #     if i != "category":
            #         public_key_aes = i
            # if public_key_aes == "msg":
            #     self.return_error(30037)
            #
            # token_salt = session.query(TokenSaltModel).filter(
            #     TokenSaltModel.public_key_aes == public_key_aes).first()
            # key = token_salt.key_aes
            # nonce = token_salt.nonce_aes
            # sub_private_key_aes = result_map[public_key_aes][0]["private_key_aes"]
            # sub_private_key = super_deAES(sub_private_key_aes, key, nonce)
            # priv = [sub_private_key]
            #
            # new_tx_encoded = self.rpc.signrawtransactionwithkey(old_tx_encoded, priv)
            # hex = new_tx_encoded.get("hex")
            tx_no_list_str = ",".join(str(tx["txid"]) for tx in vin)

            try:
                params = {
                    "order_no": generate_order_no(),
                    "parameter": {
                        "coin_id": self.coin_id_btc,
                        "address": from_address,
                        "symbol": _GATHER
                    },
                    "sign": old_tx_encoded
                }
                tx_res = do_post(self.private_url, params)
                tx_no = None
                if tx_res.get("status", ""):
                    tx_no = tx_res.get("data", "")
                else:
                    err_msg = tx_res.get("data", "")
                    raise_logger(err_msg, "wallet", "error")
                    self.return_error(10025)
                # tx_no = self.rpc.sendrawtransaction(hex, True)
                # insert 提现记录表
                record_id = generate_order_no()
                foreign_multi_withdraw_record = ForeignMultiWithdrawRecordModel(
                    record_id=record_id,
                    coin_id=_ZERO,
                    from_address=from_address,
                    amount=amount,
                    amount_change=amount_change,
                    gas=gas,
                    withdraw_status=_ONE_S
                )
                session.add(foreign_multi_withdraw_record)
                # insert tx监听表
                btc_tx_listening = TxListeningBtcModel(
                    order_no=generate_order_no(),
                    record_no=foreign_multi_withdraw_record.record_id,
                    tx_no=tx_no,
                    tx_nos=tx_no_list_str,
                    withdraw_type=_ZERO_S,
                    source_status=_ZERO_S,
                    listen_flag=_ONE,
                    multi_flag=_ONE
                )
                session.add(btc_tx_listening)
                # 修改withdraw表状态
                for w in withdraw_list:
                    session.query(ForeignWithdrawOrderRecordModel).filter(
                        ForeignWithdrawOrderRecordModel.order_no == w.order_no).update({
                        ForeignWithdrawOrderRecordModel.relate_flow_no: foreign_multi_withdraw_record.record_id,
                        ForeignWithdrawOrderRecordModel.withdraw_status: _ONE_S,
                        ForeignWithdrawOrderRecordModel.transfer_at: get_now_time()})
                # 修改wallet_btc_gather表
                session.query(WalletBtcGatherModel).filter(
                    WalletBtcGatherModel.sub_public_address == from_address).with_for_update().first()  # 锁行
                session.query(WalletBtcGatherModel).filter(
                    WalletBtcGatherModel.sub_public_address == from_address).update({
                    WalletBtcGatherModel.amount: WalletBtcGatherModel.amount - send_amount,
                    WalletBtcGatherModel.amount_change: WalletBtcGatherModel.amount_change + amount_change,
                    WalletBtcGatherModel.amount_frozen: WalletBtcGatherModel.amount_frozen + (amount - gas)
                })
                session.commit()
                return True
            except JSONRPCException as err:
                raise_logger(err, "wallet", "error")
                self.return_error(10001)

    def append_gas(self, order_no, verification_code):
        """
        eth追加手续费
        :param order_no: order_no
        :param verification_code: 验证码
        :return:
        """
        conf = get_config()
        env = conf["env"]
        if env == "pd":
            vcode_service = VcodeService()
            result = vcode_service.check_sms_email_vcode('common', verification_code)
        return

    def send_code(self):
        """
        发送邮箱验证码
        :return:
        """
        vcode_service = VcodeService()
        result = vcode_service.send_vcode_by_email('common')
        return result

    def check_address(self, coin_id, user_id, address):
        """
        判断提现地址是否为平台地址
        :param coin_id: 币种
        :param user_id
        :param address: 地址
        :return:
        """
        with MysqlTools().session_scope() as session:
            wallet_model = None
            if coin_id == _ZERO_S:
                wallet_model = WalletBtcModel
            elif coin_id == _SIXTY_S:
                wallet_model = WalletEthModel
            elif coin_id == _COIN_ID_EOS:
                wallet_model = WalletEosModel
            user_account = session.query(UserAccountModel).filter(UserAccountModel.user_id == user_id).first()
            account_id = user_account.account_id
            wallet = session.query(wallet_model).filter(wallet_model.account_id == account_id,
                                                        wallet_model.sub_public_address == address).first()
            result = {}
            if not wallet:
                result["result"] = "1"  # 是平台账号
            else:
                result["result"] = "0"  # 非平台账号
            return result


class CheckEthAddress(object):

    @staticmethod
    def big_endian_to_int(value: bytes) -> int:
        return int.from_bytes(value, "big")

    @staticmethod
    def sha3_256_digest(x):
        return keccak.new(digest_bits=256, data=x).digest()

    @staticmethod
    def sha3_bytes(seed):
        return CheckEthAddress.sha3_256_digest(CheckEthAddress.to_string(seed))

    @staticmethod
    def to_string(value):
        if isinstance(value, bytes):
            return value
        if isinstance(value, str):
            return bytes(value, 'utf-8')
        if isinstance(value, int):
            return bytes(str(value), 'utf-8')

    @staticmethod
    def checksum_encode(addr_str):
        if addr_str[:2] != "0x" or not isinstance(addr_str, str):
            raise Exception("checksum_encode address is not lawful address: " + str(addr_str))
        addr = bytes.fromhex(addr_str[2:])
        o = ''
        v = CheckEthAddress.big_endian_to_int(CheckEthAddress.sha3_bytes(addr.hex()))
        for i, c in enumerate(addr.hex()):
            if c in '0123456789':
                o += c
            else:
                o += c.upper() if (v & (2 ** (255 - 4 * i))) else c.lower()
        return '0x' + o

    @staticmethod
    def get_right_address(address):
        try:
            address = address.strip()
            if address[:2] == "0x" and len(address) == 42:
                right_address = CheckEthAddress.checksum_encode(address)
                if address.lower() == right_address.lower():
                    return right_address
            return ""
        except:
            return ""

    def game_statistical(self):
        """
        游戏记录统计
        :return:
        # {
        #     "code": "00000",
        #     "desc": "success",
        #     "msg": "成功",
        #     "data": [
        #         {
        #             "game_serial": "0011812170002",  # 期号
        #             "need": "3591",  # 总需数
        #             "release_time": "2018-12-17 08:30:02",  # 发布时间
        #             "full_load_time": "2018-12-19 03:18:02",  # 满额时间
        #             "lottery_time": "2018-12-19 03:45:02",  # 开奖时间
        #             "experience": "0",  # 体验金占比
        #             "robot_bet_number": "3536",  # 机器人投注注数
        #             "experience_bet_number": "0",  # 体验金投注注数
        #             "btc_bet_number": "0",  # btc投注注数
        #             "btc_pay_number": "0",  # btc投注金额-BTC
        #             "btc_pay_cny": "0.00000000",  # btc投注金额-CNY
        #             "eth_bet_number": "42",  # eth投注注数
        #             "eth_pay_number": "0.464700000000000000",  # eth投注金额-ETH
        #             "eth_pay_cny": "491.13678300",  # eth投注金额-CNY
        #             "reward_quantity_cny": "27543.63000000"  # 开奖CNY
        #         }
        #     ]
        # }
        """
        with MysqlTools().session_scope() as session:
            BTC_rate = decimal.Decimal(27543.63)
            ETH_rate = decimal.Decimal(1056.89)

            game_digital_instance_list = session.query(GameDigitalInstanceModel).filter(
                GameDigitalInstanceModel.status == 2).all()
            result_list = []
            for game in game_digital_instance_list:
                game_serial = game.game_serial  # 期号
                participate_in_list = session.query(ParticipateInModel).filter(
                    ParticipateInModel.game_serial == game_serial).all()
                result_dict = {}
                robot_bet_number = 0  # 机器人投注注数
                experience_bet_number = 0  # 体验金投注注数
                btc_bet_number = 0  # btc投注注数
                btc_pay_number = 0  # btc投注金额

                eth_bet_number = 0  # eth投注注数
                eth_pay_number = 0  # eth投注金额
                for participate in participate_in_list:
                    if participate.user_type == 1:  # 机器人
                        robot_bet_number = robot_bet_number + participate.bet_number
                    else:
                        pay_token = participate.pay_token
                        if pay_token == 236:  # 体验金
                            experience_bet_number = experience_bet_number + participate.bet_number
                        elif pay_token == 0:  # BTC
                            btc_bet_number = btc_bet_number + participate.bet_number
                            btc_pay_number = btc_pay_number + participate.pay_number
                        elif pay_token == 60:  # ETH
                            eth_bet_number = eth_bet_number + participate.bet_number
                            eth_pay_number = eth_pay_number + participate.pay_number
                result_dict["game_serial"] = str(game_serial)  # 期号
                result_dict["need"] = str(game.need)  # 总需数
                result_dict["release_time"] = str(game.release_time)  # 发布时间
                result_dict["full_load_time"] = str(game.full_load_time)  # 满额时间
                result_dict["lottery_time"] = str(game.lottery_time)  # 开奖时间
                result_dict["experience"] = str(game.experience)  # 体验金占比
                result_dict["robot_bet_number"] = str(robot_bet_number)  # 机器人投注注数
                result_dict["experience_bet_number"] = str(experience_bet_number)  # 体验金投注注数
                result_dict["btc_bet_number"] = str(btc_bet_number)  # btc投注注数
                result_dict["btc_pay_number"] = str(btc_pay_number)  # btc投注金额
                result_dict["btc_pay_cny"] = decimal_to_client(btc_pay_number * BTC_rate)  # btc投注金额换算成CNY

                result_dict["eth_bet_number"] = str(eth_bet_number)  # eth投注注数
                result_dict["eth_pay_number"] = str(eth_pay_number)  # eth投注金额
                result_dict["eth_pay_cny"] = decimal_to_client(eth_pay_number * ETH_rate)  # eth投注金额换算成CNY

                result_dict["reward_quantity_cny"] = decimal_to_client(BTC_rate)  # 开奖CNY
                result_list.append(result_dict)
            return result_list

    def user_statistical(self):
        """
        用户数据分析
        :return:
        """
        with MysqlTools().session_scope() as session:
            resultMap = {}
            resultList = []
            sleep_user_account_list = session.query(UserAccountModel).filter(UserAccountModel.first_lottery == 0).all()
            sleep_user_count = len(sleep_user_account_list)  # 未参与游戏用户数
            user_account_list = session.query(UserAccountModel).filter(UserAccountModel.first_lottery == 1).all()
            user_count = len(sleep_user_account_list)  # 参与过游戏用户数
            experience_winning_count = 0  # 仅用体验金就中奖的用户的累积中奖参与次数
            for user in user_account_list:
                userMap = {}
                userMap["user_name"] = user.user_name
                userMap["nick_name"] = user.nick_name
                participate_in_list = session.query(ParticipateInModel).filter(
                    ParticipateInModel.user_id == user.user_id, ParticipateInModel.pay_token != 236).all()
                experience_count = len(participate_in_list)  # 只用体验金参与过的用户数
                if experience_count == 0:
                    for participate_in in participate_in_list:
                        game_serial = participate_in.game_serial
                        award_numbers = participate_in.award_numbers
                        # award_numbers = award_numbers[1, -1]
                        game_number_set = session.query(GameNumbersSetModel).filter(
                            GameNumbersSetModel.game_serial == game_serial,
                            GameNumbersSetModel.number.in_(award_numbers)).all()
                        game_number_set_count = len(game_number_set)
                        experience_winning_count = experience_winning_count + game_number_set_count
                else:  # 充值过并用充值币参与过的用户（含未使用过体验金的用户）
                    account_change_record_list = session.query(AccountChangeRecordModel).filter(
                        AccountChangeRecordModel.account_id == user.account_id).filter(
                        or_(AccountChangeRecordModel.change_type == "3",
                            AccountChangeRecordModel.change_type == "5",
                            AccountChangeRecordModel.change_type == "20")).all()
                    user_participate_btc = get_decimal(0, 18)  # 参与金额btc
                    user_participate_eth = get_decimal(0, 18)  # 参与金额eth
                    user_winning = get_decimal(0, 18)  # 中奖金额
                    participate_time = ""  # 最近一次参与时间
                    participate_count = 0  # 参与次数(含体验金)
                    for account_change_record in account_change_record_list:
                        change_type = str(account_change_record.change_type)
                        if change_type == "3" or change_type == "20":  # 参与
                            if account_change_record.token_id == "0":
                                user_participate_btc = user_participate_btc + get_decimal(
                                    account_change_record.change_amount, 18)
                            elif account_change_record.token_id == "60":
                                user_participate_eth = user_participate_eth + get_decimal(
                                    account_change_record.change_amount, 18)
                            participate_time = format_utc(str(account_change_record.created_at))
                            participate_count = participate_count + 1
                        elif change_type == "5":  # 中奖
                            user_winning = user_winning + decimal_two(account_change_record.change_amount)
                    userMap["user_participate_btc"] = decimal_to_client(user_participate_btc)  # 参与金额btc
                    userMap["user_participate_eth"] = decimal_to_client(user_participate_eth)  # 参与金额eth
                    userMap["user_winning"] = decimal_to_client(user_winning)  # 累计中奖金额btc
                    userMap["participate_time"] = participate_time  # 最近一次参与时间
                    userMap["participate_count"] = participate_count  # 参与次数(含体验金)
                    resultList.append(userMap)
            resultMap["sleep_user_count"] = sleep_user_count  # 未参与游戏用户数
            resultMap["user_count"] = user_count  # 参与过游戏用户数
            resultMap["experience_count"] = experience_count  # 只用体验金参与过的用户数
            resultMap["experience_winning_count"] = experience_winning_count  # 仅用体验金就中奖的用户的累积中奖参与次数
            resultMap["resultList"] = resultList
            return resultMap


if __name__ == '__main__':
    pass
