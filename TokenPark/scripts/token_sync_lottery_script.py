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
from models.sync_eos_model import SyncEosModel
from models.game_get_lottery_block_info_eos_model import GameGetLotteryBlockInfoEosModel
from services.wallet_eos_service import WalletEosService
from utils.time_util import str_to_timestamp
from utils.util import get_decimal
from common_settings import *
from utils.log import Slog


# 第一个事,获取当前最新区块号,同步所有区块,一分钟一次

class TokenSyncLotteryScript(object):
    ec = None
    sync_success = _ONE
    sync_fail = _ZERO
    eos_coin_id = _COIN_ID_EOS
    slog = Slog("token_sync_lottery_script")
    mysql_tool = MysqlTools()
    wait_lottery_dict = {}

    def __init__(self):
        pass

    def work(self):
        # 逻辑: 查找GameGetLotteryBlockInfoEosModel看看是否有未开奖 规则 满额时间点的第60个区块(包含当前时间点的块)
        # 找到未开奖列表,查找时间戳 对应的基础区块号,因为是最新时间,基本上数据库都会没有找到该区块
        # 根据基础区块号,生成 开奖区块 确认区块
        # 如果没有找到对应的基础区块号,根据找到的区块号,往回查询EOSPark(睡1秒),直到找到符合时间戳的区块,规则是 一直大,直到找到小的,小的区块号下一个就是是基础区块
        # 更新 sync_eos表 基础区块
        # 找到已经同步的确认区块,返回去查开奖区块,查询EOSPark,更新开奖区块
        # 更新 sync_eos表 开奖区块
        # 更新 GameGetLotteryBlockInfoEosModel 开奖区块hash 状态完成
        # 调韩梦 通知开奖
        with self.mysql_tool.session_scope() as session:
            lottery_block_info_eos_model_list = session.query(GameGetLotteryBlockInfoEosModel).filter(GameGetLotteryBlockInfoEosModel.status != self.sync_success).all()
            if not lottery_block_info_eos_model_list:
                return True
            for lottery_block_info_eos_model in lottery_block_info_eos_model_list:
                if lottery_block_info_eos_model.base_block_num < _ZERO:
                    base_time_stamp = lottery_block_info_eos_model.base_time_stamp
                    sync_eos_model = session.query(SyncEosModel).filter(SyncEosModel.time_stamp_decimal >= base_time_stamp).order_by(SyncEosModel.block_num.asc()).first()
                    if sync_eos_model:  # 找到基础块
                        base_block_num = sync_eos_model.block_num  # 基础块
                        if sync_eos_model.time_stamp_decimal - base_time_stamp < 0.5:
                            lottery_block = base_block_num + lottery_block_info_eos_model.block_num  # 开奖块
                            confirm_block = lottery_block + lottery_block_info_eos_model.confirm_block_num  # 确认块
                            # 更新开奖块 确认块数据
                            lottery_block_info_eos_model.base_block_num = base_block_num
                            lottery_block_info_eos_model.block_num = lottery_block
                            lottery_block_info_eos_model.confirm_block_num = confirm_block
                        else:  # 基础块时间>0.5 找到的不对
                            right_block_detail = self.find_right_block(base_block_num, base_time_stamp)
                            right_sync_eos_model = session.query(SyncEosModel).filter(SyncEosModel.block_num == right_block_detail["block_num"]).first()
                            if right_sync_eos_model:
                                right_sync_eos_model.block_hash = right_block_detail["id"]
                                right_sync_eos_model.time_stamp = right_block_detail["timestamp"]
                                right_sync_eos_model.time_stamp_decimal = right_block_detail["time_stamp_decimal"]
                                right_sync_eos_model.previous = right_block_detail["previous"]
                                right_sync_eos_model.status = self.sync_success
                            else:
                                sync_eos_model = SyncEosModel(
                                    block_num=right_block_detail["block_num"],
                                    block_hash=right_block_detail["id"],
                                    time_stamp=right_block_detail["timestamp"],
                                    time_stamp_decimal=right_block_detail["time_stamp_decimal"],
                                    previous=right_block_detail["previous"],
                                    status=self.sync_success
                                )
                                session.add(sync_eos_model)
                    else:  # 没有找到基础块数据,
                        # 等待脚本下次执行
                        pass
                else:
                    # 有基础块数据 找确认块数据
                    confirm_block_num = lottery_block_info_eos_model.confirm_block_num
                    lottery_block_num = lottery_block_info_eos_model.block_num
                    confirm_block_model = session.query(SyncEosModel).filter(SyncEosModel.block_num == confirm_block_num).first()
                    lottery_block_model = session.query(SyncEosModel).filter(SyncEosModel.block_num == lottery_block_num).first()
                    game_instance_id = lottery_block_info_eos_model.game_instance_id
                    notice_flag = None
                    node_block_detail_block_hash = None
                    node_block_detail_time_stamp = None
                    if confirm_block_model:
                        node_block_detail = self.find_right_block(lottery_block_num)
                        node_block_detail_block_hash = node_block_detail["id"]
                        node_block_detail_time_stamp = node_block_detail["timestamp"]
                        if lottery_block_model and lottery_block_model.block_hash and lottery_block_model.time_stamp:
                            lottery_block_hash = lottery_block_model.block_hash
                            lottery_time_stamp = lottery_block_model.time_stamp
                            if lottery_block_hash != node_block_detail_block_hash or lottery_time_stamp != node_block_detail_time_stamp:
                                lottery_block_model.block_hash = node_block_detail_block_hash
                                lottery_block_model.time_stamp = node_block_detail_time_stamp
                                lottery_block_model.time_stamp_decimal = node_block_detail["time_stamp_decimal"]
                                lottery_block_model.previous = node_block_detail["previous"]
                        else:
                            # 没有找到同步区块,但是找到了确认区块 或者 没有找到这个块hash和time_stamp
                            if lottery_block_model:  # 有开奖区块,没有块hash或者time_stamp
                                lottery_block_model.block_hash = node_block_detail_block_hash
                                lottery_block_model.time_stamp = node_block_detail_time_stamp
                                lottery_block_model.time_stamp_decimal = node_block_detail["time_stamp_decimal"]
                                lottery_block_model.previous = node_block_detail["previous"]
                            else:
                                sync_eos_model = SyncEosModel(
                                    block_num=lottery_block_num,
                                    block_hash=node_block_detail_block_hash,
                                    time_stamp=node_block_detail_time_stamp,
                                    time_stamp_decimal=node_block_detail["time_stamp_decimal"],
                                    previous=node_block_detail["previous"],
                                    status=self.sync_success
                                )
                                session.add(sync_eos_model)
                        notice_flag = True
                    else:
                        lasted_block_detail = self.composing_right_block()
                        lasted_block_num = lasted_block_detail.get("block_num", "")
                        if lasted_block_num and int(lasted_block_num) >= int(confirm_block_num):
                            node_block_detail = self.composing_right_block(lottery_block_num)
                            node_block_detail_block_hash = node_block_detail.get("id", "")
                            node_block_detail_time_stamp = node_block_detail.get("timestamp", "")
                            if lottery_block_model:  # 有开奖区块,没有块hash或者time_stamp
                                lottery_block_model.block_hash = node_block_detail_block_hash
                                lottery_block_model.time_stamp = node_block_detail_time_stamp
                                lottery_block_model.time_stamp_decimal = node_block_detail["time_stamp_decimal"]
                                lottery_block_model.previous = node_block_detail["previous"]
                            else:
                                sync_eos_model = SyncEosModel(
                                    block_num=lottery_block_num,
                                    block_hash=node_block_detail_block_hash,
                                    time_stamp=node_block_detail_time_stamp,
                                    time_stamp_decimal=node_block_detail["time_stamp_decimal"],
                                    previous=node_block_detail["previous"],
                                    status=self.sync_success
                                )
                                session.add(sync_eos_model)
                            notice_flag = True
                        else:
                            # 还没有同步到确认区块 等待脚本下次执行
                            print("1 record is not the lottery, not find confirm_block_num: " + str(int(confirm_block_num)))
                            print("Wait for the next script loop!")
                    if notice_flag:
                        # 通知韩梦
                        process_res = WalletEosService.lottery_callback(game_instance_id, lottery_block_num, node_block_detail_block_hash, node_block_detail_time_stamp, node_block_detail_time_stamp)
                        lottery_block_info_eos_model.block_hash = node_block_detail_block_hash
                        lottery_block_info_eos_model.time_stamp = node_block_detail_time_stamp
                        lottery_block_info_eos_model.status = process_res
                        print("lottery success, notice Mr Han!!!")
                        print("lottery_block_num: " + str(int(lottery_block_num)))
                        print("lottery_block_hash: " + str(node_block_detail_block_hash))
                        print("lottery_time_stamp: " + str(node_block_detail_time_stamp))
                session.commit()

        return True

    def find_right_block(self, block_num, base_time_stamp=None):
        """
        找到对应的区块,时间戳小于0.5的
        :param block_num:
        :param base_time_stamp:
        :return:
        """
        print("find_right_block args:")
        print("block_num: " + str(int(block_num)))
        if base_time_stamp:
            print("base_time_stamp: " + str(base_time_stamp))
        block_detail = self.composing_right_block(block_num)
        if base_time_stamp:
            base_time_stamp = float(base_time_stamp)
            # 假设一个块间隔生成时间需要0.5秒,也就是1秒2块
            tmp_right_time_stamp = block_detail["time_stamp_decimal"]
            tmp_right_block_num = block_num - (tmp_right_time_stamp - base_time_stamp) // _TWO
            for i in range(3600):
                tmp_block_detail = self.composing_right_block(tmp_right_block_num)
                if tmp_block_detail:
                    print("find tmp_right_block_num: " + str(int(tmp_right_block_num)))
                    print("find tmp_right_time_stamp: " + str(tmp_right_time_stamp))
                    tmp_right_time_stamp = tmp_block_detail["time_stamp_decimal"]
                    if tmp_right_time_stamp >= base_time_stamp:
                        if tmp_right_time_stamp - base_time_stamp > 100:
                            tmp_right_block_num -= (tmp_right_time_stamp - base_time_stamp) // _TWO
                            continue
                        else:
                            if tmp_right_time_stamp - base_time_stamp < 0.5:
                                block_detail = tmp_block_detail
                                print("find right_block_num right!!!!!: " + str(int(tmp_right_block_num)))
                                print("find right_time_stamp right!!!!: " + str(tmp_right_time_stamp))
                                break
                            else:
                                tmp_right_block_num -= _ONE
                    else:
                        if base_time_stamp - tmp_right_time_stamp > 100:
                            tmp_right_block_num -= (base_time_stamp - tmp_right_time_stamp) // _TWO
                            continue
                        else:
                            tmp_right_block_num += _ONE

        return block_detail

    def composing_right_block(self, block_num=None):
        """
        查找并组装正确区块
        :param block_num:
        :return:
        """
        block_detail = {}
        # 如果一个小时都没有找到合适的块,就算了,肯定是其他问题
        for i in range(3600):
            block_detail = self.get_node_block_detail_from_block_num(block_num, ["block_num", "timestamp", "id", "previous"])
            if block_detail:
                right_time_stamp_str = block_detail.get("timestamp")
                right_time_stamp = str_to_timestamp(right_time_stamp_str)
                if right_time_stamp:
                    block_detail["time_stamp_decimal"] = right_time_stamp
                    break
                else:
                    time.sleep(0.5)
        return block_detail

    def get_node_block_detail_from_block_num(self, block_num=None, target_parameter_list=None):
        """
        根据区块号,获取节点详情
        :param block_num:
        :param target_parameter_list:
        :return:
        """
        print("get_node_block_detail_from_block_num")
        print("server local time: " + str(time.time()))
        if self.ec is None:
            self.ec = TokenNodeConfModel.get_eos_node_script(script_unit=_ONE_S)
        if block_num:
            print("block_num: " + str(block_num))
            block_num = int(block_num)
            block_detail = self.ec.http_get_block_detail(block_num)
        else:
            block_detail = self.ec.http_get_latest_block()

        ret_dict = {}
        if block_detail:
            print("timestamp: " + block_detail.get("timestamp", ""))
            if not target_parameter_list:
                return block_detail
            else:
                for i in target_parameter_list:
                    ret_dict[i] = block_detail.get(i, "")
                return ret_dict
        return ret_dict

    def process_game_list(self):
        f_filters = {
            "block_hash": "",
            "status": _ZERO
        }

        with self.mysql_tool.session_scope() as session:
            base_block_num_not_have_model_list = session.query(GameGetLotteryBlockInfoEosModel).filter(GameGetLotteryBlockInfoEosModel.base_block_num < _ZERO).all()
            if base_block_num_not_have_model_list:
                for base_block_num_not_have_model in base_block_num_not_have_model_list:
                    base_time_stamp = base_block_num_not_have_model.base_time_stamp
                    lottery_block_add = base_block_num_not_have_model.block_num
                    confirm_block_add = base_block_num_not_have_model.confirm_block_num
                    base_block = session.query(SyncEosModel).filter(SyncEosModel.time_stamp_decimal >= base_time_stamp).order_by(SyncEosModel.block_num.asc()).first()
                    if base_block and base_block.time_stamp_decimal - base_time_stamp <= _SIXTY:
                        base_block_num = base_block.block_num
                        base_block_num_not_have_model.base_block_num = base_block_num
                        base_block_num_not_have_model.block_num = base_block_num + lottery_block_add
                        base_block_num_not_have_model.confirm_block_num = base_block_num + lottery_block_add + confirm_block_add
                        session.commit()

            wait_lottery_model_list = session.query(GameGetLotteryBlockInfoEosModel).filter_by(**f_filters).filter(GameGetLotteryBlockInfoEosModel.base_block_num > _ZERO).all()
            if wait_lottery_model_list:
                wait_lottery_dict = {}
                wait_lottery_list = []
                for lottery_info_model in wait_lottery_model_list:
                    wait_lottery_dict[str(lottery_info_model.confirm_block_num)] = {
                        "game_instance_id": lottery_info_model.game_instance_id, "block_num": lottery_info_model.block_num}
                    wait_lottery_list.append(lottery_info_model.confirm_block_num)

                sync_eos_model_list = session.query(SyncEosModel).filter(
                    SyncEosModel.block_num.in_(wait_lottery_list), SyncEosModel.status == self.sync_success).all()

                if sync_eos_model_list:
                    for sync_eos_model in sync_eos_model_list:
                        confirm_block_num = sync_eos_model.block_num
                        game_instance_id = wait_lottery_dict[str(confirm_block_num)]["game_instance_id"]
                        block_no = wait_lottery_dict[str(confirm_block_num)]["block_num"]
                        lottery_eos_model = session.query(SyncEosModel).filter(SyncEosModel.block_num == block_no).first()
                        if lottery_eos_model:
                            block_hash = lottery_eos_model.block_hash
                            sync_eos = self.update_sync_eos(session, block_no, block_hash)
                            if sync_eos:
                                block_hash = sync_eos["block_hash"]
                                received_time = timestamp = sync_eos["time_stamp"]
                                TokenSyncLotteryScript.lottery_callback(session, game_instance_id, block_no, block_hash, timestamp, received_time)
                                if str(confirm_block_num) in wait_lottery_dict:
                                    del wait_lottery_dict[str(confirm_block_num)]
                                session.commit()
                self.wait_lottery_dict = wait_lottery_dict
        return True

    def update_sync_eos(self, session, block_num, block_hash):
        """
        开奖时,如果再次查询节点上的该区块,如果hash有变化,说明回滚,取最新区块详情,修改该区块
        :param session:
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
                    sync_eos_model = session.query(SyncEosModel).filter(SyncEosModel.block_num == block_num).first()
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


if __name__ == "__main__":
    sbe = TokenSyncLotteryScript()
    res = sbe.work()
    if res:
        sbe.slog.info("eos sync block success!")
    else:
        sbe.slog.info("eos sync block fail!")
