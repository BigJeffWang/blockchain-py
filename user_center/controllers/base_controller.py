from flask_restful import Resource
from common_settings import *
from tools.redis_tools import RedisTools
from flask import request
from crypto_utils import *
from log import raise_logger
from tools.request_tools import RequestTools
from utils import *
from services.api_token_service import ApiTokenService
from services.decrypt_service import DecryptService
from errors.error_handler import OperateUsageException, InvalidUsageException
from services.vcode_service import VcodeService
import logging


class BaseController(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_tools = RequestTools()
        self.logger = logging.getLogger('rs')

    def return_error(self, err_code, error_msg=None, status_code=400):
        self.request_tools.return_error(err_code, error_msg, status_code)

    # 正式环境测试，开所有校验的函数头
    def get_argument_dict(self, must_keys=None, format_str=False, format_keys=True, format_eval=True,
                          verify_timeliness=True, encrypt=True, check_token=True, invariable_key=True,
                          check_form_token=False, is_transfer=False,
                          api_type=_USER_TYPE_INVEST, request_type=_REQUEST_TYPE_LOGIN,
                          decode_by_inner=_DECODE_TYPE_DEFAULT, check_user_id=False):
        """
        :param must_keys: 必须含有的key
        :param format_str: str格式化
        :param format_keys: keys格式化
        :param format_eval:
        :param verify_timeliness: 校验时效性
        :param encrypt: 是否加密
        :param check_token: 是否校验token
        :param invariable_key: 是否采用默认的sharekey解密
        :param check_form_token: 是否校验表单的随机字符串
        :param is_transfer: 是否是通过usercenter传递数据到其他平台
        :param api_type: 访问接口的用户类型
        :param request_type: 请求的类型：注册、登陆前、登陆后
        :param decode_by_inner: 是否采用内网的sharekey解析
        :param check_user_id: 是否校验userid的正确性
        :return:
        """
        env = get_conf('env')
        if env == 'dev' and get_conf('close_all_aes'):
            # 测试环境，关所有校验的函数头
            verify_timeliness = False
            encrypt = False
            check_token = False
            invariable_key = False
            check_form_token = False

        try:
            # 1. 校验时效性
            if not verify_timeliness:
                request_header = request.headers
                source = request_header.get("Source", _SOURCE_TYPE_1)
            else:
                '''
                # 校验实效性，需要header中存在如下参数 Timestamp， Signature， Nonce， Source
                '''
                redis_tools = RedisTools()
                request_header = request.headers
                # 1.0 判断时间是否在请求限制时间内
                timestamp = request_header.get("Timestamp", '0')
                df_timestamp = abs(int(time.time()) - int(timestamp))
                if df_timestamp > 6000 or df_timestamp < 0:
                    self.return_error(10005)

                # 2.0 检查signature是否在redis中,防止重复请求
                c_signature = request_header.get("Signature")
                if redis_tools.exists(c_signature):
                    self.return_error(10003)

                # 3.0 验证c_signature合理性
                nonce = request_header.get("Nonce", '')
                source = request_header.get("Source", _SOURCE_TYPE_1)
                if nonce == '' or source == '':
                    self.return_error(10006)
                s_signature = sha256_hex(str(timestamp) + str(nonce) + str(source))
                self.logger.info('check signature ' + str(timestamp) + ' ' + str(nonce) + ' ' + str(source) + ' ' + str(s_signature) + ' ' + str(c_signature))
                if s_signature != c_signature:
                    self.return_error(10004)

                # 4.0 将c_signature存到redis中
                redis_tools.set(name=c_signature, value="c_signature", ex=60)

            content = self.get_request_content()
            share_key, nonce = None, None

            # 2.1 不解密解析，仅开发环境生效
            if not encrypt:
                decrypt_content = content
                if 'data' in content and isinstance(content['data'], dict):
                    for k, v in content['data'].items():
                        content[k] = v
                    del content['data']

                if check_token:
                    #  2.0 获取用户信息
                    ts = ApiTokenService(aes_share_key=share_key, aes_nonce=nonce).check_access_token_by_user_id(decrypt_content, api_type)
                    if not ts:
                        self.return_error(10035)
            else:
                if 'data' not in content.keys():
                    self.return_error(10008)
                delete_user_id = False
                if is_transfer and content['user_mobile'] == '':
                    invariable_key = False
                    check_token = False
                    decode_by_inner = _DECODE_TYPE_DEFAULT
                    delete_user_id = True

                # 2.2 使用指定秘钥解密
                if invariable_key:
                    decrypt_content, share_key, nonce = self.decrypt_request_content(
                        content, check_token=check_token, api_type=api_type, request_type=request_type,
                        check_user_id=check_user_id, source=source)
                else:
                    decrypt_content, share_key, nonce = self.decrypt_request_content_with_invariable_key(
                        content, check_token=check_token, api_type=api_type,
                        decode_by_inner=decode_by_inner, source=source)
                if delete_user_id:
                    decrypt_content['user_id'] = ''

            # 3 规范入参
            request_args = formate_args(decrypt_content, format_str, format_keys, format_eval)
            self.logger.info("request_args解析后:" + str(request_args))

            # 4 确保表单有效性
            if check_form_token:
                if 'form_token' not in request_args:
                    self.return_error(10046)
                vcode_service = VcodeService(aes_share_key=share_key, aes_nonce=nonce)
                # 2.0 校验token
                vcode_service.check_register_signature(request_args['form_token'])
                request_args.pop('form_token')

            # 5 校验是否包含规定的参数
            if must_keys:
                for key in must_keys:
                    if key not in request_args:
                        error_msg = "请求缺少 [%s] 参数" % key
                        self.return_error(10048, error_msg=error_msg)
            return request_args, share_key, nonce
        except InvalidUsageException as error:
            raise_logger(error.error_msg, error_code=error.error_code)
            raise error
        except OperateUsageException as error:
            raise error
        except Exception as error:
            raise_logger(str(error), error_code=10022)
            self.return_error(10022)

    def get_request_content(self, set_default=True):
        """
        获取请求参数,如果参数中有data字段,直接返回data字段内容
        :return:
        """
        request_type = request.headers.get('Content-Type')
        user_mobile = request.headers.get('User-Mobile', default="")
        source = request.headers.get("Source", _SOURCE_TYPE_1)
        if user_mobile != "":
            user_mobile = str(base64.b64decode(bytes(user_mobile, encoding="utf8")), encoding="utf8")
        access_token = request.headers.get('Authorization', default="")
        if request_type:
            content_type = request_type.split(';')[0].lower()
            if content_type == "application/json":
                self.logger.info("Content-Type: application/json")
                request_args = request.get_json()
            else:  # multipart/form-data
                self.logger.info("Content-Type: multipart/form-data")
                request_args = request.form
                request_args = request_args.to_dict()
        else:
            self.logger.info("Content-Type: None")
            request_args = {}
            for i in request.values.dicts:
                for k, v in i.items():
                    request_args[k] = v

        if set_default:
            request_args.setdefault("user_mobile", user_mobile)
            request_args.setdefault("access_token", access_token)
            request_args.setdefault("source", source)
        return request_args

    def decrypt_request_content(self, content, check_token=True, api_type=_USER_TYPE_INVEST,
                                request_type= _REQUEST_TYPE_LOGIN, check_user_id=False, source=_SOURCE_TYPE_1):
        """
        解析用户请求参数
        :param check_token: 是否对token进行校验(针对注册登录提交信息的接口)
        :return:
        """
        user_mobile = content.get("user_mobile")
        self.logger.info("存在key为data的数据,开始使用用户绑定密钥对数据进行解密")
        encrypt_data = content.get("data")
        ds = DecryptService()
        decrypt_data, share_key, nonce = ds.decrypt_users_data(
            user_mobile,
            encrypt_data,
            check_token=check_token,
            api_type=api_type,
            request_type=request_type,
            check_user_id=check_user_id,
            source=source
        )
        content.pop("data")
        content = dict(content, **decrypt_data)
        return content, share_key, nonce

    def decrypt_request_content_with_invariable_key(self, content, check_token=True,
                                                    api_type=_USER_TYPE_INVEST, decode_by_inner=_DECODE_TYPE_DEFAULT,
                                                    source=_SOURCE_TYPE_1):
        """
        使用不变key,解密请求参数(针对注册,登录获取sqlt和验证用户是否注册的接口)
        :return:
        """
        self.logger.info("存在key为data的数据,开始使用未用户绑定密钥对数据进行解密")
        encrypt_data = content.get("data")
        ds = DecryptService()
        decrypt_data, share_key, nonce = ds.decrypt_request_content_with_invariable_key(
            encrypt_data,
            check_token,
            api_type,
            decode_by_inner=decode_by_inner
        )
        content.pop("data")
        content = dict(content, **decrypt_data)
        return content, share_key, nonce

    def check_form_token(self, token):
        vcode_service = VcodeService()
        # 2.0 校验token
        return vcode_service.check_register_signature(token, direct_error=False)





