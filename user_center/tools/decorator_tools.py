from functools import wraps
import traceback
from tools.request_tools import RequestTools
from werkzeug.exceptions import HTTPException
from log import raise_logger
from tools.data_formate_tools import make_body_return_success, make_body_tranfer_return_success


class FormateOutput(object):
    def __init__(self, return_type='str', default_value=None, cover_http_exception=False):
        '''
        # try 机制的返回信息，若代码正常则按照原代码逻辑返回数据，否则return_error
        :param return_type: 返回值的类型
        :param default_value: 默认的返回值
        :param cover_http_exception: 是否覆盖程序本身抛出的HTTPException(也就是程序调用的self.return_error方法)
        '''
        self.return_type = return_type
        self.default_value = default_value
        self.cover_http_exception = cover_http_exception

    def __call__(self, func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            try:
                func_data = func(*args, **kwargs)
                return func_data
            except HTTPException as e:
                if not self.cover_http_exception:
                    raise e
                else:
                    exceptions = traceback.format_exc()
                    if exceptions:
                        exception_list = exceptions.split(':')
                        if not exception_list[0] == 'NoneType':
                            for i in exception_list:
                                for j in i.split("\n"):
                                    raise_logger(j, 'rs_error')
                                    pass
                            return_msg = self.get_return_msg()
                            return return_msg
            except Exception:
                exceptions = traceback.format_exc()
                if exceptions:
                    exception_list = exceptions.split(':')
                    if not exception_list[0] == 'NoneType':
                        for i in exception_list:
                            for j in i.split("\n"):
                                raise_logger(j, 'rs_error')
                        return_msg = self.get_return_msg()
                        return return_msg

        return wrapped_func

    def get_return_msg(self):
        if self.return_type == 'str':
            if self.default_value is None:
                return ''
            else:
                return self.default_value
        elif self.return_type == 'return_error':
            request_tools = RequestTools()
            request_tools.return_error(int(self.default_value))
        elif self.return_type == 'return_error_by_header':
            request_tools = RequestTools()
            request_tools.return_error_by_header(int(self.default_value))

        # 出现报错，最后的方案是直接return_error终止程序
        request_tools = RequestTools()
        request_tools.return_error(10000)


class AESOutput(object):
    def __init__(self, **kwargs):
        """
        加密输出正常运算结果的方法结果的方法
        """
        pass
        self.cover_body = True
        if 'cover_body' in kwargs:
            self.cover_body = kwargs['cover_body']

    def __call__(self, func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            func_data = func(*args, **kwargs)
            if isinstance(func_data, tuple) and len(func_data) == 3:
                if self.cover_body:
                    return make_body_return_success(func_data[0], func_data[1], func_data[2])
                else:
                    return make_body_tranfer_return_success(func_data[0], func_data[1], func_data[2])
            else:
                return func_data
        return wrapped_func


