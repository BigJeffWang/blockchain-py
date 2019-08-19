import sys
from pathlib import Path

pro_name = "TokenPark"
current_path = str(Path(__file__).resolve())
import_index = current_path.rfind(pro_name)
import_path = current_path[:import_index + len(pro_name)]
path_flag = True if not import_path in sys.path else False
if path_flag:
    sys.path.append(import_path)

from tools.mysql_tool import MysqlTools
from models.sync_eos_model import SyncEosModel
from config import get_mysql_conf
from common_settings import *
# from utils.log import Slog


# 第一个事,获取当前最新区块号,同步所有区块,一分钟一次

class TokenSyncBlockEosFromDbScript(object):
    mysql_tool = None
    mysql_dev_tool = None
    # slog = Slog("token_sync_block_eos_from_db_script")

    def __init__(self):
        self.mysql_tool = MysqlTools()
        mysql_dev_conf = get_mysql_conf(env="dev")
        # mysql_dev_conf["host"] = "luckypark0121.cnzvcx1qv3xd.us-east-2.rds.amazonaws.com"
        self.mysql_dev_tool = MysqlTools(mysql_dev_conf)

    def work(self, last_block_num=None):

        with self.mysql_dev_tool.session_scope() as dev_session:
            if not last_block_num:
                last_block_num_tuple = dev_session.query(SyncEosModel.block_num).order_by(SyncEosModel.block_num.desc()).first()
                if last_block_num_tuple:
                    last_block_num = last_block_num_tuple[_ZERO]
                else:
                    last_block_num = _ZERO
            with self.mysql_tool.session_scope() as session:
                tmp_block_detail_list = session.query(SyncEosModel).filter(SyncEosModel.block_num > last_block_num).all()
                if not tmp_block_detail_list:
                    return True
                dev_tmp_block_detail_list = []
                for tmp_block_detail in tmp_block_detail_list:
                    block_num = tmp_block_detail.block_num
                    block_hash = tmp_block_detail.block_hash
                    time_stamp = tmp_block_detail.time_stamp
                    time_stamp_decimal = tmp_block_detail.time_stamp_decimal
                    previous = tmp_block_detail.previous
                    status = tmp_block_detail.status
                    print("syncing block_num: " + str(block_num), "time_stamp: " + time_stamp)
                    dev_tmp_block_detail = SyncEosModel(
                        block_num=block_num,
                        block_hash=block_hash,
                        time_stamp=time_stamp,
                        time_stamp_decimal=time_stamp_decimal,
                        previous=previous,
                        status=status,
                    )
                    if len(dev_tmp_block_detail_list) <= _SIXTY:
                        dev_tmp_block_detail_list.append(dev_tmp_block_detail)
                    else:
                        dev_session.add_all(dev_tmp_block_detail_list)
                        dev_session.commit()
                        dev_tmp_block_detail_list = []

        return True


if __name__ == "__main__":
    sbe = TokenSyncBlockEosFromDbScript()
    res = sbe.work()
    if res:
        print("eos sync block success!")
    else:
        print("eos sync block fail!")
