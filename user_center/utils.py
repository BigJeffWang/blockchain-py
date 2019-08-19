"""
-------------------------------------------------
   File Name：     utils
   Description:
   Author:        Zyt
   Date：          2018/7/26
-------------------------------------------------
"""

from config import get_conf
import os
import sys
import binascii
import datetime
import time
import random
import string
from crypto_utils import sha256_hex
from email.mime.text import MIMEText
from email.header import Header
import smtplib
import re


def detect_file(find_file_name, dir_path=None):
    """
    在项目目录下,递归查找文件,找到返回一个字典{"root":"/test", "file":"/test/t.py"},未找到返回FALSE
    :param dir_path: 默认为空时在项目主目录下查找,否则在dir_path目录下查找,dir_path必须是系统真实路径,不能是相对路径
    :param find_file_name: 要查找的文件名,需要带后缀
    :return:
    """
    if not dir_path:
        server_name = get_conf('bases')['server_name']
        real_path = os.path.realpath(__file__)
        file_index = real_path.rfind(server_name)
        dir_path = os.path.abspath(os.path.join(real_path[:file_index], server_name))
    for root, dirs, files in os.walk(dir_path):
        if find_file_name in files:
            return dict(root=root, file=os.path.abspath(os.path.join(root, find_file_name)))

    return False


def detect_python_path(find_file_name):
    """
    检测文件是否在Python环境变量里,如果存在返回这个文件的真实完整路径,否则加载到系统环境变量里
    :param find_file_name: 文件名 "logging.json"
    :return:
    """
    for iter_path in sys.path:
        iter_root, iter_file = os.path.split(iter_path)
        if find_file_name == iter_file:
            return iter_path

    res = detect_file(find_file_name)
    if not res:
        raise Exception("File does not exist")
    real_name = res["file"]
    sys.path.append(real_name)
    return real_name


def formate_args(args, format_str=False, format_keys=True, format_eval=True):
    """
    参数格式化
    :param args: 参数字典
    :param format_str: 是否需要把所有int类型,强转成字符串
    :param format_eval: 是否开启 把字符串 '["a","b"]' '{"a":1,"b":"1"}' 强转回list dict
    :param format_keys: 是否开启 把key的值 转为全小写
    :return:
    """
    tmp = {}
    for key, value in args.items():
        if format_eval and isinstance(value, str) and value:
            if value[0] in ("[", "{", "(") and value[-1] in ("]", "}", ")"):
                value = eval(value)
        if format_keys:
            key_lower = key.lower()
        else:
            key_lower = key
        if format_str:
            if isinstance(value, (int, float)):
                value = str(value)
        tmp[key_lower] = value
    # formated_args = dict(filter(lambda x: x[1] != '', tmp.items()))
    return tmp


def n_day_ago(date=None, n=0):
    if not date:
        date = datetime.date.today()
    day = date - datetime.timedelta(days=n)
    return day


def str_to_hex(s):
    return "0x" + s.encode('utf-8').hex()


def bytes_to_str(b):
    return b.decode("utf8")


def str_to_bytes(s):
    return bytes(s, encoding="utf8")


def hexbytes_to_str(h):
    return binascii.hexlify(h).decode('utf-8')


def str_to_hexbytes(s):
    return binascii.unhexlify(s.encode("utf-8"))


def generate_str(k=32):
    """
    符合base58 去除 0 (零), O (大写字母O), I (大写的字母i) and l (小写的字母L)
    :param k:
    :return:
    """
    ascii_lowercase = random.choices(string.ascii_lowercase.replace("l", "x"), k=k // 3)
    ascii_uppercase = random.choices(string.ascii_uppercase.replace("O", "X").replace("I", "X"), k=k // 3)
    digits = random.choices(string.digits.replace("0", "1"), k=k // 3 + k % 3)
    l = ascii_lowercase + ascii_uppercase + digits
    random.shuffle(l)
    return "".join(l).capitalize()


def get_random_str(k=8, except_list=[]):
    item_lab = string.ascii_letters + string.digits
    for i in except_list:
        item_lab.replace(i, '')
    ran_str = ''.join(random.sample(item_lab, k))
    return ran_str


def generate_num(k=16):
    """
    生成随机数的字符串
    :param k:
    :return:
    """
    return "".join(random.choices(string.digits, k=k))


def generate_time_str(k=None, h=None):
    """
    生成时间的20位字符串 日期8位 时间6位 毫秒6位
    :param h: 从末尾截取
    :param k: 从头部截取
    :return:
    """
    time_str = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')

    return time_str[h:k]


def generate_order_no(k=12):
    """
    生成订单号 20位时间 12位随机数字
    :return:
    """
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + "".join(random.choices(string.digits, k=k))


def merchantname_to_merchantno(merchant_name):
    """
    商户名称 对应返回 商户号
    :param merchant_name:
    :return:
    """
    merchant_no_dict = {
        "licaifan": "M211732929910428",
    }
    if merchant_name not in merchant_no_dict:
        return False
    return merchant_no_dict[merchant_name]


def get_sign(merchant_no, order_no, timestamp, constant="sparkchain"):
    """

    :param merchant_no:
    :param order_no:
    :param timestamp:
    :param constant:
    :return:
    """
    return sha256_hex(constant+merchant_no+order_no+timestamp)


def get_timestamp():
    return int(time.time())


def send_mail(mail_body, user, pwd, to, subject, smtp_server, smtp_port):
    """
    Need to config mq_config["email_to"],to define the receiver
    :param msg:
    :return:
    """
    _user = user
    _pwd = pwd
    # _to = to
    _to = [to]
    _subject = subject
    _smtp_server = smtp_server
    _smtp_port = smtp_port

    msg = MIMEText(mail_body, 'html', 'utf-8')

    msg['Subject'] = Header(_subject, "utf-8")
    msg["From"] = _user
    # msg["To"] = Header(",".join(_to), 'utf-8')
    msg["To"] = Header(",".join(_to))

    s = smtplib.SMTP_SSL(_smtp_server, _smtp_port)
    s.login(_user, _pwd)
    s.sendmail(_user, _to, msg.as_string())
    s.quit()


def check_mobile(user_mobile):
    regexp = r"^(1)\d{10}$"
    return check_regexp(regexp, user_mobile)


def check_mobile_all(user_mobile):
    regexp = r"^\d{11}$"
    return check_regexp(regexp, user_mobile)


def check_email(email):
    regexp = r'^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
    return check_regexp(regexp, email)


def check_regexp(regexp, check_str):
    return re.match(regexp, check_str)


if __name__ == "__main__":
    pass
