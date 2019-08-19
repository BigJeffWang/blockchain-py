from flask import request
from flask_restful import Resource
from utils.log import raise_logger
from tools.tool import formate_args
from flask import make_response
from tools.request_tools import RequestTools
from config import get_white_list


class BaseController(Resource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_tools = RequestTools()

    def get_argument_dict(self, must_keys=None, format_str=False, format_keys=True,
                          format_eval=True, verify_timeliness=True, verify_key=None,
                          expire_time=None, check_token=True, invariable_key=False, api_type="invest"):
        """
        :param must_keys: must_keys=["aa", "bb"] 判断出入列表里的值,是否在请求参数里,没有报错
        :param format_str: 是否需要把所有int类型,强转成字符串
        :param format_eval: 是否开启 把字符串 '["a","b"]' '{"a":1,"b":"1"}' 强转回list dict
        :param format_keys: 是否开启 把key的值 转为全小写
        :param verify_timeliness: 是否做请求时效校验，默认需要校验
        :param verify_key: 请求时效校验所包含的key，默认不包含key的校验
        :param expire_time: 请求实效校验的时效
        :param check_token: 是否检查token,存在token,则必须检查
        :param invariable_key: 用户未登录情况下,使用指定密钥解密
        :param api_type: invest/投资用户前端和移动端  borrow/管理后台
        :return:
        """
        # 获取参数字典
        ip = request.remote_addr
        white_list = get_white_list()
        if ip not in white_list:
            self.return_error(100000)
        request_args = {}
        if verify_timeliness and verify_key and expire_time and invariable_key:
            try:
                request_args = self.decrypt_request_content(check_token=check_token, api_type=api_type)

                print("request_args解析后:\n", request_args)
            except Exception as error:
                raise_logger(str(error))
                self.return_error(10006, error_msg="解析参数出现错误,请重新尝试")
        else:
            request_args = self.get_request_content()

        request_args = formate_args(request_args, format_str, format_keys, format_eval)

        # 判断必填字段
        if must_keys:
            for key in must_keys:
                if key not in request_args:
                    raise_logger("请求缺少 [%s] 参数" % key, error_code=20003)
                    self.return_error(20003)
        return request_args

    # def get_bank_argument_dict(self, format_str=False, format_keys=True,
    #                            format_eval=True):
    #     """
    #     :param must_keys: must_keys=["aa", "bb"] 判断出入列表里的值,是否在请求参数里,没有报错
    #     :param format_str: 是否需要把所有int类型,强转成字符串
    #     :param format_eval: 是否开启 把字符串 '["a","b"]' '{"a":1,"b":"1"}' 强转回list dict
    #     :param format_keys: 是否开启 把key的值 转为全小写
    #     :return:
    #     """
    #     # 获取参数字典
    #     request_args = self.get_request_content()
    #     args = formate_args(request_args, format_str, format_keys, format_eval)
    #     cfca_helper = CfcaHelper()
    #     print("银行返回的原装参数=========")
    #     print(request_args)
    #     return cfca_helper.res_data(args)

    def return_error(self, error_code, error_msg=None, status_code=200):
        self.request_tools.return_error(error_code, error_msg, status_code)

    def decrypt_request_content(self, check_token, api_type):
        """
        解析用户请求参数
        :param check_token: 是否对token进行校验(针对注册登录提交信息的接口)
        :return:
        """
        content = self.get_request_content()
        user_mobile = content.get("user_mobile")

        # 临时添加,防止加密
        version = request.headers.get('Version', "1.0")
        if version == "1.0":
            return content

        if "data" in content.keys():
            print("存在key为data的数据,开始使用用户绑定密钥对数据进行解密")
            encrypt_data = content.get("data")
            ds = DecryptService()
            decrypt_data = ds.decrypt_request_content_with_invariable_key(user_mobile, encrypt_data, check_token, api_type)
            content.pop("data")
            content = dict(content, **decrypt_data)
        return content


    def get_request_content(self):
        """
        获取请求参数,如果参数中有data字段,直接返回data字段内容
        :return:
        """
        request_type = request.headers.get('Content-Type')
        user_mobile = request.headers.get('User-Mobile', default="")
        if request_type:
            content_type = request_type.split(';')[0].lower()
            if content_type == "application/json":
                print("application/json")
                request_args = request.get_json()
            else:  # multipart/form-data
                print("multipart/form-data")
                request_args = request.form
                request_args = request_args.to_dict()
        else:
            print("None Content-Type")
            request_args = {}
            for i in request.values.dicts:
                for k, v in i.items():
                    request_args[k] = v

        print("request_args解析前:\n", request_args)
        request_args.setdefault("user_mobile", user_mobile)
        return request_args

    def make_html_response(self, value):
        resp = make_response(value)
        resp.headers['Content-Type'] = 'text/html'
        return resp
