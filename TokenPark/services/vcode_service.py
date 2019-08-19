from services.base_service import BaseService
from config import get_sms_email
from tools.redis_tools import RedisTools
import redis_lock
from werkzeug.exceptions import HTTPException
import traceback
from utils.log import raise_logger
import string
import random
from utils.util import send_mail


class VcodeService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send_vcode_by_email(self, vcode_key):
        email_config = get_sms_email(vcode_key)
        if email_config == {}:
            self.return_error(35034)
        redis = RedisTools()
        lock = redis_lock.Lock(redis.redis_conn, 'send_vcode', expire=60)
        try:
            if lock.acquire():
                vcode = self.generate_verification_code()

                # 发送验证码
                send_email_config = get_sms_email("send_email_config")
                subject = email_config['email_subject']
                send_mail(vcode, send_email_config['user'], send_email_config['pwd'], email_config['email'], subject,
                          send_email_config['smtp_server'], send_email_config['smtp_port'])

                redis_key = self.get_sms_email_key(email_config['redis_key'], vcode)
                redis.set(redis_key, vcode, ex=email_config['redis_second'])

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
                            raise_logger(j, 'rs', 'error')
            self.return_error(30035)

    # 0-9的数字 ＋26位英文大小写。展示八位
    def generate_verification_code(self, num=8):
        item_lab = string.ascii_letters + string.digits
        return ''.join(random.sample(item_lab, num))

    def get_sms_email_key(self, vcode_key, vcode):
        return 'sms:email:' + str(vcode_key) + ':' + str(vcode)

    def check_sms_email_vcode(self, vcode_key, vcode):
        email_config = get_sms_email(vcode_key)
        if email_config == {}:
            self.return_error(35034)
        redis = RedisTools()
        redis_key = self.get_sms_email_key(email_config['redis_key'], vcode)
        redis_value = redis.get(redis_key)
        if not redis_value:
            self.return_error(30036)
        if str(redis_value, encoding='utf-8') != str(vcode):
            self.return_error(30036)
        redis.delete(redis_key)
        return True



