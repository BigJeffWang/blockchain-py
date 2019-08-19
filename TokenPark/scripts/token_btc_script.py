import sys
from pathlib import Path

pro_name = "TokenPark"
current_path = str(Path(__file__).resolve())
import_index = current_path.rfind(pro_name)
import_path = current_path[:import_index + len(pro_name)]
path_flag = True if not import_path in sys.path else False
if path_flag:
    sys.path.append(import_path)

from services.wallet_callback_service import WalletCallbackService
from tools.mysql_tool import MysqlTools
from models.sync_block_model import SyncBlockModel
from models.tx_list_btc_model import TxListBtcModel
from models.wallet_btc_model import WalletBtcModel
from models.wallet_btc_gather_model import WalletBtcGatherModel
from models.tx_listening_btc_model import TxListeningBtcModel
from models.foreign_withdraw_order_record_model import ForeignWithdrawOrderRecordModel
from models.foreign_gather_record_model import ForeignGatherRecordModel
from models.token_conf_model import TokenConfModel
from models.account_change_record_model import AccountChangeRecordModel
from models.foreign_multi_withdraw_record_model import ForeignMultiWithdrawRecordModel
from utils.util import *
from common_settings import *
from utils.log import Slog
from models.token_node_conf_model import TokenNodeConfModel


class TokenBtcScript(object):
    coin_id = "0"  # BTC
    slog = Slog("token_btc_script")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.block_flag = 0  # 定时器状态，默认0:未启动，1:运行中
        # self.rpc = btc_rpc_client()
        self.rpc = TokenNodeConfModel.get_btc_node_script()

    # 定时循环查询BTC UTXO--1、查询余额监听器
    def btc_block_listener(self, count=_ZERO):
        if count >= _HUNDRED:
            return
        # 保证同期只有一个此定时器在运行
        if self.block_flag == 1:
            return
        else:
            self.block_flag == 1
        cover = False  # 覆盖标识
        with MysqlTools().session_scope() as session:
            btc_block = session.query(SyncBlockModel).filter(SyncBlockModel.coin_id == _ZERO).first()
            block_no = btc_block.block_no
            status = btc_block.status
            try:
                block_count = self.rpc.getblockcount()  # 查询链上最优最近区块号
            except Exception as err:  # 连接异常
                self.slog.info(err)
                self.btc_block_listener_api()
                return
            token_conf = session.query(TokenConfModel).filter(TokenConfModel.coin_id == _ZERO_S).first()
            confirmations = token_conf.confirm_last_block_num  # 区块确认次数
            block_count = block_count - int(confirmations) + 1
            if block_count > block_no and status == 1:  # 大于本地且本地已执行完毕--从本地区块号+1开始工作
                block_no = block_no + 1
                block_hash = self.rpc.getblockhash(block_no)
            elif block_count > block_no and status == 0:  # 大于本地且本地未执行完毕--从本地区块号开始工作并覆盖
                block_hash = self.rpc.getblockhash(block_no)
                cover = True
            elif block_count == block_no and status == 1:  # 等于本地且本地已执行完毕--return
                self.block_flag = 0
                return
            elif block_count == block_no and status == 0:  # 等于本地且本地未执行完毕--从本地区块号开始工作并覆盖
                block_hash = self.rpc.getblockhash(block_no)
                cover = True
            else:  # 其他情况(小于本地）
                self.block_flag = 0
                return
            self.slog.info(block_no)
            block_map = self.rpc.getblock(block_hash)
            btc_block.block_no = block_map.get("height")
            btc_block.block_hash = block_map.get("hash")
            btc_block.status = 0
            session.commit()
            if cover:  # 删除之前未执行完毕的tx[不会出现此类情况]
                session.query(TxListBtcModel).filter(TxListBtcModel.block_no == block_no).delete(
                    synchronize_session=False)
                session.commit()
            tx_list = block_map["tx"]

            # 建立子钱包地址list、归集账户地址list
            wallet_btc = session.query(WalletBtcModel.sub_public_address).filter(WalletBtcModel.account_id != "").all()
            sub_address_list = []
            for w in wallet_btc:
                sub_address_list.append(w.sub_public_address)
            wallet_btc_gather = session.query(WalletBtcGatherModel.sub_public_address).all()
            gather_address_list = []
            for w in wallet_btc_gather:
                gather_address_list.append(w.sub_public_address)
            # 建立tx监听list
            tx_listening_btc = session.query(TxListeningBtcModel).filter(TxListeningBtcModel.listen_flag == _ONE).all()
            tx_listening_list = []
            for t in tx_listening_btc:
                tx_listening_list.append(t.tx_no)
            btc_tx_add_list = []
            tx_count = 1
            tx_size = len(tx_list)
            tx_size_s = "/" + str(tx_size)
            for tx in tx_list:
                self.slog.info(str(tx_count) + tx_size_s)
                tx_count += 1
                # if tx != "c22d1ddfed78a446eb608c0bec0bfa00aa83c63893b891784dd626798ed6981c":
                #     continue
                if tx in tx_listening_list:  # tx在tx监听列表中
                    tl = session.query(TxListeningBtcModel).filter(TxListeningBtcModel.tx_no == tx,
                                                                   TxListeningBtcModel.listen_flag == _ONE).first()
                    tl.listen_flag = _ZERO  # 修改监听状态
                    tl.block_no = block_no
                    multi_flag = tl.multi_flag
                    if multi_flag == _ONE:  # 1对多转账(提现)
                        fmwr = session.query(ForeignMultiWithdrawRecordModel).filter(
                            ForeignMultiWithdrawRecordModel.record_id == tl.record_no).first()
                        fmwr.withdraw_status = _TWO_S
                        fmwr.verified_amount = fmwr.amount
                        fmwr.verified_gas = fmwr.gas
                        fwor_list = session.query(ForeignWithdrawOrderRecordModel).filter(
                            ForeignWithdrawOrderRecordModel.relate_flow_no == fmwr.record_id).all()
                        '''
                            1对多转账(提现):
                            当前方法实现:1、调user接口通知进账,2、修改withdraw表,3、修改归集账户表(from_address)字段:[找零][已支付未确认到账]
                            扫描地址实现:1、给归集账户(from_address)增加余额{找零}utxo{找零}
                        '''
                        for f in fwor_list:
                            result = WalletCallbackService().withdraw_notify_callback(f.req_no,
                                                                                      f.order_no,
                                                                                      AccountChangeRecordModel.change_type_4,
                                                                                      f.withdraw_amount - f.withdraw_fee,
                                                                                      f.withdraw_fee)  # 提现user接口
                            session.query(ForeignWithdrawOrderRecordModel).filter(
                                ForeignWithdrawOrderRecordModel.order_no == f.order_no).update({
                                ForeignWithdrawOrderRecordModel.withdraw_actual_amount: ForeignWithdrawOrderRecordModel.withdraw_amount - ForeignWithdrawOrderRecordModel.withdraw_fee,
                                ForeignWithdrawOrderRecordModel.withdraw_status: _TWO_S,
                                ForeignWithdrawOrderRecordModel.do_withdraw_result: result,
                                ForeignWithdrawOrderRecordModel.confirm_at: get_now_time()
                            })

                        session.query(WalletBtcGatherModel).filter(
                            WalletBtcGatherModel.sub_public_address == fmwr.from_address).update({
                            WalletBtcGatherModel.amount_change: WalletBtcGatherModel.amount_change - fmwr.amount_change,
                            WalletBtcGatherModel.amount_frozen: WalletBtcGatherModel.amount_frozen - (
                                    fmwr.amount - fmwr.gas)
                        })
                    elif multi_flag == _ZERO:  # 1对1转账(归集、归集转归集)
                        fwor = session.query(ForeignWithdrawOrderRecordModel).filter(
                            ForeignWithdrawOrderRecordModel.order_no == tl.record_no).first()  # 查询withdraw提现记录表数据
                        if fwor is not None:
                            withdraw_actual_amount = fwor.withdraw_amount - fwor.withdraw_fee
                            fwor.withdraw_actual_amount = withdraw_actual_amount  # 修改提现记录实际到账金额
                            fwor.withdraw_status = _TWO_S  # 修改提现记录表状态
                            fwor.confirm_at = get_now_time()  # 更新到账时间

                            if fwor.withdraw_type == _TWO_S:
                                '''
                                    归集:
                                    当前方法实现:1、归集记录表叠加确认金额,2、修改归集账户(from_address)表字段:[找零][已支付未确认到账]{正常情况下不会存在找零}
                                    扫描地址实现:1、给归集账户(to_address)表增加余额{进账}utxo{进账},2、给归集账户(from_address)增加余额{找零}utxo{找零}
                                '''
                                session.query(ForeignGatherRecordModel).filter(
                                    ForeignGatherRecordModel.record_id == fwor.relate_flow_no).update(
                                    {
                                        ForeignGatherRecordModel.actual_amount: ForeignGatherRecordModel.actual_amount + withdraw_actual_amount,
                                        ForeignGatherRecordModel.gather_status: _TWO_S})  # 归集记录表叠加确认金额
                                # 修改wallet_btc表(from_address)
                                session.query(WalletBtcModel).filter(
                                    WalletBtcModel.sub_public_address == fwor.from_address).update({
                                    WalletBtcModel.amount_change: WalletBtcModel.amount_change - fwor.amount_change,
                                    WalletBtcModel.amount_frozen: WalletBtcModel.amount_frozen - withdraw_actual_amount
                                })
                            elif fwor.withdraw_type == _THREE_S:
                                '''
                                    归集转归集:
                                    当前方法实现:1、归集记录表叠加确认金额,2、修改归集账户(from_address)表字段:[找零][已支付未确认到账]
                                    扫描地址实现:1、给归集账户(to_address)表增加余额{进账}utxo{进账}2、给归集账户(from_address)增加余额{找零}utxo{找零}
                                '''
                                session.query(ForeignGatherRecordModel).filter(
                                    ForeignGatherRecordModel.record_id == fwor.relate_flow_no).update(
                                    {
                                        ForeignGatherRecordModel.actual_amount: ForeignGatherRecordModel.actual_amount + withdraw_actual_amount})  # 归集记录表叠加确认金额
                                # 修改wallet_btc_gather表(from_address)
                                session.query(WalletBtcGatherModel).filter(
                                    WalletBtcGatherModel.sub_public_address == fwor.from_address).update({
                                    WalletBtcGatherModel.amount_change: WalletBtcGatherModel.amount_change - fwor.amount_change,
                                    WalletBtcGatherModel.amount_frozen: WalletBtcGatherModel.amount_frozen - fwor.withdraw_amount
                                })
                transaction_map = self.rpc.getrawtransaction(tx, True, block_hash)
                vout = transaction_map.get("vout")
                for v in vout:
                    value = get_decimal(v.get("value"), 18)
                    if value == 0:
                        continue
                    else:
                        scriptPubKey = v.get("scriptPubKey")
                        if scriptPubKey is None:
                            continue
                        else:
                            type = scriptPubKey.get("type")
                            if type == "multisig":  # 多重签名
                                continue
                            addresses = scriptPubKey.get("addresses")
                            if addresses is None:
                                continue
                            for address in addresses:
                                if address in sub_address_list:  # 地址在子账户列表中
                                    tx_id = generate_order_no()
                                    btc_tx = TxListBtcModel(
                                        tx_id=tx_id,
                                        tx_no=tx,
                                        vout=v.get("n"),
                                        block_no=block_no,
                                        value=value,
                                        address=address
                                    )
                                    wb = session.query(WalletBtcModel).filter(
                                        WalletBtcModel.sub_public_address == address).first()
                                    wb.amount = wb.amount + value
                                    result2 = WalletCallbackService().recharge_notify_callback(wb.account_id,
                                                                                               value, self.coin_id,
                                                                                               address,
                                                                                               tx_id)  # 充值user接口
                                    btc_tx.do_recharge_result = result2
                                    btc_tx_add_list.append(btc_tx)
                                else:  # 地址不在子账户列表中
                                    if address in gather_address_list:  # 地址在归集账户列表中
                                        tx_id = generate_order_no()
                                        btc_tx = TxListBtcModel(
                                            tx_id=tx_id,
                                            tx_no=tx,
                                            vout=v.get("n"),
                                            block_no=block_no,
                                            value=value,
                                            address=address
                                        )
                                        wbg = session.query(WalletBtcGatherModel).filter(
                                            WalletBtcGatherModel.sub_public_address == address).first()
                                        wbg.amount = wbg.amount + value
                                        btc_tx_add_list.append(btc_tx)
            if btc_tx_add_list:
                session.add_all(btc_tx_add_list)
            btc_block.status = 1
            session.commit()
            self.block_flag = 0
            token = TokenBtcScript()
            token.btc_block_listener(count + 1)

    # 定时循环查询BTC UTXO--1、查询余额监听器
    def btc_block_listener_api(self):
        # 保证同期只有一个此定时器在运行
        if self.block_flag == 1:
            return
        else:
            self.block_flag == 1
        cover = False  # 覆盖标识
        with MysqlTools().session_scope() as session:
            btc_block = session.query(SyncBlockModel).filter(SyncBlockModel.coin_id == _ZERO).first()
            block_no = btc_block.block_no
            status = btc_block.status

            latest_map = do_get("https://chainflyer.bitflyer.jp/v1/block/latest")
            block_count = latest_map.get("height")  # 查询链上最优最近区块号

            token_conf = session.query(TokenConfModel).filter(TokenConfModel.coin_id == _ZERO_S).first()
            confirmations = token_conf.confirm_last_block_num  # 区块确认次数
            block_count = block_count - int(confirmations) + 1
            if block_count > block_no and status == 1:  # 大于本地且本地已执行完毕--从本地区块号+1开始工作
                block_no = block_no + 1
                url = "https://chainflyer.bitflyer.jp/v1/block/height/" + str(block_no)
                latest_map = do_get(url)
            elif block_count > block_no and status == 0:  # 大于本地且本地未执行完毕--从本地区块号开始工作并覆盖
                url = "https://chainflyer.bitflyer.jp/v1/block/height/" + str(block_no)
                latest_map = do_get(url)
                cover = True
            elif block_count == block_no and status == 1:  # 等于本地且本地已执行完毕--return
                self.block_flag = 0
                return
            elif block_count == block_no and status == 0:  # 等于本地且本地未执行完毕--从本地区块号开始工作并覆盖
                url = "https://chainflyer.bitflyer.jp/v1/block/height/" + str(block_no)
                latest_map = do_get(url)
                cover = True
            else:  # 其他情况(小于本地）
                self.block_flag = 0
                return
            block_map = latest_map
            btc_block.block_no = block_map.get("height")
            block_hash = block_map.get("block_hash")
            btc_block.block_hash = block_hash
            btc_block.status = 0
            session.commit()
            if cover:  # 删除之前未执行完毕的tx[不会出现此类情况]
                session.query(TxListBtcModel).filter(TxListBtcModel.block_no == block_no).delete(
                    synchronize_session=False)
                session.commit()
            tx_list = block_map["tx_hashes"]

            # 建立子钱包地址list、归集账户地址list
            wallet_btc = session.query(WalletBtcModel.sub_public_address).filter(WalletBtcModel.account_id != "").all()
            sub_address_list = []
            for w in wallet_btc:
                sub_address_list.append(w.sub_public_address)
            wallet_btc_gather = session.query(WalletBtcGatherModel.sub_public_address).all()
            gather_address_list = []
            for w in wallet_btc_gather:
                gather_address_list.append(w.sub_public_address)
            # 建立tx监听list
            tx_listening_btc = session.query(TxListeningBtcModel).filter(TxListeningBtcModel.listen_flag == _ONE).all()
            tx_listening_list = []
            for t in tx_listening_btc:
                tx_listening_list.append(t.tx_no)

            btc_tx_add_list = []
            for tx in tx_list:
                if tx in tx_listening_list:  # tx在tx监听列表中
                    tl = session.query(TxListeningBtcModel).filter(TxListeningBtcModel.tx_no == tx,
                                                                   TxListeningBtcModel.listen_flag == _ONE).first()
                    tl.listen_flag = _ZERO  # 修改监听状态
                    tl.block_no = block_no
                    multi_flag = tl.multi_flag
                    if multi_flag == _ONE:  # 1对多转账(提现)
                        fmwr = session.query(ForeignMultiWithdrawRecordModel).filter(
                            ForeignMultiWithdrawRecordModel.record_id == tl.record_no).first()
                        fmwr.withdraw_status = _TWO_S
                        fmwr.verified_amount = fmwr.amount
                        fmwr.verified_gas = fmwr.gas
                        fwor_list = session.query(ForeignWithdrawOrderRecordModel).filter(
                            ForeignWithdrawOrderRecordModel.relate_flow_no == fmwr.record_id).all()
                        '''
                            1对多转账(提现):
                            当前方法实现:1、调user接口通知进账,2、修改withdraw表,3、修改归集账户表(from_address)字段:[找零][已支付未确认到账]
                            扫描地址实现:1、给归集账户(from_address)增加余额{找零}utxo{找零}
                        '''
                        for f in fwor_list:
                            result = WalletCallbackService().withdraw_notify_callback(f.req_no,
                                                                                      f.order_no,
                                                                                      AccountChangeRecordModel.change_type_4,
                                                                                      f.withdraw_amount - f.withdraw_fee,
                                                                                      f.withdraw_fee)  # 提现user接口
                            session.query(ForeignWithdrawOrderRecordModel).filter(
                                ForeignWithdrawOrderRecordModel.order_no == f.order_no).update({
                                ForeignWithdrawOrderRecordModel.withdraw_actual_amount: ForeignWithdrawOrderRecordModel.withdraw_amount - ForeignWithdrawOrderRecordModel.withdraw_fee,
                                ForeignWithdrawOrderRecordModel.withdraw_status: _TWO_S,
                                ForeignWithdrawOrderRecordModel.do_withdraw_result: result,
                                ForeignWithdrawOrderRecordModel.confirm_at: get_now_time()
                            })

                        session.query(WalletBtcGatherModel).filter(
                            WalletBtcGatherModel.sub_public_address == fmwr.from_address).update({
                            WalletBtcGatherModel.amount_change: WalletBtcGatherModel.amount_change - fmwr.amount_change,
                            WalletBtcGatherModel.amount_frozen: WalletBtcGatherModel.amount_frozen - fmwr.amount
                        })
                    elif multi_flag == _ZERO:  # 1对1转账(归集、归集转归集)
                        fwor = session.query(ForeignWithdrawOrderRecordModel).filter(
                            ForeignWithdrawOrderRecordModel.order_no == tl.record_no).first()  # 查询withdraw提现记录表数据
                        if fwor is not None:
                            withdraw_actual_amount = fwor.withdraw_amount - fwor.withdraw_fee
                            fwor.withdraw_actual_amount = withdraw_actual_amount  # 修改提现记录实际到账金额
                            fwor.withdraw_status = _TWO_S  # 修改提现记录表状态
                            fwor.confirm_at = get_now_time()  # 更新到账时间

                            if fwor.withdraw_type == _TWO_S:
                                '''
                                    归集:
                                    当前方法实现:1、归集记录表叠加确认金额,2、修改归集账户(from_address)表字段:[找零][已支付未确认到账]{正常情况下不会存在找零}
                                    扫描地址实现:1、给归集账户(to_address)表增加余额{进账}utxo{进账},2、给归集账户(from_address)增加余额{找零}utxo{找零}
                                '''
                                session.query(ForeignGatherRecordModel).filter(
                                    ForeignGatherRecordModel.record_id == fwor.relate_flow_no).update(
                                    {
                                        ForeignGatherRecordModel.actual_amount: ForeignGatherRecordModel.actual_amount + withdraw_actual_amount})  # 归集记录表叠加确认金额
                                # 修改wallet_btc表(from_address)
                                session.query(WalletBtcModel).filter(
                                    WalletBtcModel.sub_public_address == fwor.from_address).update({
                                    WalletBtcModel.amount_change: WalletBtcModel.amount_change - fwor.amount_change,
                                    WalletBtcModel.amount_frozen: WalletBtcModel.amount_frozen - fwor.withdraw_amount
                                })
                            elif fwor.withdraw_type == _THREE_S:
                                '''
                                    归集转归集:
                                    当前方法实现:1、归集记录表叠加确认金额,2、修改归集账户(from_address)表字段:[找零][已支付未确认到账]
                                    扫描地址实现:1、给归集账户(to_address)表增加余额{进账}utxo{进账}2、给归集账户(from_address)增加余额{找零}utxo{找零}
                                '''
                                session.query(ForeignGatherRecordModel).filter(
                                    ForeignGatherRecordModel.record_id == fwor.relate_flow_no).update(
                                    {
                                        ForeignGatherRecordModel.actual_amount: ForeignGatherRecordModel.actual_amount + withdraw_actual_amount})  # 归集记录表叠加确认金额
                                # 修改wallet_btc_gather表(from_address)
                                session.query(WalletBtcGatherModel).filter(
                                    WalletBtcGatherModel.sub_public_address == fwor.from_address).update({
                                    WalletBtcGatherModel.amount_change: WalletBtcGatherModel.amount_change - fwor.amount_change,
                                    WalletBtcGatherModel.amount_frozen: WalletBtcGatherModel.amount_frozen - fwor.withdraw_amount
                                })
                tx_url = "https://chainflyer.bitflyer.jp/v1/tx/" + tx
                transaction_map = do_get(tx_url)
                vout = transaction_map.get("outputs")
                for v in vout:
                    value = get_decimal(v.get("value"), 18)
                    if value == 0:
                        continue
                    else:
                        address = v.get("address")
                        if address is None:
                            continue
                        if address in sub_address_list:  # 地址在子账户列表中
                            tx_id = generate_order_no()
                            btc_tx = TxListBtcModel(
                                tx_id=tx_id,
                                tx_no=tx,
                                vout=v.get("n"),
                                block_no=block_no,
                                value=value,
                                address=address
                            )
                            wb = session.query(WalletBtcModel).filter(
                                WalletBtcModel.sub_public_address == address).first()
                            wb.amount = wb.amount + value
                            result2 = WalletCallbackService().recharge_notify_callback(wb.account_id,
                                                                                       value, self.coin_id,
                                                                                       address,
                                                                                       tx_id)  # 充值user接口
                            btc_tx.do_recharge_result = result2
                            btc_tx_add_list.append(btc_tx)
                        else:  # 地址不在子账户列表中
                            if address in gather_address_list:  # 地址在归集账户列表中
                                tx_id = generate_order_no()
                                btc_tx = TxListBtcModel(
                                    tx_id=tx_id,
                                    tx_no=tx,
                                    vout=v.get("n"),
                                    block_no=block_no,
                                    value=value,
                                    address=address
                                )
                                wbg = session.query(WalletBtcGatherModel).filter(
                                    WalletBtcGatherModel.sub_public_address == address).first()
                                wbg.amount = wbg.amount + value
                                btc_tx_add_list.append(btc_tx)
            if btc_tx_add_list:
                session.add_all(btc_tx_add_list)
            btc_block.status = 1
            session.commit()
            self.block_flag = 0
            token = TokenBtcScript()
            token.btc_block_listener()


if __name__ == "__main__":
    tes = TokenBtcScript()
    tes.btc_block_listener()
