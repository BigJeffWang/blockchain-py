import os
import json
import logging
import logging.config
from utils import error_code_utils
import datetime
import sys
import config
from mq.producer_mq import produce_object
from tools.tool import super_json_dumps, detect_file


def show_sqlalchemy_log():
    logging.basicConfig()
    # By default, the log level is set to logging.WARN.
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class ContextFilter(logging.Filter):
    def filter(self, record):
        return True


def setup_logging(path='logging.json', default_level=logging.INFO):
    detect_result = detect_file(path)
    json_path = detect_result["file"]

    if os.path.exists(json_path):

        real_path = ''
        base_config = config.get_config()
        base_conf = base_config["bases"]
        env = base_config["env"]

        if base_conf.get('log_path') and os.path.exists('/data'):
            real_path = base_conf['log_path'] + '/' + base_conf["server"]["name"] + '/' + env
            if not os.path.exists(real_path):
                try:
                    os.makedirs(real_path)
                except:
                    real_path = ''
        if not real_path:
            real_path = detect_result['server_path'] + '/logs'

        with open(json_path, 'rt', encoding="utf-8") as f:
            log_config = json.load(f)
            for k, v in log_config.items():
                if k != 'handlers':
                    continue
                for k1, v1 in v.items():
                    if 'filename' in v1:
                        v1['filename'] = os.path.join(real_path, v1['filename'])
        logging.config.dictConfig(log_config)
    else:
        logging.basicConfig(level=default_level)


setup_logging()

logger = logging.getLogger('rs')
wallet_logger = logging.getLogger('wallet')

log_server_name = config.get_bases_conf()["server"]["name"]
log_server_env = config.get_env()
whether_on_server = config.get_whether_on_server()


def raise_logger(msg, log_name='rs', lv="info", file=None):
    """

    :param msg: 日志的写入内容，若为int，则表示为报错编码；为str则是报错信息
    :param log_name: 要写入的日志文件 rs game_bet_in game_product block wallet script
    :param lv: 级别 info error
    :param file: 报错文件行数
    :return:
    """
    try:
        if not isinstance(msg, str):
            record = super_json_dumps(msg)
        else:
            record = msg
    except Exception as e:
        record = str(e)
    f_back = sys._getframe().f_back
    if not file:
        file_path = str(f_back.f_code.co_filename)
        if file_path[0] == "/":
            file_path = file_path[file_path.rindex(log_server_name) + len(log_server_name):]
        line_no = str(f_back.f_lineno)
        func_name = str(f_back.f_code.co_name)
        file = " file:" + file_path + " line:" + line_no + " func:" + func_name
    record = super_json_dumps({
        "file": file,
        "msg": record
    })

    logger_switch = {
        "rs": logger,
        "wallet": wallet_logger,
    }
    tmp_logger = logger_switch.get(log_name, "")
    if not tmp_logger:
        raise Exception("The log name is wrong")
    if lv == 'error':
        tmp_logger.error(record)
    elif lv == 'info':
        tmp_logger.info(record)


# def raise_logger(msg, log_name='rs_info', error_code=10000, queue="queue"):
#     """
#
#     :param msg: 日志的写入内容，若为int，则表示为报错编码；为str则是报错信息
#     :param log_name: 要写入的日志文件 rs_info rs_err
#     :param error_code:
#     :param queue:
#     :return:
#     """
#
#     way, level = log_name.split('_')
#
#     params = {
#         'log_name': log_name,
#         'error_code': error_code,
#         'queue': queue
#     }
#
#     record = make_msg(msg, params, True)
#     # 拼接的内容头，time+当前方法名+当前文件+调用方法+调用所在行+调用代码所在文件
#
#     server_name = config.get_bases_conf()["server"]["name"]
#     file_path = str(sys._getframe().f_back.f_code.co_filename)
#     file_path = file_path[file_path.rindex(server_name) + len(server_name):]
#     record = super_json_dumps({
#         "time": str(datetime.datetime.now()),
#         "func": str(sys._getframe().f_back.f_code.co_name),
#         "lineno": file_path + ":" + str(sys._getframe().f_back.f_lineno),
#         "msg": record
#     }) + '===' + str(log_name)
#
#     # 记录日志
#     tmp_logger = logging.getLogger(way)
#     if level == 'error':
#         tmp_logger.error(record)
#     elif level == 'info':
#         tmp_logger.info(record)
#
#     # 生产消息
#     # put_rmq(record, queue)


def make_msg(msg, params, with_code=False):
    if with_code:
        if isinstance(msg, int):
            err_code = msg
        else:
            err_code = params.get("error_code", 10000)
        err_desc = error_code_utils.get_error_desc(err_code)
        err_msg = error_code_utils.get_error_msg(err_code)

        if isinstance(msg, str):
            msg = str(err_code) + "-" + err_msg + "-" + err_desc + "-" + msg
        else:
            msg = str(err_code) + "-" + err_msg + "-" + err_desc + "-" + 'None'
    else:
        msg = '0-None-' + str(msg)
    return msg


def put_rmq(msg, queue):
    produce_object(msg, queue)


if __name__ == '__main__':
    pass
    raise_logger("123", "wallet", "info")