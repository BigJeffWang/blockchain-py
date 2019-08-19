from log import raise_logger
from services.base_service import BaseService
import random
import datetime
import json
import uuid
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.profile import region_provider
from aliyun_sms import const
import redis_lock
from werkzeug.exceptions import HTTPException
import traceback
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from tools.redis_tools import RedisTools
from common_settings import *
from config import get_conf, get_sms_config
from models.invest_user_model import InvestUserModel
from models.borrow_user_model import BorrowUserModel


class VcodeService(BaseService):
    def __init__(self, *args, **kwargs):
        super(VcodeService, self).__init__(*args, **kwargs)

        self.vcode_picture_key = 'vcode:picture:'
        self.vcode_sms_key = 'vcode:sms:'
        self.vcode_sms_minute_limit_key = 'vcode:smslimit:'
        self.vcode_sms_day_limit_key = 'vcode:smsday:'

        self.sms_config = None
        self.acs_client = None
        self.sms_redis_second = 600  # 验证码的存储时间
        self.sms_redis_second_diff = 60  # 验证码过了多久可以更改

        self.sms_config = get_sms_config()
        # 注意：不要更改
        self.acs_client = AcsClient(const.ACCESS_KEY_ID, const.ACCESS_KEY_SECRET, self.sms_config['region'])
        region_provider.add_endpoint(self.sms_config['product_name'], self.sms_config['region'], self.sms_config['domain'])

    # 生成六位验证码
    def generate_verification_code(self, num=6):

        code_list = ''

        for i in range(num):
            # 生成一个0~9的随机数
            random_num = random.randint(0, 9)

            code_list = code_list + str(random_num)
        return code_list

    # 生成四位字母，数字混合编码
    def get_mix_vcode(self, num_num=3, upper_num=1, lowwer_num=2, except_zero=True, except_o_upper=True, except_o_lower=True):
        result_array = []
        i = 0
        while i < num_num:
            random_num = str(random.randint(0, 9))
            if except_zero and random_num == '0':
                i -= 1
            else:
                result_array.append(random_num)
            i += 1

        i = 0
        while i < lowwer_num:
            random_low_alpha = chr(random.randint(97, 122))
            if except_o_lower and except_o_lower =='o':
                i -= 1
            else:
                result_array.append(random_low_alpha)
            i += 1
        i = 0
        while i < upper_num:
            random_upper_alpha = chr(random.randint(65, 90))
            if except_o_upper and random_upper_alpha == 'O':
                i -= 1
            else:
                result_array.append(random_upper_alpha)
            i += 1
        random.shuffle(result_array)
        return ''.join(result_array)

    def get_random_color(self):
        '''
        获取一个随机颜色(r,g,b)格式的
        '''
        c1 = random.randint(0, 255)
        c2 = random.randint(0, 255)
        c3 = random.randint(0, 255)
        return (c1, c2, c3)

    def make_vcode_picture(self):
        width = 80
        height = 28
        image = Image.new('RGB', (width, height), self.get_random_picture_background())
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("./ttfs/KumoFont.ttf", size=18)
        vcode_str = self.get_mix_vcode()
        for i in range(len(vcode_str)):
            draw.text((5 + i * 12, 7), vcode_str[i], self.get_random_picture_string(), font=font)

        for i in range(2):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line((x1, y1, x2, y2), fill=self.get_random_picture_line())

        for i in range(6):
            draw.point([random.randint(0, width), random.randint(0, height)], fill=self.get_random_color())
            x = random.randint(0, width)
            y = random.randint(0, height)
            draw.arc((x, y, x + 4, y + 4), 0, 90, fill=self.get_random_picture_arc())

        img_file = BytesIO()
        image.save(img_file, 'JPEG')
        return img_file.getvalue(), vcode_str

    def set_vcode_picture(self, vcode_str, vcode_key='', vcode_type=_REQUEST_TYPE_REGISTER,
                          user_type=_USER_TYPE_INVEST):
        if vcode_key == '':
            redis_key = self.vcode_picture_key + str(vcode_type) + ':' + str(user_type) + ':' + str(vcode_str).lower()
        else:
            redis_key = self.vcode_picture_key + str(vcode_type) + ':' + str(user_type) + ':' + str(vcode_key)
        redis_tools = RedisTools()
        redis_tools.set(redis_key, vcode_str.lower(), ex=60)

    def check_vcode_picture(self, vcode_str, vcode_key='', vcode_type=_REQUEST_TYPE_REGISTER,
                          user_type=_USER_TYPE_INVEST):
        env = get_conf('env')
        if vcode_str == "111111" and env == 'dev':
            return True
        if vcode_key == '':
            redis_key = self.vcode_picture_key + str(vcode_type) + ':' + str(user_type) + ':' + str(vcode_str).lower()
        else:
            redis_key = self.vcode_picture_key + str(vcode_type) + ':' + str(user_type) + ':' + str(vcode_key)
        redis_tools = RedisTools()
        redis_result = redis_tools.get(redis_key)
        raise_logger('check vcode' + ' ' + str(redis_key))
        if redis_result is None:
            self.return_aes_error(30052)
        if str(redis_result, encoding='utf-8').lower() != str(vcode_str).lower():
            self.return_aes_error(30060)
        redis_tools.delete(redis_key)
        return True

    def get_random_picture_background(self):
        random.shuffle(_PICTURE_VCODE_BACKGROUND)
        one = _PICTURE_VCODE_BACKGROUND[0]
        return one

    def get_random_picture_string(self):
        random.shuffle(_PICTURE_VCODE_STRING)
        one = _PICTURE_VCODE_STRING[0]
        return one

    def get_random_picture_line(self):
        random.shuffle(_PICTURE_VCODE_LINE)
        one = _PICTURE_VCODE_LINE[0]
        return one

    def get_random_picture_arc(self):
        random.shuffle(_PICTURE_VCODE_ARC)
        one = _PICTURE_VCODE_ARC[0]
        return one

    def make_register_signature(self, num=128, save_time=180):
        one = random.randint(0, num - 2)
        num -= one
        two = random.randint(0, num - 1)
        num -= two

        redis_str = self.get_mix_vcode(one, two, num, except_zero=False, except_o_upper=False, except_o_lower=False)
        redis_tools = RedisTools()
        redis_tools.set(redis_str, 1, ex=save_time)
        return redis_str

    def check_register_signature(self, register_signature, direct_error=True):
        env = get_conf('env')
        if register_signature == "111111" and env == 'dev':
            return True
        redis_tools = RedisTools()
        if redis_tools.exists(register_signature):
            redis_tools.delete(register_signature)
            return True
        if direct_error:
            self.return_aes_error(30058)
        else:
            return False

    def send_vcode(self, code_type, mobile, user_type=_USER_TYPE_INVEST):
        self.check_mobile(mobile)
        with self.session_scope() as session:
            if user_type == _USER_TYPE_INVEST:
                userModel = InvestUserModel
                q = session.query(userModel).filter(userModel.user_mobile == mobile, userModel.deleted == False).first()
            elif user_type == _USER_TYPE_BORROW:
                userModel = BorrowUserModel
                q = session.query(userModel).filter(userModel.user_mobile == mobile, userModel.deleted == False).first()
            else:
                self.return_aes_error(10019)

            if code_type == _VCODE_REGISTER:
                if q is not None:
                    self.return_aes_error(30203)
            else:
                if q is None:
                    self.return_aes_error(30209)

        redis = RedisTools()
        env = get_conf("env")

        lock = redis_lock.Lock(redis.redis_conn, 'send_vcode', expire=1)
        try:
            if lock.acquire():
                vcode = self.generate_verification_code()
                delta = datetime.timedelta(seconds=self.sms_redis_second)

                #  发送验证码限制
                if env != 'dev':
                    self.send_vcode_limit(redis, mobile, code_type, user_type, minute_limit=self.sms_redis_second_diff)

                # 给第三方平台发送验证码
                redis_key = self.get_sms_key(mobile, code_type, user_type)
                # save_vcode = redis.get(redis_key)
                # if save_vcode is not None:
                #     self.return_aes_error(30055)

                # 发送验证码
                __business_id = uuid.uuid1()
                params = {"code": vcode}
                params_json = json.dumps(params)
                response = self.send_sms(__business_id, mobile, self.sms_config['sign_name'], self.sms_config['template_code'], params_json).decode('utf-8')
                response_dict = json.loads(response)
                if response_dict['Code'] != "OK":
                    raise_logger('sendsmsfail' + str(response_dict), 'rs_error')
                    self.return_aes_error(30056)

                raise_logger('smscode*' + redis_key + '*' + str(datetime.datetime.now() + delta))
                redis.set(redis_key, vcode, ex=delta)

                status = {
                    "status": "true"
                }
                lock.release()
                return status
        except HTTPException as e:
            raise e
        except Exception as err:
            exceptions = traceback.format_exc()
            if exceptions:
                exception_list = exceptions.split(':')
                if not exception_list[0] == 'NoneType':
                    for i in exception_list:
                        for j in i.split("\n"):
                            raise_logger(j, 'rs_error')
            self.return_aes_error(30057)

    def send_sms(self, business_id, phone_numbers, sign_name, template_code, template_param=None):
        smsRequest = SendSmsRequest.SendSmsRequest()
        # 申请的短信模板编码,必填
        smsRequest.set_TemplateCode(template_code)

        # 短信模板变量参数
        if template_param is not None:
            smsRequest.set_TemplateParam(template_param)

        # 设置业务请求流水号，必填。
        smsRequest.set_OutId(business_id)

        # 短信签名
        smsRequest.set_SignName(sign_name)

        # 数据提交方式
        # smsRequest.set_method(MT.POST)

        # 数据提交格式
        # smsRequest.set_accept_format(FT.JSON)

        # 短信发送的号码列表，必填。
        smsRequest.set_PhoneNumbers(phone_numbers)

        # 调用短信发送接口，返回json
        smsResponse = self.acs_client.do_action_with_exception(smsRequest)

        # TODO 业务处理

        return smsResponse

    '''
    发送验证码限制
    '''
    def send_vcode_limit(self, redis_tool, mobile, code_type, user_type, minute_limit=60, day_limit=5):
        minute_key = self.vcode_sms_minute_limit_key + str(code_type) + ':' + str(user_type) + ':' + str(mobile)
        minute_key_is_exist = redis_tool.redis_conn.exists(minute_key)
        if minute_key_is_exist:
            self.return_aes_error(30053)
        else:
            redis_tool.redis_conn.set(minute_key, 1, ex=minute_limit)

        day_key = self.vcode_sms_day_limit_key + str(code_type) + ':' + str(user_type) + ':' + str(mobile)
        day_key_is_exist = redis_tool.redis_conn.exists(day_key)
        if day_key_is_exist:
            # 校验 day_key 的 value 是否 大于 5
            if int(redis_tool.redis_conn.get(day_key)) > day_limit:
                # self.return_aes_error(30054)
                pass
            else:
                redis_tool.redis_conn.incr(day_key)
        else:
            redis_tool.redis_conn.set(day_key, 1, ex=86400)

        return True

    def get_sms_key(self, mobile, code_type, user_type):
        return self.vcode_sms_key + str(code_type) + ':' + str(user_type) + ':' + str(mobile)

    # 校验验证码
    def check_vcode(self, vcode, code_type, mobile, user_type=_USER_TYPE_INVEST, register_by=None, direct_return_error=True):
        if register_by in [_REGISTER_BY_MOBILE]:
            self.check_mobile_all(mobile)
        elif register_by in [_REGISTER_BY_EMAIL]:
            self.check_email(mobile)
        elif register_by in [
            _REGISTER_AUTHEN_MOBILE,
            _REGISTER_SET_PAYPD_MOBILE,
            _RESET_PWD_MOBILE,
            _REGISTER_AUTHEN_EMAIL,
            _REGISTER_SET_PAYPD_EMAIL,
            _RESET_PWD_EMAIL,
            _REGISTER_SET_EMAIL,
            _REGISTER_SET_MOBILE,
            _REGISTER_RESET_PAYPD_MOBILE,
            _REGISTER_RESET_PAYPD_EMAIL,
        ]:
            pass
        else:
            self.check_mobile(mobile)
        env = get_conf("env")
        if vcode == "111111" and env == 'dev':
            return True

        redis = RedisTools()
        redis_key = self.get_sms_key(mobile, code_type, user_type)
        check_result = redis.get(redis_key)
        if check_result:
            redis.delete(redis_key)
            return True
        else:
            if direct_return_error:
                self.return_aes_error(30059)
            else:
                return False

    def send_vcode_by_register_type(self, code_type, mobile, user_type=_USER_TYPE_INVEST, register_by=None,
                                    mobile_country_code=None, check_user_id=None):
        """
        发送不同类型的验证码
        :param code_type: 验证码种类
        :param mobile: 手机号
        :param user_type: 用户类别
        :param register_by: 操作种类，也用来区分发送验证码的路径为email或者mobile
        :param mobile_country_code: 手机号国家区号
        :param check_user_id: 被用来校验的userid，比如设置手机号时，需要校验userid是否正常且该userid下没有手机号
        :return:
        """
        if register_by in [_REGISTER_BY_MOBILE, _RESET_PWD_MOBILE, _REGISTER_SET_MOBILE]:
            self.check_mobile_all(mobile)
        elif register_by in [_REGISTER_BY_EMAIL, _RESET_PWD_EMAIL, _REGISTER_SET_EMAIL]:
            self.check_email(mobile)

        with self.session_scope() as session:
            if user_type == _USER_TYPE_INVEST:
                userModel = InvestUserModel
                if register_by in [_REGISTER_BY_MOBILE, _RESET_PWD_MOBILE]:
                    q = session.query(userModel).filter(
                        userModel.user_mobile == mobile,
                        userModel.mobile_country_code == mobile_country_code,
                        userModel.deleted == False,
                        userModel.status_on == userModel.status_on,
                    ).first()
                elif register_by in [_REGISTER_BY_EMAIL, _RESET_PWD_EMAIL]:
                    q = session.query(userModel).filter(
                        userModel.email == mobile,
                        userModel.deleted == False,
                        userModel.status_on == userModel.status_on,
                    ).first()
                elif register_by in [_REGISTER_AUTHEN_MOBILE, _REGISTER_SET_PAYPD_MOBILE, _REGISTER_RESET_PAYPD_MOBILE,
                                     _REGISTER_AUTHEN_EMAIL, _REGISTER_SET_PAYPD_EMAIL, _REGISTER_RESET_PAYPD_EMAIL]:

                    q = session.query(userModel).filter(
                        userModel.user_id == mobile,
                        userModel.deleted == False,
                        userModel.status_on == userModel.status_on,
                    ).first()
                elif register_by in [_REGISTER_SET_MOBILE]:
                    q = session.query(userModel).filter(
                        userModel.user_id == check_user_id,
                        userModel.deleted == False,
                        userModel.status_on == userModel.status_on,
                    ).first()
                    if q is not None and q.user_id != q.user_mobile:
                        self.return_aes_error(30237)
                elif register_by in [_REGISTER_SET_EMAIL]:
                    q = session.query(userModel).filter(
                        userModel.user_id == check_user_id,
                        userModel.deleted == False,
                        userModel.status_on == userModel.status_on,
                    ).first()
                    if q is not None and q.user_id != q.email:
                        self.return_aes_error(30238)
                else:
                    self.return_aes_error(10019)
            else:
                self.return_aes_error(10019)

            if code_type == _VCODE_REGISTER:
                if q is not None:
                    self.return_aes_error(30203)
            else:
                if q is None:
                    self.return_aes_error(30209)
                if register_by in [
                    _REGISTER_AUTHEN_MOBILE,
                    _REGISTER_AUTHEN_EMAIL,
                ] and q.authentication_status != userModel.authentication_status_on:
                    self.return_aes_error(10019)

        redis = RedisTools()
        env = get_conf("env")

        lock = redis_lock.Lock(redis.redis_conn, 'send_vcode', expire=60)
        try:
            if lock.acquire():
                vcode = self.generate_verification_code()
                delta = datetime.timedelta(seconds=self.sms_redis_second)

                #  发送验证码限制
                if env != 'dev':
                    self.send_vcode_limit(redis, mobile, code_type, user_type, minute_limit=self.sms_redis_second_diff)

                # 给第三方平台发送验证码
                if code_type in [_VCODE_SET_EMAIL, _VCODE_SET_MOBILE]:
                    redis_key = self.get_sms_key(q.user_id, code_type, user_type)
                else:
                    redis_key = self.get_sms_key(mobile, code_type, user_type)
                # save_vcode = redis.get(redis_key)
                # if save_vcode is not None:
                #     lock.release()
                #     self.return_aes_error(30055)

                # 发送验证码
                if register_by == _REGISTER_BY_MOBILE:
                    # __business_id = uuid.uuid1()
                    # params = {"code": vcode}
                    # params_json = json.dumps(params)
                    # response = self.send_sms(__business_id, mobile, self.sms_config['sign_name'], self.sms_config['template_code'], params_json).decode('utf-8')
                    # response_dict = json.loads(response)
                    # if response_dict['Code'] != "OK":
                    #     raise_logger('sendsmsfail' + str(response_dict), 'rs_error')
                    #     self.return_aes_error(30056)
                    self.send_gateway_sms(
                        mobile,
                        vcode,
                        mobile_country_code=mobile_country_code,
                        template='【LuckyPark】您的验证码是：' + str(vcode) + '。您正在进行［注册］，有效时间10分钟，请尽快完成注册。请勿泄露。'
                    )
                elif register_by == _REGISTER_BY_EMAIL:
                    email_config = get_conf('email')
                    subject = '注册LuckyPark'
                    self.send_mail(
                        '您好：您的验证码是：' + str(vcode) + '。您正在进行［注册］，有效时间10分钟，请尽快完成注册。请勿泄露。【LuckyPark】',
                        # vcode,
                        email_config['user'],
                        email_config['pwd'],
                        mobile, subject,
                        email_config['smtp_server'],
                        email_config['smtp_port']
                    )
                elif register_by in [
                    _REGISTER_AUTHEN_MOBILE,
                ]:
                    # __business_id = uuid.uuid1()
                    # params = {"code": vcode}
                    # params_json = json.dumps(params)
                    # response = self.send_sms(__business_id, q.user_mobile, self.sms_config['sign_name'], self.sms_config['template_code'], params_json).decode('utf-8')
                    # response_dict = json.loads(response)
                    # if response_dict['Code'] != "OK":
                    #     raise_logger('sendsmsfail' + str(response_dict), 'rs_error')
                    #     self.return_aes_error(30056)
                    self.send_gateway_sms(
                        mobile,
                        vcode,
                        mobile_country_code=mobile_country_code
                    )
                elif register_by in [
                    _REGISTER_SET_PAYPD_MOBILE,
                    _REGISTER_RESET_PAYPD_MOBILE,
                ]:
                    self.send_gateway_sms(
                        q.user_mobile,
                        vcode,
                        mobile_country_code=q.mobile_country_code,
                        template='【LuckyPark】您的验证码是：' + str(vcode) + '。您正在进行［设置交易密码］，有效时间10分钟。若非您本人操作，请立即修改登录密码。请勿泄露'
                    )
                elif register_by in [
                    _RESET_PWD_MOBILE,
                ]:
                    self.send_gateway_sms(
                        mobile,
                        vcode,
                        mobile_country_code=mobile_country_code,
                        template='【LuckyPark】您的验证码是：' + str(vcode) + '。您正在进行［重置密码］，有效时间10分钟。若非您本人操作，请立即修改登录密码。请勿泄露'
                    )
                elif register_by in [
                    _REGISTER_AUTHEN_EMAIL,
                ]:
                    email_config = get_conf('email')
                    subject = '验证码'
                    self.send_mail(vcode, email_config['user'], email_config['pwd'], q.email, subject, email_config['smtp_server'], email_config['smtp_port'])
                elif register_by in [
                    _REGISTER_SET_PAYPD_EMAIL,
                    _REGISTER_RESET_PAYPD_EMAIL,
                ]:
                    email_config = get_conf('email')
                    subject = 'LuckyPark设置交易密码'
                    self.send_mail(
                        '您好：您的验证码是：' + str(vcode) + '。您正在进行［设置交易密码］，有效时间10分钟。若非您本人操作，请立即修改登录密码。请勿泄露。【LuckyPark】',
                        # vcode,
                        email_config['user'],
                        email_config['pwd'],
                        q.email, subject,
                        email_config['smtp_server'],
                        email_config['smtp_port']
                    )
                elif register_by in [
                    _RESET_PWD_EMAIL,
                ]:
                    email_config = get_conf('email')
                    subject = 'LuckyPark忘记密码'
                    self.send_mail(
                        '您好：您的验证码是：' + str(vcode) + '。您正在进行［重置密码］，有效时间10分钟。若非您本人操作，请立即修改登录密码。请勿泄露。【LuckyPark】',
                        # vcode,
                        email_config['user'],
                        email_config['pwd'],
                        q.email, subject,
                        email_config['smtp_server'],
                        email_config['smtp_port']
                    )
                elif register_by in [
                    _REGISTER_SET_MOBILE,
                ]:
                    # __business_id = uuid.uuid1()
                    # params = {"code": vcode}
                    # params_json = json.dumps(params)
                    # response = self.send_sms(__business_id, mobile, self.sms_config['sign_name'], self.sms_config['template_code'], params_json).decode('utf-8')
                    # response_dict = json.loads(response)
                    # if response_dict['Code'] != "OK":
                    #     raise_logger('sendsmsfail' + str(response_dict), 'rs_error')
                    #     self.return_aes_error(30056)
                    self.send_gateway_sms(
                        mobile,
                        vcode,
                        mobile_country_code=mobile_country_code,
                        template='【LuckyPark】您的验证码是：' + str(vcode) + '。您正在进行［绑定手机号］，有效时间10分钟。若非您本人操作，请立即修改登录密码。请勿泄露'
                    )
                elif register_by in [
                    _REGISTER_SET_EMAIL,
                ]:
                    email_config = get_conf('email')
                    subject = 'LuckyPark邮箱绑定'
                    self.send_mail(
                        '您好：您的验证码是：' + str(vcode) + '。您正在进行［绑定邮箱］，有效时间10分钟。请尽快完成绑定。请勿泄露。【LuckyPark】',
                        # vcode,
                        email_config['user'],
                        email_config['pwd'],
                        mobile,
                        subject,
                        email_config['smtp_server'],
                        email_config['smtp_port']
                    )
                else:
                    lock.release()
                    self.return_aes_error(10040)

                raise_logger('smscode*' + redis_key + '*' + str(datetime.datetime.now() + delta))
                redis.set(redis_key, vcode, ex=delta)

                status = {
                    "status": "true"
                }
                lock.release()
                return status
        except HTTPException as e:
            raise e
        except Exception as err:
            exceptions = traceback.format_exc()
            if exceptions:
                exception_list = exceptions.split(':')
                if not exception_list[0] == 'NoneType':
                    for i in exception_list:
                        for j in i.split("\n"):
                            raise_logger(j, 'rs_error')
            self.return_aes_error(30057)





