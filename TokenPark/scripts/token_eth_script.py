import sys
import binascii
from pathlib import Path

pro_name = "TokenPark"
current_path = str(Path(__file__).resolve())
import_index = current_path.rfind(pro_name)
import_path = current_path[:import_index + len(pro_name)]
path_flag = True if not import_path in sys.path else False
if path_flag:
    sys.path.append(import_path)

from tools.mysql_tool import MysqlTools
from models.token_coin_model import TokenCoinModel
from models.wallet_eth_model import WalletEthModel
from models.sync_block_model import SyncBlockModel
from models.token_conf_model import TokenConfModel
from models.wallet_eth_gather_model import WalletEthGatherModel
from models.tx_listening_eth_model import TxListeningEthModel
from models.tx_list_eth_model import TxListEthModel
from models.foreign_withdraw_order_record_model import ForeignWithdrawOrderRecordModel
from models.foreign_multi_withdraw_record_model import ForeignMultiWithdrawRecordModel
from models.foreign_gather_record_model import ForeignGatherRecordModel
from models.token_node_conf_model import TokenNodeConfModel
from utils.util import get_decimal, generate_order_no
from services.wallet_callback_service import WalletCallbackService
from utils.time_util import get_day_datetime, days_diff, get_datetime_from_str, get_utc_now
from common_settings import *
from utils.log import Slog


class TokenEthScript(object):
    # node_url = "http://" + get_config()["node_url"]["eth"][get_env()]["lan_url"] + ":8545"
    # node_url = eth_rpc_client()
    # "node_url": "https://rinkeby.infura.io/v3/e073287f5feb4e7892b38384fdee54dc",  # infura
    # "node_url": "http://52.194.21.55:8545"  # 正式
    # "node_url": "http://13.115.154.149:8545",  # 测试
    # "node_url": "http://3.16.26.56:8545"  # 测试俄亥俄
    coin_id = _SIXTY_S  # ETH
    sync_unfinished = _ZERO  # 状态标识:1-已完成,0-未完成
    sync_finished = _ONE
    unit = 'ether'  # 数据库以太坊计量单位
    gwei = 1e9
    withdraw_process_ing = _ONE_S  # 2-提现成功
    withdraw_success = _TWO_S  # 2-提现成功
    withdraw_fail = _THREE_S  # 3-提现失败
    withdraw_part_success = _FIVE_S  # 5-部分提现成功
    callback_account_withdraw_fail = _SIX_S
    account_withdraw_type_list = [_ZERO_S, _ONE_S]
    gather_withdraw_type_list = [_TWO_S, _THREE_S]
    wallet_model_list = [WalletEthModel, WalletEthGatherModel]
    block_num_temp = None
    process_count = None
    process_index = None
    slog = Slog("token_eth_script")

    def __init__(self, block_num_temp=None, multi_process=True):
        self.w3 = self.block_chain_connect()
        self.block_num_temp = block_num_temp
        if multi_process:
            self.multi_process_set()

    def multi_process_set(self):
        argv = sys.argv
        if len(argv) > 2:
            self.process_count = int(argv[1])
            self.process_index = int(argv[2]) - 1
        else:
            raise Exception("Python run script parameter error")

    @staticmethod
    def convert_info_to_json(info):
        try:
            info_dict = dict(info)
        except:
            return {}
        for key, value in info_dict.items():
            if key == "logs":
                info_dict[key] = []
            elif not isinstance(value, (str, int, float, list)):
                if value is None:
                    info_dict[key] = ""
                else:
                    info_dict[key] = binascii.hexlify(value).decode('utf-8')
            elif isinstance(value, list) and len(value) != 0:
                for i, v in enumerate(value):
                    if not isinstance(v, (str, int, float)):
                        value[i] = binascii.hexlify(v).decode('utf-8')
                info_dict[key] = value

        return info_dict

    def get_coin_type(self):
        with MysqlTools().session_scope() as session:
            coin = session.query(TokenCoinModel).filter(TokenCoinModel.coin_id == self.coin_id).first()
            return coin.coin_name

    def block_chain_connect(self):
        # w3 = Web3(Web3.HTTPProvider(self.node_url))
        # w3.middleware_stack.inject(geth_poa_middleware, layer=0)
        w3 = TokenNodeConfModel.get_eth_node_script()
        return w3

    def work(self):
        # 获取当前网络节点上的最新区块编号
        last_net_block = self.get_last_block_from_net()
        if self.block_num_temp:
            last_net_block_num = self.block_num_temp + 20
        else:
            last_net_block_num = last_net_block.number

        # 获取脚本相关配置文件
        token_conf = self.get_token_conf()
        # 获取同步区块编号,没有则从当前最新区块的前N块开始同步 同时锁定锁事物
        if self.block_num_temp:
            last_local_block = {
                "block_no": self.block_num_temp - 1,
                "status": True  # 状态标识:1-已完成,0-未完成
            }
        else:
            last_local_block = self.get_last_block_from_local()

        # 查找需要遍历的收款 子钱包地址 和 交易Tx
        address_list = self.get_wallet_eth_address()
        gather_address_list = self.get_wallet_eth_gather_address()
        eth_tx_model, eth_tx_list = self.get_wallet_eth_tx()
        # 开始同步区块
        sync_block_result = self.sync_block(token_conf, last_net_block_num, last_local_block, address_list, gather_address_list, eth_tx_list)
        # 检查如果有交易Tx超过失败天数,改成不需要监听
        check_tx_result = self.check_and_update_tx_flag(eth_tx_model, int(token_conf["confirm_last_err_days"]))
        # 如果遍历批量提现流水一期的所有提现都已提现成功,那么批量提现流水的状态改成成功
        check_multi_withdraw = self.check_and_update_multi_withdraw()
        # 如果遍历批量归集一期的所有提现都已提现成功,那么批量归集流水的状态改成成功
        check_multi_gather = self.check_and_update_gather()
            # # 提交事物
            # block_session.commit()
        return sync_block_result and check_tx_result and check_multi_withdraw and check_multi_gather

    def get_token_conf(self):
        with MysqlTools().session_scope() as session:
            token_conf = session.query(TokenConfModel).filter(TokenConfModel.coin_id == self.coin_id).first()
            if not token_conf:
                raise Exception("The relevant configuration file was not read => TokenConfModel")
            return {
                "confirm_last_block_num": token_conf.confirm_last_block_num,
                "confirm_last_err_days": token_conf.confirm_last_err_days,
            }

    def get_last_block_from_local(self):
        with MysqlTools().session_scope() as session:
            f_filters = {"coin_id": self.coin_id}
            if self.process_index is not None:
                f_filters["process"] = str(self.process_index)
            block_sync = session.query(SyncBlockModel).filter_by(**f_filters).first()
            if not block_sync:
                return
            return {
                "block_no": block_sync.block_no,
                "status": True if self.sync_finished == block_sync.status else False  # 状态标识:1-已完成,0-未完成
            }

    def update_wallet_eth_address(self, session, block_no, block_hash):
        f_filters = {"coin_id": self.coin_id}
        if self.process_index is not None:
            f_filters["process"] = str(self.process_index)
        sync_block = session.query(SyncBlockModel).filter_by(**f_filters).first()
        if not sync_block:
            if self.process_index is not None:
                sync_block_model = SyncBlockModel(
                    block_no=int(block_no),
                    block_hash=block_hash,
                    status=_ONE_S,
                    coin_id=self.coin_id,
                    process=str(self.process_index)
                )
            else:
                sync_block_model = SyncBlockModel(
                    block_no=int(block_no),
                    block_hash=block_hash,
                    status=_ONE_S,
                    coin_id=self.coin_id
                )
            session.add(sync_block_model)
        else:
            sync_block.block_no = block_no
            sync_block.block_hash = block_hash
            sync_block.status = self.sync_finished

    def get_last_block_from_net(self):
        try:
            return self.w3.eth.getBlock(self.w3.eth.blockNumber)
        except:
            raise Exception("The network is bad!")

    @staticmethod
    def get_wallet_eth_address():
        """
        获取需要侦听的 eth address
        :return:
        """
        with MysqlTools().session_scope() as session:
            address_model = session.query(WalletEthModel.sub_public_address).filter(WalletEthModel.account_id != "").all()

            # 处理 用户地址列表
            address_list = []
            if address_model:
                for address in address_model:
                    address_list.append(address[_ZERO])
            return address_list

    @staticmethod
    def get_wallet_eth_gather_address():
        """
        获取需要侦听归集账户的 eth gather address
        :param session:
        :return:
        """
        with MysqlTools().session_scope() as session:
            gather_address_model = session.query(WalletEthGatherModel.sub_public_address).all()

            # 处理 归集地址列表
            gather_address_list = []
            if gather_address_model:
                for address in gather_address_model:
                    gather_address_list.append(address[_ZERO])
            return gather_address_list

    @staticmethod
    def get_wallet_eth(session, address):
        return session.query(WalletEthModel).filter(WalletEthModel.sub_public_address == address).first()

    @staticmethod
    def get_wallet_eth_by_account(session, account_id):
        return session.query(WalletEthModel).filter(WalletEthModel.account_id == account_id and WalletEthModel.status == _ONE).first()

    @staticmethod
    def get_wallet_eth_gather(session, address):
        return session.query(WalletEthGatherModel).filter(WalletEthGatherModel.sub_public_address == address).first()

    @staticmethod
    def get_wallet_eth_tx():
        """
        获取需要侦听的 eth Tx
        :param session:
        :return:
        """
        with MysqlTools().session_scope() as session:
            eth_tx_model = session.query(TxListeningEthModel).filter(TxListeningEthModel.source_status == _ZERO_S, TxListeningEthModel.listen_flag == _ONE).all()
            # 处理 侦听TX列表
            eth_tx_list = []
            if eth_tx_model:
                for eth_tx in eth_tx_model:
                    eth_tx_list.append(eth_tx.tx_no)
        return eth_tx_model, eth_tx_list

    @staticmethod
    def update_wallet_eth_tx(session, tx):
        # session.query(TxListeningEthModel).filter(TxListeningEthModel.tx_no == tx).update({TxListeningEthModel.listen_flag: _ZERO})
        return session.query(TxListeningEthModel).filter(TxListeningEthModel.tx_no == tx).first()

    @staticmethod
    def get_foreign_withdraw_order_record(session, record_no):
        return session.query(ForeignWithdrawOrderRecordModel).filter(ForeignWithdrawOrderRecordModel.order_no == record_no).first()

    @staticmethod
    def get_foreign_multi_withdraw_order_record(session, record_id):
        return session.query(ForeignMultiWithdrawRecordModel).filter(ForeignMultiWithdrawRecordModel.record_id == record_id).first()

    @staticmethod
    def get_foreign_gather_record(session, record_id):
        return session.query(ForeignGatherRecordModel).filter(ForeignGatherRecordModel.record_id == record_id).first()

    def get_eth_block_info(self, number):
        return self.convert_info_to_json(self.w3.eth.getBlock(number))

    def get_eth_tx_info(self, tx):
        return self.convert_info_to_json(self.w3.eth.getTransaction(tx))

    def get_eth_tx_info_receipt(self, tx):
        return self.convert_info_to_json(self.w3.eth.getTransactionReceipt(tx))

    def get_eth_tx_info_by_block(self, block_identifier, transaction_index):
        return self.convert_info_to_json(self.w3.eth.getTransactionByBlock(block_identifier, transaction_index))

    def sync_block(self, token_conf, last_net_block_num, last_local_block, address_list, gather_address_list, eth_tx_list):
        confirm_last_block_num = token_conf["confirm_last_block_num"]
        end_listen_block_num = int(last_net_block_num) - int(confirm_last_block_num)
        # 确认起始侦听区块号
        if not last_local_block:
            begin_listen_block_num = end_listen_block_num
        else:
            if end_listen_block_num <= _ZERO:
                raise Exception("last net_block_num less than confirm_last_block_num")
            last_local_block_num = last_local_block["block_no"]
            last_local_block_status = last_local_block["status"]
            begin_listen_block_num = last_local_block_num + _ONE if last_local_block_status else last_local_block_num

        for listen_num in range(begin_listen_block_num, end_listen_block_num + _ONE):
            if self.process_index is not None:
                if listen_num % self.process_count != self.process_index:
                    continue
            self.slog.info("listen block: ", str(listen_num))
            block_info = self.get_eth_block_info(listen_num)
            block_hash = block_info["hash"]
            block_number = block_info["number"]
            transactions = block_info["transactions"]
            tx_model_list = []
            multi_withdraw_record = None
            foreign_gather_record = None
            wallet_eth = None
            with MysqlTools().session_scope() as session:
                for tx in transactions:
                    # 查询交易详情
                    tx_info = self.get_eth_tx_info(tx)
                    if not tx_info:
                        continue
                    tx_info_receipt = self.get_eth_tx_info_receipt(tx)
                    # 处理 块上的交易Tx 是否碰撞 平台发起的交易Tx
                    if tx in eth_tx_list:
                        # 获取实际到账金额 和 手续费
                        listening_value_ether = get_decimal(self.w3.fromWei(tx_info["value"], self.unit) if tx_info["value"] else _ZERO_S, 18)
                        listening_gas_price_ether = get_decimal(self.w3.fromWei(int(tx_info["gasPrice"]), self.unit) if tx_info["gasPrice"] else _ZERO_S, 18)
                        listening_gas_price_used_ether = get_decimal(tx_info_receipt["gasUsed"] if tx_info_receipt["gasUsed"] else _ZERO_S, 18)
                        listening_gas_ether = listening_gas_price_ether * listening_gas_price_used_ether
                        # 如果存在 更改listening 提现侦听表 状态
                        listening_tx = self.update_wallet_eth_tx(session, tx)
                        listening_tx.listen_flag = _ZERO
                        listening_tx.block_no = block_number
                        record_no = listening_tx.record_no
                        # 改流水表 成功
                        withdraw_order_record = self.get_foreign_withdraw_order_record(session, record_no)
                        if not withdraw_order_record:
                            self.slog.error("没有找到withdraw_order_record根据listening_tx.record_no:", record_no)
                            continue
                        withdraw_order_record.withdraw_status = self.withdraw_success
                        withdraw_order_record.confirm_at = get_utc_now()

                        # 计算已花费未上块时消耗的手续费累计,如果没有一般是0
                        withdraw_consume_total_fee = get_decimal(withdraw_order_record.withdraw_consume_total_fee, 18)
                        # 计算预计冻结金额
                        amount_frozen = withdraw_order_record.withdraw_amount
                        # 计算花费完手续费剩余返还给用户的金额
                        withdraw_remain_fee = amount_frozen - listening_value_ether - listening_gas_ether - withdraw_consume_total_fee
                        # 判断 提现类型 用户提现和中奖
                        if withdraw_order_record.withdraw_type in self.account_withdraw_type_list:

                            # 获取 批量提现流水
                            if not multi_withdraw_record:
                                multi_withdraw_record = self.get_foreign_multi_withdraw_order_record(session, withdraw_order_record.relate_flow_no)

                            # 通知 账户成功
                            withdraw_result = _FOUR_S
                            do_withdraw_result = WalletCallbackService.withdraw_notify_callback(withdraw_order_record.req_no, withdraw_order_record.order_no, withdraw_result,
                                                                                                listening_value_ether, listening_gas_ether, withdraw_remain_fee)
                            # 保存 账户处理结果
                            withdraw_order_record.do_withdraw_result = do_withdraw_result

                            # 判断用户系统返回结果 "0"是正确
                            if do_withdraw_result == _ZERO_S:
                                # 加钱 提现流水 单笔
                                withdraw_order_record.withdraw_actual_amount = listening_value_ether
                                withdraw_order_record.withdraw_actual_fee = listening_gas_ether + withdraw_consume_total_fee

                                # 加钱 批量提现流水 累计
                                multi_withdraw_record.verified_amount += listening_value_ether
                                multi_withdraw_record.verified_gas += listening_gas_ether + withdraw_consume_total_fee

                                # 减钱 归集地址 冻结金额
                                wallet_eth = self.get_wallet_eth_gather(session, withdraw_order_record.from_address)
                                wallet_eth.amount_frozen -= amount_frozen
                                wallet_eth.amount += withdraw_remain_fee

                        # 判断 提现类型 普通归集和归集转归集
                        elif withdraw_order_record.withdraw_type in self.gather_withdraw_type_list:

                            # 获取 归集操作流水
                            if not foreign_gather_record:
                                foreign_gather_record = self.get_foreign_gather_record(session, withdraw_order_record.relate_flow_no)

                            # 加钱 提现流水 单笔
                            withdraw_order_record.withdraw_actual_amount = listening_value_ether
                            withdraw_order_record.withdraw_actual_fee = listening_gas_ether + withdraw_consume_total_fee

                            # 加钱 归集流水 累计
                            foreign_gather_record.actual_amount += listening_value_ether
                            foreign_gather_record.actual_fee += listening_gas_ether + withdraw_consume_total_fee

                            # 更新 归集流水 部分成功
                            foreign_gather_record.gather_status = self.withdraw_part_success

                            # 判断 普通归集
                            if withdraw_order_record.withdraw_type == _TWO_S:
                                # 获取 用户地址
                                wallet_eth = self.get_wallet_eth(session, withdraw_order_record.from_address)
                            # 判断 归集转归集
                            elif withdraw_order_record.withdraw_type == _THREE_S:
                                # 获取 归集地址
                                wallet_eth = self.get_wallet_eth_gather(session, withdraw_order_record.from_address)

                            # 减钱 相关地址 冻结金额
                            wallet_eth.amount_frozen -= amount_frozen
                            wallet_eth.amount += withdraw_remain_fee
                        else:
                            # 其他类型 暂不处理
                            pass
                        self.slog.info("listening block_number: ", str(block_number))
                        self.slog.info("listening tx: ", str(tx))
                        self.slog.info("listening amount: ", str(listening_value_ether))
                        self.slog.info("listening gas: ", str(listening_gas_ether))

                    # 处理 块上的每笔交易Tx详情 to_address 是否碰撞 平台的子钱包地址 和 归集账户的地址
                    listening_address = tx_info["to"]
                    check_address_flag = None
                    source_status = None
                    do_recharge_result = ""
                    if listening_address in address_list:
                        check_address_flag = _ZERO
                    elif listening_address in gather_address_list:
                        check_address_flag = _ONE
                    if check_address_flag is not None:
                        listening_value_ether = get_decimal(self.w3.fromWei(tx_info["value"], self.unit) if tx_info["value"] else _ZERO_S, 18)

                        # 检查 有没有记录过这个tx在tx_list_eth流水
                        tx_list_model = session.query(TxListEthModel).filter(TxListEthModel.tx_no == tx).first()
                        if not tx_list_model:
                            tx_id = generate_order_no()
                            # 更新子钱包和归集账户地址的钱
                            wallet_model = self.wallet_model_list[check_address_flag]
                            sub_wallet = session.query(wallet_model).filter(wallet_model.sub_public_address == listening_address).first()
                            if check_address_flag == _ZERO:
                                account_id = sub_wallet.account_id
                                # 通知账户加钱
                                do_recharge_result = WalletCallbackService.recharge_notify_callback(account_id, listening_value_ether, self.coin_id, listening_address, tx_id)
                                if do_recharge_result == _ZERO_S:
                                    # 更新子钱包和归集账户地址的钱
                                    sub_wallet.amount += listening_value_ether
                                source_status = _ZERO_S  # 线上用户地址充值
                            elif check_address_flag == _ONE:
                                if tx not in eth_tx_list:
                                    source_status = _ONE_S  # 线下归集账户充值
                                else:
                                    source_status = _ZERO_S  # 线上普通归集归集转归集
                                sub_wallet.amount += listening_value_ether  # 线下充值或者归集

                            # 增加tx_list记录
                            tx_model = TxListEthModel(
                                tx_id=tx_id,
                                tx_no=tx,
                                block_no=block_number,
                                value=listening_value_ether,
                                address=listening_address,
                                source_status=source_status,
                                do_recharge_result=do_recharge_result
                            )
                            tx_model_list.append(tx_model)
                        if tx not in eth_tx_list:
                            self.slog.info("recharge block_number: ", str(block_number))
                            self.slog.info("recharge tx: ", str(tx))
                            self.slog.info("recharge address: ", str(listening_address))
                            self.slog.info("recharge amount: ", str(listening_value_ether))

                if tx_model_list:
                    session.add_all(tx_model_list)
                # 更新SyncBlockModel本地同步远程节点数据块编号
                if not self.block_num_temp:
                    self.update_wallet_eth_address(session, listen_num, block_hash)

                # 提交事物
                session.commit()
        return True

    def check_and_update_tx_flag(self, eth_tx_model, confirm_last_err_days):
        today = get_day_datetime()
        with MysqlTools().session_scope() as session:
            for tx in eth_tx_model:
                update_time = get_datetime_from_str(str(tx.update_at))
                d_val = days_diff(update_time, today)
                if d_val > confirm_last_err_days:
                    tx.listen_flag = _ZERO
                    record_no = tx.record_no

                    # 更改 提现流水 单笔 状态失败
                    withdraw_order_record = self.get_foreign_withdraw_order_record(session, record_no)
                    if withdraw_order_record:
                        withdraw_order_record.withdraw_status = self.withdraw_fail

                        if tx.withdraw_type in self.account_withdraw_type_list:
                            # 更改 批量提现流水 单笔 状态部分失败
                            multi_withdraw_record = self.get_foreign_multi_withdraw_order_record(session, withdraw_order_record.relate_flow_no)
                            if multi_withdraw_record:
                                multi_withdraw_record.withdraw_status = self.withdraw_part_success
                        elif tx.withdraw_type in self.gather_withdraw_type_list:
                            # 更改 归集操作流水 单笔 状态部分失败
                            gather_record = self.get_foreign_gather_record(session, withdraw_order_record.relate_flow_no)
                            if gather_record:
                                gather_record.gather_status = self.withdraw_part_success
            session.commit()

                # 如果是用户提现或者中奖 代码待更改
                # if tx.withdraw_type in self.account_withdraw_type_list:
                #     listening_value_ether = get_decimal("0")
                #     listening_gas_ether = get_decimal("0")
                #     # 告诉账户 提现失败
                #     do_withdraw_result = WalletCallbackService.withdraw_notify_callback(session, withdraw_order_record.req_no, \
                #     withdraw_order_record.order_no, self.callback_account_withdraw_fail, listening_value_ether, listening_gas_ether, withdraw_remain_fee)
                #     withdraw_order_record.do_withdraw_result = do_withdraw_result
        return True

    def check_and_update_multi_withdraw(self):
        with MysqlTools().session_scope() as session:
            multi_withdraw_record_list = session.query(ForeignMultiWithdrawRecordModel).filter(ForeignMultiWithdrawRecordModel.withdraw_status == self.withdraw_process_ing,
                                                                                               ForeignMultiWithdrawRecordModel.coin_id == self.coin_id).all()
            if not multi_withdraw_record_list:
                return True
            for multi_withdraw_record in multi_withdraw_record_list:
                multi_withdraw_record_record_id = multi_withdraw_record.record_id
                withdraw_order_record = session.query(ForeignWithdrawOrderRecordModel).filter(ForeignWithdrawOrderRecordModel.relate_flow_no == multi_withdraw_record_record_id,
                                                                                              ForeignWithdrawOrderRecordModel.withdraw_status != self.withdraw_success).first()
                if not withdraw_order_record:
                    multi_withdraw_record.withdraw_status = self.withdraw_success
            session.commit()
        return True

    def check_and_update_gather(self):
        with MysqlTools().session_scope() as session:
            gather_record_list = session.query(ForeignGatherRecordModel).filter(ForeignGatherRecordModel.gather_status != self.withdraw_success,
                                                                                ForeignGatherRecordModel.coin_id == self.coin_id).all()
            if not gather_record_list:
                return True
            for gather_record in gather_record_list:
                gather_record_record_id = gather_record.record_id
                gather_order_record = session.query(ForeignWithdrawOrderRecordModel).filter(ForeignWithdrawOrderRecordModel.relate_flow_no == gather_record_record_id,
                                                                                              ForeignWithdrawOrderRecordModel.withdraw_status != self.withdraw_success).first()
                if not gather_order_record:
                    gather_record.withdraw_status = self.withdraw_success
            session.commit()
        return True


if __name__ == "__main__":
    tes = TokenEthScript()
    res = tes.work()
    if res:
        tes.slog.info("sync block success!")
    else:
        tes.slog.info("sync block fail!")
