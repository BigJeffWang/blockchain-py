import os
import traceback
from functools import wraps
from utils.log import raise_logger, log_server_env, whether_on_server
from tools.request_tools import RequestTools
from werkzeug.exceptions import HTTPException
from flask import make_response


class FormatOutput(object):
    def __init__(self, return_type=None, default_value=10001):
        """
        # try 机制的返回信息，若代码正常则按照原代码逻辑返回数据，否则return_error
        :param return_type: 返回值的类型
        :param default_value: 默认的返回值

        """

        if not return_type:
            return_type = 'str'
        self.return_type = return_type
        self.default_value = default_value

    def __call__(self, func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if log_server_env != "pd" and not whether_on_server:
                func_data = func(*args, **kwargs)
                return self.get_return_msg(func_data)
            else:
                try:
                    func_data = func(*args, **kwargs)
                    return self.get_return_msg(func_data)
                except HTTPException as he:
                    raise he
                except:
                    try:
                        exceptions = traceback.format_exc()
                        exception_list = exceptions.split('File ')
                        exc_list = exception_list[2].replace('"', "").split(",")[0].split(os.path.sep)
                        exc_desc = exc_list[-2] + "/" + exc_list[-1]
                        exc_log_list = exception_list[-1].replace("\n", " ").replace('"', "").split(" ")
                        exc_log_list = [msg for msg in exc_log_list if msg]
                        exc_file = " ".join(exc_log_list[:3]).replace(',', "")
                        exc_log = " ".join(exc_log_list[4:])
                        raise_logger(exc_log, "rs", "error", file=exc_file)
                    except:
                        exc_desc = ""
                    return self.get_return_msg(exc_desc, False)
        return wrapped_func

    def get_return_msg(self, data=None, category=True):
        if category:
            if self.return_type == 'str':
                return FormatOutput.make_body_return_success(data)
            else:
                return data
        else:
            if self.return_type == 'str':
                return FormatOutput.make_body_return_error(error_desc="System desc " + data)
            elif self.return_type == 'html':
                value = '' if self.default_value is None else self.default_value
                resp = make_response(value)
                resp.headers['Content-Type'] = 'text/html'
                return resp
            elif self.return_type == 'return_error_by_header':
                request_tools = RequestTools()
                request_tools.return_error_by_header(int(self.default_value))
            else:
                # self.return_type == 'return_error':
                request_tools = RequestTools()
                request_tools.return_error(int(self.default_value))

    @staticmethod
    def make_body_return_error(error_code=10001, error_desc="System desc", error_msg="系统错误"):
        return {
            "code": str(error_code),
            "desc": error_desc,
            "msg": error_msg,
            "data": {},
        }

    @staticmethod
    def make_body_return_success(response):
        if response is True or response is None:
            data = {}
        else:
            data = response

        return {
            "code": "00000",
            "desc": "success",
            "msg": "成功",
            "data": data
        }
