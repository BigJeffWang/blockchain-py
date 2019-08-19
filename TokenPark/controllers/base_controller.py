from flask import request
from flask_restful import Resource
from utils.log import raise_logger
from tools.tool import formate_args
from flask import make_response
from tools.request_tools import RequestTools
from tools.transfer_tools import transfer_to_platform
from config import get_user_center_conf, get_env
from utils.util import time_transform_from_zone, recursive_dict_args
from common_settings import _REQUEST_KEY_LIST, _RESPONSE_KEY_LIST


class BaseController(Resource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_tools = RequestTools()

    def return_error(self, error_code, error_msg=None, status_code=200):
        self.request_tools.return_error(error_code, error_msg, status_code)

    def get_argument_dict(self, must_keys=None, format_str=False, format_keys=True, format_eval=True, check_form_token=False, time_key_list=None):
        """
        :param must_keys: must_keys=["aa", "bb"] 判断出入列表里的值,是否在请求参数里,没有报错
        :param format_str: 是否需要把所有int类型,强转成字符串
        :param format_eval: 是否开启 把字符串 '["a","b"]' '{"a":1,"b":"1"}' 强转回list dict
        :param format_keys: 是否开启 把key的值 转为全小写
        :param check_form_token: 是否校验表单中的随机字符串，所有会修改数据的请求，都应该校验！！
        :param time_key_list: 转换时区的校验时间key补充字段列表
        :return:
        """
        # 获取参数字典
        request_args = self.get_request_content()

        request_args = formate_args(request_args, format_str, format_keys, format_eval)

        if get_env() != 'dev' and check_form_token:
            if 'form_token' not in request_args:
                self.return_error(10018)
            check_url = get_user_center_conf()[get_env()]['base_url'] + '/transfer/' + str(request_args['form_token'])
            check_result = transfer_to_platform(check_url)
            if not check_result:
                self.return_error(10018)
            request_args.pop('form_token')

        # 判断必填字段
        if must_keys:
            for key in must_keys:
                if key not in request_args:
                    raise_logger("请求缺少 [%s] 参数" % key, lv="error")
                    self.return_error(20003)
        return self.timezone_transform(request_args, time_key_list)

    def timezone_transform(self, request_args, other_listen_key_list=None):
        """
        转换请求参数时间
        :param request_args:
        :param other_listen_key_list:
        :return:
        """
        listen_key_list = _REQUEST_KEY_LIST
        if isinstance(other_listen_key_list, list):
            listen_key_list = list(set(listen_key_list + other_listen_key_list))
        if request.method == "POST":
            try:
                timezone = int(request.headers.get('TimeZone', ''))
            except:
                self.return_error(10021)
                timezone = 0
            request_args["timezone"] = timezone
            request_args = recursive_dict_args(request_args, listen_key_list, time_transform_from_zone, timezone)
        return request_args

    def utctime_to_localtime(self, response_args, other_listen_key_list=None):
        """
        服务端utc时间转换给客户端相应时区的时间
        :param response_args:
        :param other_listen_key_list:
        :return:
        """
        if not isinstance(response_args, dict):
            return response_args
        listen_key_list = _RESPONSE_KEY_LIST
        if isinstance(other_listen_key_list, list):
            listen_key_list = list(set(listen_key_list + other_listen_key_list))
        try:
            timezone = int(request.headers.get('TimeZone', ''))
            if timezone == "" and request.method == "POST":
                self.return_error(10021)
        except:
            timezone = 0
            self.return_error(10021)
        response_args = recursive_dict_args(response_args, listen_key_list, time_transform_from_zone, -timezone)
        return response_args

    def get_request_content(self):
        """
        获取请求参数,如果参数中有data字段,直接返回data字段内容
        :return:
        """
        request_type = request.headers.get('Content-Type')
        if request_type:
            content_type = request_type.split(';')[0].lower()
            if content_type == "application/json":
                request_args = request.get_json()
            else:  # multipart/form-data
                request_args = request.form
                request_args = request_args.to_dict()
        else:
            request_args = {}
            for i in request.values.dicts:
                for k, v in i.items():
                    request_args[k] = v

        return request_args

    def make_html_response(self, value):
        resp = make_response(value)
        resp.headers['Content-Type'] = 'text/html'
        return resp
