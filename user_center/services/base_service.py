"""
-------------------------------------------------
   File Name：     base_service.py
   Description:
   Author:        Zyt
   Date：          2018/7/26
-------------------------------------------------
"""
from config import *
from tools.request_tools import RequestTools
from contextlib import contextmanager
from errors.error_handler import *
from tools.decorator_tools import FormateOutput
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common_settings import *
from models.key_salt_model import KeySaltModel
from utils import check_mobile, check_mobile_all, check_email, get_random_str
from tools.sms_tools import *
from models.sms_message_model import SmsMessageModel
from tools.transfer_tools import transfer_to_platform
import time
import pytz
import datetime
from crypto_utils import encrypt_md5
from utils import send_mail


class BaseService(object):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.request_tools = RequestTools()
        self.engine = None
        self.Session = None
        self.aes_share_key = None
        self.aes_nonce = None

        self.init_session()
        if 'aes_share_key' in kwargs:
            self.aes_share_key = kwargs['aes_share_key']
        if 'aes_nonce' in kwargs:
            self.aes_nonce = kwargs['aes_nonce']

    def return_error(self, err_code, error_msg=None, status_code=400):
        # 前后端交互端报错，不需要加密给客户端
        self.request_tools.return_error(err_code, error_msg, status_code)

    @FormateOutput(default_value=10007, return_type='return_error')
    def init_session(self):
        conf = get_mysql_config()
        connect_string = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8mb4' % (conf['user'], conf['password'],
                                                                             conf['host'], conf['port'], conf['db'])
        self.engine = create_engine(connect_string)
        self.Session = sessionmaker()
        self.Session.configure(bind=self.engine)

    @contextmanager
    def session_scope(self):
        session = self.Session()
        try:
            yield session
        except InvalidUsageException as error:
            session.rollback()
            raise error
        except FundamentalErrorException as error:
            session.rollback()
            raise error
        except Exception as error:
            session.rollback()
            raise error
        finally:
            session.close()

    def check_mobile(self, user_mobile):
        if not check_mobile(user_mobile):
            self.return_error(30200)

    def check_mobile_all(self, user_mobile):
        if not check_mobile_all(user_mobile):
            self.return_error(30200)

    def check_email(self, email):
        if not check_email(email):
            self.return_error(30218)

    def get_user_key_nonce(self, user_type, user_id=None, request_type=_REQUEST_TYPE_LOGIN):
        share_key = _SHARE_KEY
        nonce = _NONCE
        if user_type == _USER_TYPE_NONE:
            pass
        elif user_type == _USER_TYPE_INNER:
            share_key = _INNER_SHARE_KEY
            nonce = _INNER_NONCE
        else:
            with self.session_scope() as session:
                key_salt = session.query(KeySaltModel).filter(KeySaltModel.user_id == user_id,
                                                              KeySaltModel.user_type == user_type,
                                                              KeySaltModel.deleted == False,
                                                              KeySaltModel.request_type == request_type,
                                                              ).first()
                if key_salt is not None:
                    share_key = key_salt.share_key
                    nonce = key_salt.nonce
        return share_key, nonce

    def return_aes_error(self, err_code, error_msg=None, status_code=200):
        # 业务逻辑报错，需要加密返回给客户端
        # self.aes_share_key, self.aes_nonce参数为空，则return_aes_error不加密，应用场景如服务端直接的通信
        self.request_tools.return_operate_error(err_code, error_msg, status_code, self.aes_share_key, self.aes_nonce)

    def check_source(self, register_by, user_source):
        allow_register_by = get_conf('register_by')
        if register_by not in allow_register_by:
            self.return_aes_error(30215)
        if user_source not in KeySaltModel.get_all_source_type():
            self.return_aes_error(30216)
        return True

    def send_aws_sms(self, mobile, vcode, template=None, mobile_country_code=None):
        aws_config = get_aws_config()
        if mobile_country_code is None:
            mobile = '+86' + str(mobile)
        else:
            mobile = str(mobile_country_code) + str(mobile)
        if template is None:
            send_message = '验证码为：' + str(vcode)
        else:
            send_message = str(template)

        send_result, response_message = send_aws_sms(
            aws_config['aws_access_key_id'],
            aws_config['aws_secret_access_key'],
            mobile,
            send_message
        )

        with self.session_scope() as session:
            q = SmsMessageModel(
                send_message=json.dumps({
                    'aws_access_key_id': aws_config['aws_access_key_id'],
                    'aws_secret_access_key': aws_config['aws_secret_access_key'],
                    'mobile': mobile,
                    'send_message': send_message,
                }),
                response_message=json.dumps(response_message),
                gateway='aws',
            )
            session.add(q)
            session.commit()
        if not send_result:
            # self.return_aes_error(30056)
            return False
        return True

    def get_nick_name(self, user_model, session=None):
        if session is None:
            with self.session_scope() as session:
                return self.__get_nick_name(user_model, session)
        else:
            return self.__get_nick_name(user_model, session)

    def __get_nick_name(self, user_model, session):
        while True:
            nick_name = get_random_str(k=8, except_list=['0'])
            one_user = self.__check_nick_name(user_model, nick_name, session)
            if not one_user:
                break
        return nick_name

    def check_nick_name(self, user_model, nick_name, session=None):
        if session is None:
            with self.session_scope() as session:
                return self.__check_nick_name(user_model, nick_name, session)
        else:
            return self.__check_nick_name(user_model, nick_name, session)

    def __check_nick_name(self, user_model, nick_name, session):
        user = session.query(user_model).filter(
            user_model.nick_name == nick_name,
            user_model.deleted == False,
        ).first()
        if user:
            return user
        else:
            return False

    def send_ZT_sms(self, mobile, vcode, template=None, mobile_country_code=None):
        # 发送国短信
        if mobile_country_code is not None and mobile_country_code not in ['+86', '0086']:
            return False
        zt_config = get_zt_config()
        user_name = zt_config['user_name']
        password = zt_config['password']
        send_url = zt_config['send_url']

        time_str = datetime.datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai')).strftime('%Y%m%d%H%M%S')
        send_password = encrypt_md5(encrypt_md5(password) + time_str)
        if template is None:
            send_message = '验证码为：' + str(vcode)
        else:
            send_message = str(template)
        request_data = {
                'username': user_name,
                'tkey': time_str,
                'password': send_password,
                'mobile': mobile,
                'content': send_message,
            }
        response_data = transfer_to_platform(
            send_url,
            data=request_data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            method="post",
            decode_type='str',
        )
        with self.session_scope() as session:
            q = SmsMessageModel(
                send_message=json.dumps({
                    'request_data': request_data,
                    'mobile': mobile,
                    'send_message': send_message,
                }),
                response_message=json.dumps(response_data),
                gateway='ZT',
            )
            session.add(q)
            session.commit()
        response_result = response_data.split(',')
        if response_result[0] == '1':
            return True
        else:
            return False

    def send_Intl_ZT_sms(self, mobile, vcode, template=None, mobile_country_code=None):
        # 发送国际短信
        # 去除区号的+和0
        mobile_country_code = mobile_country_code.replace('+', '')
        mobile_country_code = str(int(mobile_country_code))

        zt_config = get_intl_zt_config()
        user_name = zt_config['user_name']
        password = zt_config['password']
        send_url = zt_config['send_url']

        time_str = datetime.datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai')).strftime('%Y%m%d%H%M%S')
        send_password = encrypt_md5(encrypt_md5(password) + time_str)
        if template is None:
            send_message = '验证码为：' + str(vcode)
        else:
            send_message = str(template)
        request_data = {
                'username': user_name,
                'tkey': time_str,
                'password': send_password,
                'code': mobile_country_code,
                'mobile': mobile,
                'content': send_message,
            }
        response_data = transfer_to_platform(
            send_url,
            data=request_data,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            method="post",
            decode_type='str',
        )
        with self.session_scope() as session:
            q = SmsMessageModel(
                send_message=json.dumps({
                    'request_data': request_data,
                    'mobile': mobile,
                    'send_message': send_message,
                }),
                response_message=json.dumps(response_data),
                gateway='Intl_ZT',
            )
            session.add(q)
            session.commit()
        response_result = response_data.split(',')
        if response_result[0] == '1':
            return True
        else:
            return False

    def send_gateway_sms(self, mobile, vcode, template=None, mobile_country_code=None):
        import threading
        t = threading.Thread(target=self.__send_gateway_sms, args=(mobile, vcode, template, mobile_country_code,))
        t.start()
        return True

    def __send_gateway_sms(self, mobile, vcode, template=None, mobile_country_code=None):
        # 按照顺序尝试发送短信
        result = self.send_aws_sms(mobile, vcode, template=template, mobile_country_code=mobile_country_code)
        if result is True:
            return True
        if mobile_country_code is None:
            mobile_country_code = '+86'
        if mobile_country_code in ['+86', '0086']:
            result = self.send_ZT_sms(mobile, vcode, template=template, mobile_country_code=mobile_country_code)
            if result is True:
                return True
        else:
            result = self.send_Intl_ZT_sms(mobile, vcode, template=template, mobile_country_code=mobile_country_code)
            if result is True:
                return True
        with self.session_scope() as session:
            q = SmsMessageModel(
                send_message=json.dumps({
                    'mobile': mobile,
                    'vcode': vcode,
                    'template': template,
                    'mobile_country_code': mobile_country_code,
                }),
                response_message=json.dumps({}),
                gateway='send_fail',
            )
            session.add(q)
            session.commit()
        return False

    def send_mail(self, mail_body, user, pwd, to, subject, smtp_server, smtp_port):
        import threading
        t = threading.Thread(target=send_mail, args=(mail_body, user, pwd, to, subject, smtp_server, smtp_port,))
        t.start()
        return True


