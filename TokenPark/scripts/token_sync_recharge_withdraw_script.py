import sys
import time
from pathlib import Path

pro_name = "TokenPark"
current_path = str(Path(__file__).resolve())
import_index = current_path.rfind(pro_name)
import_path = current_path[:import_index + len(pro_name)]
path_flag = True if not import_path in sys.path else False
if path_flag:
    sys.path.append(import_path)

from tools.mysql_tool import MysqlTools
from models.sync_block_model import SyncBlockModel
from models.token_node_conf_model import TokenNodeConfModel
from models.tx_list_eos_model import TxListEosModel
from models.wallet_eos_model import WalletEosModel
from models.foreign_withdraw_order_record_model import ForeignWithdrawOrderRecordModel
from models.token_conf_model import TokenConfModel
from models.tx_listening_eos_model import TxListeningEosModel
from models.wallet_eos_gather_model import WalletEosGatherModel
from services.wallet_callback_service import WalletCallbackService
from utils.util import get_decimal, generate_order_no
from common_settings import *
from utils.log import Slog
from config import get_env

# 第一个事,获取当前最新区块号,同步所有区块,一分钟一次


class TokenSyncRechargeWithdrawScript(object):
    ec = None
    sync_success = _ONE
    sync_fail = _ZERO
    eos_coin_id = _COIN_ID_EOS
    slog = Slog("token_sync_recharge_withdraw_script")
    mysql_tool = MysqlTools()
    wait_lottery_dict = {}
    eos_gather_address = _EOS_RECHARGE_ADDRESS[get_env()]
    wallet_callback = None
    withdraw_online_success = _FOUR_S
    withdraw_offline_success = _SEVEN_S
    withdraw_success = _TWO_S

    def __init__(self):
        pass

    def work(self):
        # 逻辑:
        # 1. 查询SyncBlockModel trace_count
        # 2. 调EosPark get_account_related_trx_info 第一页 如果和 trace_count 相同 返回查询完成
        # 3. 如果不相同 查询tx_list_eos的列表
        # 4. 遍历所有的 get_account_related_trx_info 从第二页开始,直到返回空, 拼接list
        # 5. 遍历list 找到符合条件的 充值交易,并且在 tx_list_eos的列表里没有的,通过交易hash判断, 遍历listening list 找到符合条件的 提现交易
        # 6. 插入tx_list_eos新的充值记录 更新 listening list 提现记录表
        # 7. 同时 通知永涛回调 并 记录状态 充值 和 提现

        trace_count = self.get_trace_count()
        remote_trace_count = self.get_account_related_trx_info().get("trace_count")
        if remote_trace_count == trace_count:
            return True
        tx_eos_list = self.get_tx_eos_list()  # 充值记录表
        tx_listening_eos_dict = self.get_tx_listening_eos_dict()  # 提现记录表
        account_related_trx_info_list = self.get_account_related_trx_info_list()
        if not account_related_trx_info_list:  # 账户的actions是空的
            return True
        account_related_trx_info_recharge_dict = {}
        account_related_trx_info_withdraw_dict = {}
        for account_related_trx_info in account_related_trx_info_list:
            trx_id = account_related_trx_info.get("trx_id", "")
            if trx_id and trx_id not in tx_eos_list:
                receiver = account_related_trx_info.get("receiver", "")
                if receiver == self.eos_gather_address:
                    memo = account_related_trx_info.get("memo", "").strip()
                    if len(memo) == _EIGHT and memo[_ZERO] == _ONE_S:
                        try:
                            sub_account_address = int(memo)
                        except:
                            continue
                        status = account_related_trx_info.get("status", "")
                        symbol = account_related_trx_info.get("symbol", "")
                        code = account_related_trx_info.get("code", "")
                        if status == "executed" and symbol == "EOS" and code == "eosio.token":
                            quantity = account_related_trx_info.get("quantity", "")
                            sender = account_related_trx_info.get("sender", "")
                            timestamp = account_related_trx_info.get("timestamp", "")
                            block_num = account_related_trx_info.get("block_num", "")
                            account_related_trx_info_recharge_dict[trx_id] = {
                                "quantity": quantity,
                                "sender": sender,
                                "timestamp": timestamp,
                                "block_num": block_num,
                                "address": str(sub_account_address),
                            }
            if trx_id and trx_id in tx_listening_eos_dict:
                sender = account_related_trx_info.get("sender", "")
                if sender == self.eos_gather_address:
                    memo = account_related_trx_info.get("memo", "").strip()
                    status = account_related_trx_info.get("status", "")
                    symbol = account_related_trx_info.get("symbol", "")
                    code = account_related_trx_info.get("code", "")
                    if status == "executed" and symbol == "EOS" and code == "eosio.token":
                        quantity = account_related_trx_info.get("quantity", "")
                        receiver = account_related_trx_info.get("receiver", "")
                        timestamp = account_related_trx_info.get("timestamp", "")
                        block_num = account_related_trx_info.get("block_num", "")
                        account_related_trx_info_withdraw_dict[trx_id] = {
                            "quantity": quantity,
                            "receiver": receiver,
                            "timestamp": timestamp,
                            "block_num": block_num,
                            "order_no": tx_listening_eos_dict[trx_id]["order_no"],
                            "record_no": tx_listening_eos_dict[trx_id]["record_no"],
                            "source_status": tx_listening_eos_dict[trx_id]["source_status"],
                            "memo": memo,
                        }
        self.process_notify_and_insert(account_related_trx_info_recharge_dict, account_related_trx_info_withdraw_dict)

        # 记录当前侦听过的EOSPark的交易数
        self.update_trace_count(remote_trace_count)

        return True

    def get_trace_count(self):
        trace_count = _ZERO
        with self.mysql_tool.session_scope() as session:
            trace_count_model = session.query(SyncBlockModel.trace_count).filter(SyncBlockModel.coin_id == self.eos_coin_id).first()
            if trace_count_model:
                trace_count = int(trace_count_model[_ZERO])
            return trace_count

    def update_trace_count(self, remote_trace_count):
        with self.mysql_tool.session_scope() as session:
            trace_count_model = session.query(SyncBlockModel).filter(SyncBlockModel.coin_id == self.eos_coin_id).first()
            if trace_count_model:
                trace_count_model.trace_count = str(remote_trace_count)
            session.commit()
        return True

    def get_account_related_trx_info(self, page=None):
        if not self.ec:
            self.ec = TokenNodeConfModel.get_eos_node_script(script_unit=_TWO_S)

        account_related_trx_info = self.ec.http_get_account_related_trx_info(page=page, account=self.eos_gather_address)
        if not account_related_trx_info.get("trace_count", ""):
            raise Exception("EOSPark node get_account_related_trx_info has error!")
        return account_related_trx_info

    def get_tx_eos_list(self):
        with self.mysql_tool.session_scope() as session:
            tx_eos_list = []
            tx_eos_list_tuple_list = session.query(TxListEosModel.tx_no).all()
            if tx_eos_list_tuple_list:
                for i in tx_eos_list_tuple_list:
                    tx_eos_list.append(i[_ZERO])
            return tx_eos_list

    def get_tx_listening_eos_dict(self):
        with self.mysql_tool.session_scope() as session:
            tx_eos_dict = {}
            tx_listening_eos_model_list = session.query(TxListeningEosModel).filter(TxListeningEosModel.listen_flag == _ONE).all()
            if tx_listening_eos_model_list:
                for tx_listening_eos_model in tx_listening_eos_model_list:
                    tx_no = tx_listening_eos_model.tx_no
                    order_no = tx_listening_eos_model.order_no
                    record_no = tx_listening_eos_model.record_no
                    source_status = tx_listening_eos_model.source_status
                    tx_eos_dict[tx_no] = {"order_no": order_no, "record_no": record_no, "source_status": source_status}
            return tx_eos_dict

    def get_account_related_trx_info_list(self):
        account_related_trx_info_list = []
        page = _ONE
        while True:
            tmp_get_account_related_trx_info = self.get_account_related_trx_info(page)
            trace_list = tmp_get_account_related_trx_info.get("trace_list", "")
            if not trace_list:
                break
            for tmp_trx_info in trace_list:
                account_related_trx_info_list.append(tmp_trx_info)
            page += _ONE
            time.sleep(0.5)
        return account_related_trx_info_list

    def process_notify_and_insert(self, account_related_trx_info_dict, account_related_trx_info_withdraw_dict):
        # tx_list_eos_model_list = []
        if not self.wallet_callback:
            self.wallet_callback = WalletCallbackService()

        with self.mysql_tool.session_scope() as session:
            # 提现手续费
            withdraw_actual_fee = 0.02
            token_conf_model = session.query(TokenConfModel).filter(TokenConfModel.coin_id == self.eos_coin_id).first()
            if token_conf_model:
                withdraw_actual_fee = token_conf_model.withdraw_fee
            # 充值
            for trx_id, trx_info in account_related_trx_info_dict.items():
                transaction_id = generate_order_no()
                sub_public_address = trx_info["address"]
                token_amount = get_decimal(trx_info["quantity"], digits=_TEN)
                do_recharge_result = ""
                wallet_eos_model = session.query(WalletEosModel).filter(WalletEosModel.sub_public_address == sub_public_address).with_for_update().first()
                wallet_eos_gather_model = session.query(WalletEosGatherModel).filter(WalletEosGatherModel.sub_public_address == self.eos_gather_address).with_for_update().first()
                if wallet_eos_model:
                    # 加钱 给 账户钱包
                    wallet_eos_model.amount += token_amount
                    wallet_eos_gather_model.amount += token_amount
                    # 通知 账户模块
                    account_id = wallet_eos_model.account_id
                    do_recharge_result = self.wallet_callback.recharge_notify_callback(account_id, token_amount, self.eos_coin_id, sub_public_address, transaction_id)
                    # 存充值记录表
                tmp_tx_list_eos_model = TxListEosModel(
                    tx_id=transaction_id,
                    tx_no=trx_id,
                    block_no=trx_info["block_num"],
                    value=token_amount,
                    address=sub_public_address,
                    sender=trx_info["sender"],
                    do_recharge_result=do_recharge_result,
                )
                session.add(tmp_tx_list_eos_model)
                session.commit()
            # 提现
            for withdraw_trx_id, withdraw_trx_info in account_related_trx_info_withdraw_dict.items():
                withdraw_actual_amount = get_decimal(withdraw_trx_info["quantity"], digits=_TEN)
                foreign_withdraw_model = session.query(ForeignWithdrawOrderRecordModel).filter(ForeignWithdrawOrderRecordModel.order_no == withdraw_trx_info["record_no"]).first()
                if foreign_withdraw_model:
                    account_id = foreign_withdraw_model.account_id
                    order_no = foreign_withdraw_model.order_no
                    req_no = foreign_withdraw_model.req_no
                    withdraw_result = self.withdraw_offline_success if withdraw_trx_info["source_status"] == _ONE_S else self.withdraw_online_success
                    # 通知
                    do_withdraw_result = self.wallet_callback.withdraw_notify_callback(req_no, order_no, withdraw_result, withdraw_actual_amount, withdraw_actual_fee)
                    # 更新提现状态
                    foreign_withdraw_model.withdraw_actual_amount = withdraw_actual_amount
                    foreign_withdraw_model.withdraw_actual_fee = withdraw_actual_fee
                    foreign_withdraw_model.withdraw_status = self.withdraw_success
                    foreign_withdraw_model.do_withdraw_result = do_withdraw_result
                    # 修改冻结金额
                    wallet_eos_model = session.query(WalletEosModel).filter(WalletEosModel.account_id == account_id).with_for_update().first()
                    wallet_eos_gather_model = session.query(WalletEosGatherModel).filter(WalletEosGatherModel.sub_public_address == self.eos_gather_address).with_for_update().first()
                    if wallet_eos_model:
                        amount_frozen = withdraw_actual_amount + withdraw_actual_fee
                        wallet_eos_model.amount_frozen -= amount_frozen
                        wallet_eos_gather_model.amount_frozen -= amount_frozen
                        wallet_eos_gather_model.amount += withdraw_actual_fee
                    else:
                        self.slog.error("withdraw not has WalletEosModel by ForeignWithdrawOrderRecordModel.account_id: " + str(account_id))
                else:
                    self.slog.error("withdraw not has ForeignWithdrawOrderRecordModel by TxListeningEosModel.record_no: " + str(withdraw_trx_info["record_no"]))

                # 更新提现记录表侦听状态
                tx_listening_eos_model = session.query(TxListeningEosModel).filter(TxListeningEosModel.order_no == withdraw_trx_info["order_no"]).first()
                if tx_listening_eos_model:
                    tx_listening_eos_model.block_no = withdraw_trx_info["block_num"]
                    tx_listening_eos_model.listen_flag = _ZERO
                    tx_listening_eos_model.memo = withdraw_trx_info["memo"]
                else:
                    self.slog.error("withdraw not has TxListeningEosModel by TxListeningEosModel.order_no: " + str(withdraw_trx_info["order_no"]))
                session.commit()

                # tx_list_eos_model_list.append(tmp_tx_list_eos_model)
            # session.add_all(tx_list_eos_model_list)


if __name__ == "__main__":
    sbe = TokenSyncRechargeWithdrawScript()
    res = sbe.work()
    if res:
        sbe.slog.info("eos recharge withdraw success!")
    else:
        sbe.slog.info("eos recharge withdraw fail!")
