import os
import json
import time
import logging
import logging.config
from utils import error_code_utils
import sys
import config
from mq.producer_mq import produce_object
from tools.tool import super_json_dumps, detect_file
from multiprocessing import Process, Value


def show_sqlalchemy_log():
    logging.basicConfig()
    # By default, the log level is set to logging.WARN.
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class ContextFilter(logging.Filter):
    def filter(self, record):
        return True


class Slog(object):
    diy_conf = None
    diy_logger = None

    def __init__(self, log_name=None):
        """
        生成logging.json没有的配置文件
        :param log_name: 会以log_name 命名logs/下的log文件
        """
        if log_name:
            self.diy_conf = {
                "handlers": {
                    log_name + "_info_file_handler": {
                        "class": "logging.handlers.RotatingFileHandler",
                        "level": "INFO",
                        "formatter": "simple",
                        "filename": log_name + "_info.log",
                        "maxBytes": 10485760,
                        "backupCount": 50,
                        "encoding": "utf8"
                    },
                    log_name + "_error_file_handler": {
                        "class": "logging.handlers.RotatingFileHandler",
                        "level": "ERROR",
                        "formatter": "simple",
                        "filename": log_name + "_errors.log",
                        "maxBytes": 10485760,
                        "backupCount": 20,
                        "encoding": "utf8"
                    }
                },
                "loggers": {
                    log_name: {
                        "level": "DEBUG",
                        "handlers": [
                            log_name + "_info_file_handler",
                            log_name + "_error_file_handler"
                        ]
                    }
                }
            }
            self.setup_logging()
            self.diy_logger = logging.getLogger(log_name)

    def info(self, *msg):
        content = " ".join([str(i) for i in msg])
        self.diy_logger.info(content)

    def error(self, *msg):
        content = " ".join([str(i) for i in msg])
        self.diy_logger.error(content)

    def setup_logging(self, path='logging.json', default_level=logging.INFO):
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
                if self.diy_conf:
                    log_config["handlers"] = dict(log_config["handlers"], **self.diy_conf["handlers"])
                    log_config["loggers"] = dict(log_config["loggers"], **self.diy_conf["loggers"])
                for k, v in log_config.items():
                    if k != 'handlers':
                        continue
                    for k1, v1 in v.items():
                        if 'filename' in v1:
                            v1['filename'] = os.path.join(real_path, v1['filename'])
            logging.config.dictConfig(log_config)
        else:
            logging.basicConfig(level=default_level)


Slog().setup_logging()

logger = logging.getLogger('rs')
game_bet_in_logger = logging.getLogger('game_bet_in')
game_publish_lottery = logging.getLogger('game_publish_lottery')
game_product_logger = logging.getLogger('game_product')
block_logger = logging.getLogger('block')
wallet_logger = logging.getLogger('wallet')
script_logger = logging.getLogger('script')
timing_logger = logging.getLogger('timing')

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
        "game_bet_in": game_bet_in_logger,
        "game_publish_lottery": game_publish_lottery,
        "game_product": game_product_logger,
        "block": block_logger,
        "wallet": wallet_logger,
        "script": script_logger,
    }
    tmp_logger = logger_switch.get(log_name, "")
    if not tmp_logger:
        raise Exception("The log name is wrong")
    if lv == 'error':
        tmp_logger.error(record)
    elif lv == 'info':
        tmp_logger.info(record)


class TimingLog(object):
    begin_time = None
    end_time = None

    @classmethod
    def begin(cls):
        cls.begin_time = time.time()

    @classmethod
    def end(cls, floor="3"):
        """
        计时log,统计运行时间
        :return:
        """
        cls.end_time = time.time()
        record = "%.10f seconds" % (cls.end_time - cls.begin_time)
        sys_frame = sys._getframe()
        floor_back = {
            "1": sys_frame,
            "2": sys_frame.f_back,
            "3": sys_frame.f_back.f_back if hasattr(sys_frame.f_back, "f_back") else None,
        }
        floor_back["4"] = floor_back["3"].f_back if floor_back["3"] else None
        floor_back["5"] = floor_back["4"].f_back if floor_back["4"] else None
        f_back = floor_back[str(floor)]
        file_path = str(f_back.f_code.co_filename)
        line_no = str(f_back.f_lineno)
        func_name = str(f_back.f_code.co_name)
        if file_path[0] == "/":
            if log_server_name in file_path:
                file_path = file_path[file_path.rindex(log_server_name) + len(log_server_name):]

        file = " file:" + file_path + " line:" + line_no + " func:" + func_name
        record = super_json_dumps({
            "position": file,
            "msg": record
        })
        timing_logger.info(record)


class MultiProcessTimingLog(Process):
    alive = None
    begin_time = None
    end_time = None
    floor = None

    def __init__(self, floor="4"):
        super().__init__()
        self.floor = floor
        self.alive = Value('b', True)
        sys_frame = sys._getframe()
        floor_back = {
            "1": sys_frame,
            "2": sys_frame.f_back,
            "3": sys_frame.f_back.f_back if hasattr(sys_frame.f_back, "f_back") else None,
        }
        floor_back["4"] = floor_back["3"].f_back if floor_back["3"] else None
        floor_back["5"] = floor_back["4"].f_back if floor_back["4"] else None
        f_back = floor_back[str(floor)]
        if f_back is None:
            raise Exception("It doesn't have that many layers")
        self.file_path = str(f_back.f_code.co_filename)
        self.line_no = str(f_back.f_lineno)
        self.func_name = str(f_back.f_code.co_name)

    def run(self):
        self.begin()
        flag = 0
        while self.alive.value:
            if flag >= 10:
                break
            time.sleep(1)
            flag += 1
        self.end()

    def stop(self):
        self.alive.value = False

    def begin(self):
        self.begin_time = time.time()

    def end(self):
        """
        计时log,统计运行时间
        :return:
        """
        self.end_time = time.time()
        record = "%.10f seconds" % (self.end_time - self.begin_time)
        file_path = self.file_path
        line_no = self.line_no
        func_name = self.func_name
        if file_path[0] == "/":
            if log_server_name in file_path:
                file_path = file_path[file_path.rindex(log_server_name) + len(log_server_name):]

        file = " file:" + file_path + " line:" + line_no + " func:" + func_name
        record = super_json_dumps({
            "position": file,
            "msg": record
        })
        timing_logger.info(record)


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
    # 第二个参数 可以是 rs game_bet_in game_product block wallet script
    # raise_logger("123", "game_bet_in", "info")
    # raise_logger("123", "game_bet_in", "error")
    # TimingLog.begin()
    # TimingLog.end()
    mpt = MultiProcessTimingLog("2")
    mpt.start()
    for i in range(10):
        time.sleep(2)
        print(time.time())
    # mpt.stop()
