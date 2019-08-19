from services.base_service import BaseService
from services.game_model_service import GamePublishLotteryServie
from utils.log import raise_logger
from models.game_get_lottery_block_info_eos_model import GameGetLotteryBlockInfoEosModel
from models.token_node_conf_model import TokenNodeConfModel
from tools.mysql_tool import MysqlTools
from common_settings import *
from utils.time_util import str_to_timestamp
import time


class WalletEosService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def dice_adduce(self):
        """
        石头剪刀布 外部引用
        :return:
        """
        pass

    def dice_callback(self):
        """
        石头剪刀布 内部回调
        :return:
        """
        pass

    @classmethod
    def lottery_adduce(cls, game_instance_id, base_time_stamp, lottery_block_add=60, confirm_block_add=200):
        """
        一元夺宝 外部引用
        :param game_instance_id: 游戏实例id 必传
        :param base_time_stamp: 传时间戳 float或decimal类型 必须保留小数点后3位 必传
        :param lottery_block_add: 根据时间戳找到基础参照区块,加上该参数,即开奖区块号
        :param confirm_block_add: 根据开奖区块号,加上该参数,就是确认区块号,脚本找到该区块,即公布开奖,脚本回调 lottery_callback
        :return:
        """
        lottery_block_add -= _ONE  # 根据基础块找,所以需要减1
        game_instance_id = int(game_instance_id)
        try:
            with MysqlTools().session_scope() as session:
                lottery_block_info = session.query(GameGetLotteryBlockInfoEosModel).filter(GameGetLotteryBlockInfoEosModel.game_instance_id == game_instance_id).first()
                if lottery_block_info:
                    base_block_num = lottery_block_info.base_block_num
                    lottery_block = lottery_block_info.block_num
                    confirm_block = lottery_block_info.confirm_block_num
                else:
                    base_block_num = game_instance_id * -1
                    lottery_block = lottery_block_add
                    confirm_block = confirm_block_add

                    lottery_block_info = GameGetLotteryBlockInfoEosModel(
                        game_instance_id=game_instance_id,
                        base_block_num=base_block_num,
                        base_time_stamp=base_time_stamp,
                        block_num=lottery_block,
                        confirm_block_num=confirm_block
                    )
                    session.add(lottery_block_info)
                    session.commit()
                return {
                    "game_instance_id": game_instance_id,
                    "base_block_num": base_block_num,
                    "block_num": lottery_block,
                    "confirm_block": confirm_block
                }

        except Exception as e:
            raise_logger("lottery_adduce" + str(e), "wallet", "error")
        return False

    @classmethod
    def lottery_callback(cls, game_instance_id, block_no, block_hash, timestamp, received_time):
        """
        一元夺宝 内部回调
        :return:
        :param game_instance_id: 项目id int类型
        :param block_no: 区块号 int类型
        :param block_hash: 区块hash
        :param timestamp: 区块生成时间
        :param received_time: 区块hash值不可逆时间
        """
        # timestamp = str(timestamp).replace("T"," ")[:-4]
        # received_time = str(received_time).replace("T"," ")[:-4]
        try:
            res = GamePublishLotteryServie().check_game_sold_out_by_eos(game_instance_id, block_no, block_hash, timestamp, received_time)
            if res is True:
                return _ONE
        except Exception as e:
            raise_logger("lottery_callback" + str(e), "wallet", "error")
        return _ZERO

    @classmethod
    def lottery_instant_adduce(cls, base_time_stamp, user_lottery_num_list, imaginary_num, faker=True, times=6):
        """
        一元夺宝 即时版
        :param base_time_stamp: 收到的请求时间 float类型 时间戳
        :param user_lottery_num_list: 判断用户是否中奖的号码段 例: [12, 45]
        :param imaginary_num: hash16进制之后取摩用的总虚数,当前btc价格加上溢价
        :param faker: 你猜这个是干嘛的:) 传True就特殊处理,反之不处理
        :param times: 查询区块的次数,默认6次
        :return:
        """
        ec = TokenNodeConfModel.get_eos_node_script(script_unit=_ZERO_S)
        node_data = ec.http_get_latest_block()
        latest_block = node_data.get("latest_block", {})
        block_num = None
        begin, end = user_lottery_num_list
        counter = _ONE
        for i in range(_HUNDRED):
            if latest_block:
                if counter > int(times):
                    break
                counter += _ONE
                block_num = latest_block["block_num"]
                block_hash = latest_block["id"]
                timestamp = latest_block["timestamp"]
                block_timestamp = str_to_timestamp(timestamp)
                if block_timestamp >= base_time_stamp:
                    lottery_num = int(block_hash, 16) % imaginary_num + _ONE
                    if (end < lottery_num or lottery_num < begin) or not faker:
                        return {
                            "block_num": block_num,
                            "block_hash": block_hash,
                            "timestamp": timestamp,
                            "lottery_num": lottery_num,
                        }
            if block_num:
                block_num += _ONE
                latest_block = ec.http_get_block_detail(block_num)
                if not latest_block:
                    block_num -= _ONE
            else:
                latest_block = ec.http_get_latest_block()

            time.sleep(0.5)

        return {}


if __name__ == "__main__":
    # WalletEosService.lottery_adduce(199, 11547514735.123)
    # base_time_stamp = 12345.123
    # user_lottery_num = 123
    # imaginary_num = 4400
    # res = WalletEosService.lottery_instant_adduce(base_time_stamp, user_lottery_num, imaginary_num, faker=True)
    # print(res)
    pass
