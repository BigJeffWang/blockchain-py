from utils.util import btc_rpc_client
from models.token_node_conf_model import TokenNodeConfModel
import time


class BlockHashService():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rpc = TokenNodeConfModel.get_btc_node_server()
        self.block_no = 0
        self.confirm_num = 2
        self.block_map = None

    def get_time(self, time_stamp):
        timeArray = time.localtime(time_stamp)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return otherStyleTime

    def get_block_no(self):
        """
        获取当前最高区块号
        :return:int(block_no)
        """
        return self.rpc.getblockcount()

    def get_block_no_eos(self):
        """
        获取当前最高区块号 eos
        :return:int(block_no)
        """
        return int(self.rpc.http_get_latest_block().get("block_num"))

    def get_match_block_no(self, utc):  # 1
        """
        获取最匹配区块号
        :return:int(block_no)
        """
        block_no = self.get_block_no()
        block_no_hash = self.rpc.getblockhash(block_no)
        block_no_map = self.rpc.getblock(block_no_hash)
        time = block_no_map.get("time")
        if utc >= time:
            return block_no + 1
        else:
            return block_no

    # def get_block_hash(self, block_no):  # 2
    #     block_no = int(block_no)
    #     while True:
    #         block_no_best = self.get_block_no()  # 当前最高区块号
    #         block_no2 = block_no_best - (self.confirm_num - 1)  # 开奖时最高区块号
    #         if block_no2 == block_no or block_no2 > block_no:
    #             block_hash = self.rpc.getblockhash(block_no)
    #             block_map = self.rpc.getblock(block_hash)
    #             return {"block_no": block_no, "block_hash": block_hash,
    #                     "timestamp": self.get_time(block_map.get("time")),
    #                     "received_time": self.get_time(block_map.get("mediantime"))}
    #         time.sleep(10)

    def get_hash_by_no(self, block_no):  # 2
        block_no = int(block_no)
        block_no_best = self.get_block_no()  # 当前最高区块号
        if block_no_best >= (block_no + self.confirm_num):
            block_hash = self.rpc.getblockhash(block_no)
            block_map = self.rpc.getblock(block_hash)
            return {"block_no": block_no, "block_hash": block_hash,
                    "timestamp": self.get_time(block_map.get("time")),
                    "received_time": self.get_time(block_map.get("mediantime"))}
        else:
            return False


if __name__ == "__main__":
    b = BlockHashService()
    utc = int(time.time())  # UTC时间戳

    vvv = b.get_match_block_no(utc)
    print("vvv:", vvv)

    # a = b.get_hash_by_no(1448332)
    # print(a)

    # mmm = b.get_block_hash(vvv)
    # print("mmm:", mmm)
