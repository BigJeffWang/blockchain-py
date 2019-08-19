import sys
import time
import threading
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
from models.sync_eos_model import SyncEosModel
from models.game_get_lottery_block_info_eos_model import GameGetLotteryBlockInfoEosModel
from services.wallet_eos_service import WalletEosService
from utils.time_util import str_to_timestamp
from utils.util import get_decimal
from config import get_mysql_eos_conf
from common_settings import *
from utils.log import Slog


# 第一个事,获取当前最新区块号,同步所有区块,一分钟一次

class TokenSyncBlockEosScript(object):
    ec = None
    sync_success = _ONE
    sync_fail = _ZERO
    eos_coin_id = _COIN_ID_EOS
    slog = Slog("token_sync_block_eos_script")
    mysql_tool = MysqlTools()
    mysql_eos_tool = MysqlTools(get_mysql_eos_conf())
    wait_lottery_dict = {}

    def __init__(self):
        self.ec = TokenNodeConfModel.get_eos_node_script(script_unit=_ZERO_S)  # 获取eos connect连接
        # pass

    def get_local_block_num(self):
        """
        获取本地区块的高度
        :return:
        """
        with self.mysql_tool.session_scope() as session:
            f_filter = {
                "status": self.sync_success,
                "coin_id": self.eos_coin_id
            }
            local_block = session.query(SyncBlockModel).filter_by(**f_filter).first()
        if not local_block:
            raise Exception("Mysql database SyncBlockModel lacks configuration data")
        local_block_num = local_block.block_no

        return local_block_num

    def get_remote_block_num(self):
        """
        获取远端节点的最新区块高度
        :return:
        """
        remote_block = self.ec.http_get_latest_block()
        remote_block_num = remote_block.get("block_num", "")
        if not remote_block_num:
            raise Exception("Remote eos node has error")
        return remote_block_num

    def async_block_multi(self, begin=None, end=None, sync_block_num_list=None):
        block_data_dict = {}
        thread_list = []
        if not sync_block_num_list:
            for j in range(begin, end):
                t = threading.Thread(target=self._get_block_detail, args=(block_data_dict, j))
                t.setDaemon(True)
                thread_list.append(t)
            for t in thread_list:
                t.start()
            for t in thread_list:
                t.join()
        else:
            for j in sync_block_num_list:
                t = threading.Thread(target=self._get_block_detail, args=(block_data_dict, j))
                t.setDaemon(True)
                thread_list.append(t)
            for t in thread_list:
                t.start()
            for t in thread_list:
                t.join()

        return block_data_dict

    def _get_block_detail(self, block_data_dict, temp_remote_block_num):
        temp_insert_block_data = self.ec.http_get_block_detail(temp_remote_block_num)
        block_data_dict[str(temp_remote_block_num)] = temp_insert_block_data

    def sync_block(self, local_block_num, remote_block_num, interval=8):
        """
        同步区块,默认每8个块创建一个session scope,防止长连接
        同步到SyncEosModel
        同步到SyncBlockModel
        :param local_block_num: 本地block num
        :param remote_block_num: 远程block num
        :param interval: 创建MySQL链接的块数间隔
        :return:
        """
        for i in range(local_block_num + 1, remote_block_num, interval):
            temp_remote_block_num = i + interval
            if temp_remote_block_num > remote_block_num:
                temp_remote_block_num = remote_block_num
            sync_eos_model_list = []
            temp_last_sync_block_no = None
            temp_last_sync_block_hash = ""
            # 调用协程读取
            block_data_dict = self.async_block_multi(i, temp_remote_block_num)
            btime = time.time()
            with self.mysql_eos_tool.session_scope() as session_eos:
                with self.mysql_tool.session_scope() as session_select:
                    for block_no_item in range(i, temp_remote_block_num):
                        temp_last_sync_block_no = block_no_item
                        temp_insert_block_data = block_data_dict.get(str(block_no_item), {})
                        if not temp_insert_block_data:
                            time_stamp_decimal = get_decimal(block_no_item, digits=3) * -1
                            temp_last_sync_block_hash = ""
                            eos_model = SyncEosModel(
                                block_num=int(block_no_item),
                                time_stamp_decimal=time_stamp_decimal,
                                status=self.sync_fail
                            )
                            sync_eos_model_list.append(eos_model)
                        else:
                            time_stamp = temp_insert_block_data.get("timestamp", "")
                            time_stamp_decimal = get_decimal(str_to_timestamp(time_stamp), digits=3)
                            temp_last_sync_block_hash = temp_insert_block_data.get("id")
                            eos_model = SyncEosModel(
                                block_num=temp_insert_block_data.get("block_num"),
                                block_hash=temp_last_sync_block_hash,
                                time_stamp=time_stamp,
                                time_stamp_decimal=time_stamp_decimal,
                                previous=temp_insert_block_data.get("previous"),
                                status=self.sync_success
                            )
                            sync_eos_model_list.append(eos_model)
                        self.slog.info("sync block_num:", temp_last_sync_block_no, "sync block_hash:", temp_last_sync_block_hash)
                if sync_eos_model_list:
                    session_eos.add_all(sync_eos_model_list)
                    try:
                        session_select.query(SyncBlockModel).filter(SyncBlockModel.coin_id == self.eos_coin_id).update({
                            SyncBlockModel.block_no: temp_last_sync_block_no,
                            SyncBlockModel.block_hash: temp_last_sync_block_hash})
                        session_select.commit()
                        session_eos.commit()
                    except Exception as e:
                        self.slog.error(str(e))
                    print("insert time " + str(time.time() - btime))
        return True

    def process_game_list(self):
        f_filters = {
            "block_hash": "",
            "status": _ZERO
        }
        with self.mysql_eos_tool.session_scope() as session_eos:

            with self.mysql_tool.session_scope() as session:
                base_block_num_not_have_model_list = session.query(GameGetLotteryBlockInfoEosModel).filter(GameGetLotteryBlockInfoEosModel.base_block_num < _ZERO).all()
                if base_block_num_not_have_model_list:
                    for base_block_num_not_have_model in base_block_num_not_have_model_list:
                        base_time_stamp = base_block_num_not_have_model.base_time_stamp
                        lottery_block_add = base_block_num_not_have_model.block_num
                        confirm_block_add = base_block_num_not_have_model.confirm_block_num
                        base_block = session_eos.query(SyncEosModel).filter(SyncEosModel.time_stamp_decimal >= base_time_stamp).order_by(SyncEosModel.block_num.asc()).first()
                        if base_block and base_block.time_stamp_decimal - base_time_stamp <= _SIXTY:
                            base_block_num = base_block.block_num
                            base_block_num_not_have_model.base_block_num = base_block_num
                            base_block_num_not_have_model.block_num = base_block_num + lottery_block_add
                            base_block_num_not_have_model.confirm_block_num = base_block_num + lottery_block_add + confirm_block_add
                            session.commit()
                            session_eos.commit()

                wait_lottery_model_list = session.query(GameGetLotteryBlockInfoEosModel).filter_by(**f_filters).filter(GameGetLotteryBlockInfoEosModel.base_block_num > _ZERO).all()
                if wait_lottery_model_list:
                    wait_lottery_dict = {}
                    wait_lottery_list = []
                    for lottery_info_model in wait_lottery_model_list:
                        wait_lottery_dict[str(lottery_info_model.confirm_block_num)] = {
                            "game_instance_id": lottery_info_model.game_instance_id, "block_num": lottery_info_model.block_num}
                        wait_lottery_list.append(lottery_info_model.confirm_block_num)

                    sync_eos_model_list = session_eos.query(SyncEosModel).filter(
                        SyncEosModel.block_num.in_(wait_lottery_list), SyncEosModel.status == self.sync_success).all()

                    if sync_eos_model_list:
                        for sync_eos_model in sync_eos_model_list:
                            confirm_block_num = sync_eos_model.block_num
                            game_instance_id = wait_lottery_dict[str(confirm_block_num)]["game_instance_id"]
                            block_no = wait_lottery_dict[str(confirm_block_num)]["block_num"]
                            lottery_eos_model = session_eos.query(SyncEosModel).filter(SyncEosModel.block_num == block_no).first()
                            if lottery_eos_model:
                                block_hash = lottery_eos_model.block_hash
                                sync_eos = self.update_sync_eos(session_eos, block_no, block_hash)
                                if sync_eos:
                                    block_hash = sync_eos["block_hash"]
                                    received_time = timestamp = sync_eos["time_stamp"]
                                    TokenSyncBlockEosScript.lottery_callback(session, game_instance_id, block_no, block_hash, timestamp, received_time)
                                    if str(confirm_block_num) in wait_lottery_dict:
                                        del wait_lottery_dict[str(confirm_block_num)]
                                    session.commit()
                                    session_eos.commit()
                    self.wait_lottery_dict = wait_lottery_dict
        return True

    def update_sync_eos(self, session_eos, block_num, block_hash):
        """
        开奖时,如果再次查询节点上的该区块,如果hash有变化,说明回滚,取最新区块详情,修改该区块
        :param session_eos:
        :param block_num:
        :param block_hash:
        :return:
        """
        block_detail = self.ec.http_get_block_detail(block_num)
        if block_detail:
            remote_block_hash = block_detail.get("id", "")
            time_stamp = block_detail.get("timestamp", "")
            if remote_block_hash:
                if remote_block_hash != block_hash:
                    sync_eos_model = session_eos.query(SyncEosModel).filter(SyncEosModel.block_num == block_num).first()
                    if sync_eos_model:
                        time_stamp_decimal = get_decimal(str_to_timestamp(time_stamp), digits=3)
                        previous = block_detail.get("previous", "")
                        sync_eos_model.block_hash = remote_block_hash
                        sync_eos_model.time_stamp = time_stamp
                        sync_eos_model.time_stamp_decimal = time_stamp_decimal
                        sync_eos_model.previous = previous
                        sync_eos_model.status = self.sync_success
                        self.slog.info("lottery block_num:", block_num, "lottery block_hash:", remote_block_hash)

                return {
                    "block_hash": remote_block_hash,
                    "time_stamp": time_stamp,
                }
        return {}

    @staticmethod
    def lottery_callback(session, game_instance_id, block_no, block_hash, timestamp, received_time):
        """

        :param session:
        :param game_instance_id:
        :param block_no:
        :param block_hash:
        :param timestamp:
        :param received_time:
        :return:
        """
        process_res = WalletEosService.lottery_callback(game_instance_id, block_no, block_hash, timestamp, received_time)
        session.query(GameGetLotteryBlockInfoEosModel).filter(
            GameGetLotteryBlockInfoEosModel.game_instance_id == game_instance_id).update({
            GameGetLotteryBlockInfoEosModel.block_hash: block_hash,
            GameGetLotteryBlockInfoEosModel.time_stamp: timestamp,
            GameGetLotteryBlockInfoEosModel.status: process_res
        })
        return True

    def work(self):
        # 1.查询已经同步的区块高度
        local_block_num = self.get_local_block_num()
        # 2.查询当前节点的区块最新高度
        remote_block_num = self.get_remote_block_num()
        # local_block_num, remote_block_num = 37657192, 37657202
        # 3.遍历区块号,8个块创建一个session scope
        sync_res = self.sync_block(local_block_num, remote_block_num)
        return sync_res


if __name__ == "__main__":
    sbe = TokenSyncBlockEosScript()
    res = sbe.work()
    if res:
        sbe.slog.info("eos sync block success!")
    else:
        sbe.slog.info("eos sync block fail!")
