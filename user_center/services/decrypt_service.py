import binascii
from crypto_utils import deAES, sha256
from models.invest_user_model import InvestUserModel
from services.base_service import BaseService
from services.api_token_service import ApiTokenService
from models.admin_user_model import AdminUserModel
from models.key_salt_model import KeySaltModel
from common_settings import *
from models.borrow_user_model import BorrowUserModel
from dateutil.relativedelta import relativedelta
import datetime
from log import raise_logger


class DecryptService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_salt_expiry_date(self, source=_SOURCE_TYPE_1):
        return datetime.datetime.now() - relativedelta(months=+1)

    def decrypt_users_data(self, user_mobile, encrypt_data, check_token=False, api_type=_USER_TYPE_INVEST,
                           request_type= _REQUEST_TYPE_LOGIN, check_user_id=False, source=_SOURCE_TYPE_1):
        """
        针对不同用户，使用不同的私钥解密
        :param user_mobile:
        :param encrypt_data:
        :param check_token: 是否对token进行校验
        :return:
        """
        with self.session_scope() as session:
            #  1.0 获取用户信息
            if api_type == _USER_TYPE_INVEST:
                UserModel = InvestUserModel
            elif api_type == _USER_TYPE_ADMIN:
                UserModel = AdminUserModel
            elif api_type == _USER_TYPE_BORROW:
                UserModel = BorrowUserModel
            else:
                self.return_error(10017)
            expiry_date = self.get_salt_expiry_date(source=source)
            if request_type == _REQUEST_TYPE_REGISTER:
                salt_info = session.query(KeySaltModel.share_key, KeySaltModel.nonce) \
                    .filter(KeySaltModel.deleted == False,
                            KeySaltModel.user_id == user_mobile,
                            KeySaltModel.user_type == api_type,
                            KeySaltModel.request_type == request_type,
                            KeySaltModel.source == source,
                            KeySaltModel.created_at > expiry_date,
                            ).first()
            elif request_type == _REQUEST_TYPE_LOGINING:
                if api_type == _USER_TYPE_ADMIN:
                    salt_info = session.query(UserModel.user_id, KeySaltModel.share_key, KeySaltModel.nonce, UserModel.level) \
                        .outerjoin(KeySaltModel, UserModel.user_id == KeySaltModel.user_id) \
                        .filter(UserModel.name == user_mobile,
                                UserModel.deleted == False,
                                KeySaltModel.deleted == False,
                                KeySaltModel.user_type == api_type,
                                KeySaltModel.request_type == _REQUEST_TYPE_LOGIN,
                                KeySaltModel.source == source,
                                KeySaltModel.created_at > expiry_date,
                                ).first()
                else:
                    # 手机号登陆到情况
                    salt_info = session.query(UserModel.user_id, KeySaltModel.share_key, KeySaltModel.nonce) \
                        .outerjoin(KeySaltModel, UserModel.user_id == KeySaltModel.user_id) \
                        .filter(UserModel.user_mobile == user_mobile,
                                UserModel.deleted == False,
                                KeySaltModel.deleted == False,
                                KeySaltModel.user_type == api_type,
                                KeySaltModel.request_type == _REQUEST_TYPE_LOGIN,
                                KeySaltModel.source == source,
                                KeySaltModel.created_at > expiry_date,
                                ).first()
                    if salt_info is None:
                        # email登陆到情况
                        salt_info = session.query(UserModel.user_id, KeySaltModel.share_key, KeySaltModel.nonce) \
                            .outerjoin(KeySaltModel, UserModel.user_id == KeySaltModel.user_id) \
                            .filter(UserModel.email == user_mobile,
                                    UserModel.deleted == False,
                                    KeySaltModel.deleted == False,
                                    KeySaltModel.user_type == api_type,
                                    KeySaltModel.request_type == _REQUEST_TYPE_LOGIN,
                                    KeySaltModel.source == source,
                                    KeySaltModel.created_at > expiry_date,
                                    ).first()
                    if salt_info is None:
                        # 用户名登陆到情况
                        salt_info = session.query(UserModel.user_id, KeySaltModel.share_key, KeySaltModel.nonce) \
                            .outerjoin(KeySaltModel, UserModel.user_id == KeySaltModel.user_id) \
                            .filter(UserModel.user_name == user_mobile,
                                    UserModel.deleted == False,
                                    KeySaltModel.deleted == False,
                                    KeySaltModel.user_type == api_type,
                                    KeySaltModel.request_type == _REQUEST_TYPE_LOGIN,
                                    KeySaltModel.source == source,
                                    KeySaltModel.created_at > expiry_date,
                                    ).first()
            else:
                if api_type == _USER_TYPE_ADMIN:
                    salt_info = session.query(UserModel.user_id, KeySaltModel.share_key, KeySaltModel.nonce, UserModel.level) \
                        .outerjoin(KeySaltModel, UserModel.user_id == KeySaltModel.user_id) \
                        .filter(UserModel.user_id == user_mobile,
                                UserModel.deleted == False,
                                KeySaltModel.deleted == False,
                                KeySaltModel.user_type == api_type,
                                KeySaltModel.request_type == request_type,
                                KeySaltModel.source == source,
                                KeySaltModel.created_at > expiry_date,
                                ).first()
                else:
                    salt_info = session.query(UserModel.user_id, KeySaltModel.share_key, KeySaltModel.nonce) \
                        .outerjoin(KeySaltModel, UserModel.user_id == KeySaltModel.user_id) \
                        .filter(UserModel.user_id == user_mobile,
                                UserModel.deleted == False,
                                KeySaltModel.deleted == False,
                                KeySaltModel.user_type == api_type,
                                KeySaltModel.request_type == request_type,
                                KeySaltModel.source == source,
                                KeySaltModel.created_at > expiry_date,
                                ).first()
            raise_logger("用户:%s的用户信息获取成功" % user_mobile)
            #  2.0 判断用户解密言在不在, 如果不在则报错
            if not salt_info or (not salt_info.share_key) or (not salt_info.nonce):
                raise_logger("用户解密言不在")
                self.return_error(10018)
            json_dict = self.decrypt_data(encrypt_data, str(salt_info.share_key), str(salt_info.nonce))
            if api_type == _USER_TYPE_ADMIN:
                json_dict['admin_user_level'] = salt_info.level

            if request_type != _REQUEST_TYPE_REGISTER:
                user_mobile = salt_info.user_id
                # 登录的情况下，若入参没有userid则补充进来，若有userid则校验其与数据库信息是否一致
                if check_user_id and isinstance(json_dict, dict):
                    if 'user_id' not in json_dict:
                        json_dict['user_id'] = salt_info.user_id
                    elif json_dict['user_id'] != salt_info.user_id:
                        self.return_error(10037)

            if check_token:
                ts = ApiTokenService().check_access_token(
                    user_mobile,
                    json_dict['access_token'],
                    api_type,
                    source=source,
                )
                if not ts:
                    self.return_error(10035)
            return json_dict, salt_info.share_key, salt_info.nonce

    def decrypt_request_content_with_invariable_key(self, encrypt_data, check_token=False,
                                                    api_type=_USER_TYPE_INVEST, decode_by_inner=_DECODE_TYPE_DEFAULT,
                                                    source=_SOURCE_TYPE_1):
        """
        请求参数解密
        :param user_mobile: 用户手机号  
        :param encrypt_data: 加密参数
        :param check_token: 是否对token（用户）进行校验
        :return:
        """
        with self.session_scope() as session:
            # print("开始解析...", encrypt_data, check_token, api_type, decode_by_inner, source)
            #  1.0 对数据进行解密,如果解密出错,则双方协议出现问题.需要用户退出重新登录.
            if decode_by_inner == _DECODE_TYPE_INNER:
                share_key, nonce = _INNER_SHARE_KEY, _INNER_NONCE
            else:
                share_key, nonce = _SHARE_KEY, _NONCE
            json_dict = self.decrypt_data(encrypt_data, str(share_key), str(nonce))
            # print("解析完成:\n", json_dict)
            if check_token:
                if 'user_id' not in json_dict:
                    self.return_error(10017)
                #  2.0 获取用户信息
                if api_type == _USER_TYPE_INVEST:
                    UserModel = InvestUserModel
                elif api_type == _USER_TYPE_BORROW:
                    UserModel = BorrowUserModel
                else:
                    self.return_error(10016)
                user_info = session.query(UserModel.user_id) \
                    .filter(UserModel.user_id == json_dict['user_id'], UserModel.deleted == False).first()
                # print("用户信息获取成功", user_info)
                if user_info is None:
                    self.return_error(10015)

                ts = ApiTokenService().check_access_token(
                    json_dict["user_id"],
                    json_dict['access_token'],
                    api_type,
                    source=source,
                )
                if not ts:
                    self.return_error(10035)
            return json_dict, share_key, nonce

    def decrypt_data(self, encrypt_data, share_key, nonce):
        """
        对数据进行解密,数据必须为json格式字符串
        :param encrypt_data: 加密Data
        :param share_key: share_key
        :param nonce: 随机数
        :return:
        """

        b_nonce = binascii.unhexlify(nonce)
        b_data = binascii.unhexlify(encrypt_data)
        content = deAES(b_data, sha256(share_key), b_nonce).decode('utf-8')
        json_dict = eval(content)
        return json_dict

