import os
import json
import logging
import logging.config
import error_code_utils
from mq.producer_mq import produce_object
import datetime
import sys
import config
from utils import detect_python_path, detect_file


def setup_logging(path='logging.json', default_level=logging.INFO):
    jsonPath = detect_python_path(path)
    detectResult = detect_file(path)

    if os.path.exists(jsonPath) and 'root' in detectResult:

        real_path = ''
        base_conf = config.get_conf('bases')
        env = config.get_conf('env')

        if base_conf.get('log_path') and os.path.exists('/data'):
            real_path = base_conf['log_path'] + '/' + base_conf['server_name'] + '/' + env
            if not os.path.exists(real_path):
                try:
                    os.makedirs(real_path)
                except Exception as e:
                    real_path = ''
        if not real_path:
            real_path = detectResult['root'] + '/logs'
        with open(jsonPath, 'rt') as f:
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
ess_logger = logging.getLogger('ess')
match_logger = logging.getLogger('match')
payback_logger = logging.getLogger('payback')
repay_logger = logging.getLogger('repay')


def raise_logger(msg, log_name='rs_info', error_code=10000, queue=None):
    """
    :param msg: 日志的写入内容，若为int，则表示为报错编码；为str则是报错信息
    :param log_name: 要写入的日志文件 rs_info rs_err
    :param error_code:
    :param queue:
    :return:
    """

    way, level = log_name.split('_')

    params = {
        'log_name': log_name,
        'error_code': error_code
    }

    record = make_msg(msg, params)
    # 拼接的内容头，time+当前方法名+当前文件+调用方法+调用所在行+调用代码所在文件

    server_name = config.get_conf('bases')['server_name']
    file_path = str(sys._getframe().f_back.f_code.co_filename)
    file_path = file_path[file_path.rindex(server_name) + len(server_name):]
    record = json.dumps({
        "time": str(datetime.datetime.now()),
        "func": str(sys._getframe().f_back.f_code.co_name),
        "lineno": file_path + ":" + str(sys._getframe().f_back.f_lineno),
        "msg": record
    }, ensure_ascii=False) + '===' + str(log_name)
    # 记录日志
    tmp_logger = logging.getLogger(way)
    if level == 'error':
        tmp_logger.error(record)
    elif level == 'info':
        tmp_logger.info(record)

    # 生产消息
    # put_rmq(record, queue)


def make_msg(msg, params):
    err_code = params.get("error_code", 10000)
    err_desc = error_code_utils.get_error_desc(err_code)
    err_msg = error_code_utils.get_error_msg(err_code)
    if msg == '':
        msg = 'None'
    msg = str(err_code) + "-" + err_msg + "-" + err_desc + "-" + msg
    return msg


def put_rmq(msg, queue):
    produce_object(msg, queue)


if __name__ == '__main__':
    pass

