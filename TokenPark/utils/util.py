import binascii
import datetime
import decimal
import json
import math
import random
import smtplib
import string
import boto3
from email.header import Header
from email.mime.text import MIMEText
import urllib
from urllib import parse, request

import requests
from bitcoinrpc.authproxy import AuthServiceProxy

from config import get_config, get_env
from utils.time_util import get_datetime_from_str
from common_settings import *


def recursive_dict_args(dicts, key_list, func, *args):
    """
    根据传入条件和方法递归遍历字典,改造参数
    :param dicts:
    :param key_list:
    :param func:
    :param args:
    :return:
    """
    if not isinstance(dicts, dict):
        return dicts
    for k, v in dicts.items():
        if k in key_list:
            dicts[k] = func(v, *args)
        if isinstance(v, dict):
            dicts[k] = recursive_dict_args(v, key_list, func, *args)
        if isinstance(v, list):
            tmp_list = []
            for index, l_v in enumerate(v):
                if isinstance(l_v, dict):
                    tmp_list.append(recursive_dict_args(l_v, key_list, func, *args))
                else:
                    tmp_list.append(l_v)
            dicts[k] = tmp_list
    return dicts


def time_transform_from_zone(cli_time, timezone):
    """
    根据参数timezone时区,把客户端时间,转换成utc服务器时间
    :param cli_time: 客户端时间 %m/%d/%Y or %Y-%m-%d 选填 %H:%M:%S 会补全
    :param timezone: 时区 0,1~12,-1~-12
    :return:
    """
    zero_time = "0000-00-00 00:00:00"
    if cli_time == zero_time:
        return cli_time
    if len(cli_time) < len(zero_time):
        cli_time += zero_time[len(cli_time) - len(zero_time):]
    time_tuple = get_datetime_from_str(cli_time)
    if not time_tuple:
        return ""
    utc_time = (time_tuple + datetime.timedelta(hours=-timezone)).strftime('%Y-%m-%d %H:%M:%S')
    return utc_time


def format_utc(utc_time):
    """
    默认把服务器数据库UTC时间转换为东八区时间,临时解决
    :param utc_time:
    :return:
    """
    if utc_time == "0000-00-00 00:00:00":
        return utc_time
    utc_time_tuple = get_datetime_from_str(utc_time)
    bj_time = (utc_time_tuple + datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    return bj_time


def format_zone8(utc_time):
    """
    默认把东八区时间转换为服务器数据库UTC时间,临时解决
    :param utc_time:
    :return:
    """
    utc_time_tuple = get_datetime_from_str(utc_time)
    utc_time = (utc_time_tuple - datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    return utc_time


def format_str(data):
    """
    转字符串小数点 补零
    :param data:
    :return:
    """
    s = str(data)
    if "e" or "E" in s:
        s = s.lower()
        e_index = s.find("e")
        prefix_str = s[:e_index]
        point_count = 0
        if "." in prefix_str:
            point_count = prefix_str.find(".")
            prefix_str = prefix_str.replace(".", "")
        if s[e_index + 1] in ["-", "+"]:
            multiple = int(s[e_index + 2:]) - point_count
            if s[e_index + 1] == "-":
                suffix_str = "0." + "0" * multiple
                return suffix_str + prefix_str
            elif s[e_index + 1] == "+":
                suffix_str = "0" * multiple
                return prefix_str + suffix_str
            else:
                return s
    return s


def get_decimal(data, digits=4, decimal_type="down"):
    if decimal_type.lower() == "up":
        round_type = decimal.ROUND_UP
    elif decimal_type.lower() == "round":
        round_type = decimal.ROUND_HALF_EVEN
    else:
        round_type = decimal.ROUND_DOWN

    if not data:
        data = "0"

    if not isinstance(data, str):
        data = str(data)

    decimal_template = "0." + "0" * digits
    return decimal.Decimal(data).quantize(decimal.Decimal(decimal_template), round_type)


def decimal_to_client(data, digits=8, decimal_type="down"):
    """
    将decimal数据格式化为客户端所需的格式
    :param data:
    :param digits:
    :param decimal_type:
    :return:
    """
    return format(get_decimal(data, digits, decimal_type), "f")


def decimal_to_str(data, digits=18, decimal_type="down"):
    """
    将decimal数据格式化为后台所需的格式,默认为小数点后17位 对应 decimal(21,18)的转换
    data 可以是字符串, 也可以是 decimal 类型
    :param data:
    :param digits:
    :param decimal_type:
    :return:
    """
    return format(get_decimal(data, digits, decimal_type), "f")


def decimal_two_up(n):
    # 保留两位小数向上取
    return get_decimal(n, 2, "up")


def decimal_two_down(n):
    # 保留两位小数向下取
    return get_decimal(n, 2, "down")


def decimal_two(n):
    # 保留两位小数四舍五入
    return get_decimal(n, 2, "round")


def generate_order_no(k=12):
    """
    生成订单号 20位时间 12位随机数字
    :return:
    """
    order_no = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f') + "".join(random.choices(string.digits, k=k))
    return order_no


# 必填校验+去空格
def check_empty(data):
    if data == None:
        return False
    data = data.replace(" ", "")
    if data == "":
        return False
    return data


# 去空格(适用于非必填字段)
def remove_space(data):
    if data == None:
        return ""
    data = data.replace(" ", "")
    return data


def do_get(url, textmod={}):
    textmod = parse.urlencode(textmod)
    header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'}
    req = request.Request(url='%s%s%s' % (url, '?', textmod), headers=header_dict)
    res = request.urlopen(req)
    res = res.read()
    return json.loads(res.decode(encoding='utf-8'))


def do_post(url, params):
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.3'
                       '6 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'
                       ),
    }
    postdata = urllib.parse.urlencode(params)
    try:
        response = requests.post(url, postdata, headers=headers, timeout=3600)
        if response.status_code == 200:
            return response.json()
        else:
            return
    except Exception as e:
        raise ConnectionError("httpGet failed, detail is:%s" % e)


# 创建bitcoind rpc连接
def btc_rpc_client():
    # rpc_connection = AuthServiceProxy(
    #         "http://%s:%s@127.0.0.1:18332" % ("RPCuser", "RPCpasswd"))
    conf = get_config()
    env = conf["env"]
    # url = conf["node_url"]["btc"][env]["lan_url"]
    url = conf["node_url"]["btc"][env]["inter_url"]
    rpc_connection = AuthServiceProxy(
        "http://%s:%s@%s:18332" % ("RPCuser", "RPCpasswd", url))
    return rpc_connection


def eth_rpc_client():
    rpc_connection = "http://" + get_config()["node_url"]["eth"][get_env()]["inter_url"] + ":8545"
    return rpc_connection


def get_offset_by_page(page_num, page_limit):
    """
    根据前端传的页数，返回mysql所需的offset
    :param page_num: 页数
    :param page_limit: 每页条数
    :return: mysql 的 offset
    """
    page_num = int(page_num)
    page_limit = int(page_limit)
    if page_num < 1:
        return '0'
    return str((page_num - 1) * page_limit)


def get_page_by_offset(offset_num, page_limit):
    """
    根据数据条数，返回对应页数
    :param offset_num: 数据条数
    :param page_limit: 每页条数
    :return: 页数
    """
    offset_num = int(offset_num)
    page_limit = int(page_limit)
    if offset_num <= 0:
        return 0
    return str(math.ceil(offset_num / page_limit))


def str_to_bytes(s):
    return bytes(s, encoding="utf8")


def str_to_hexbytes(s):
    return binascii.unhexlify(s.encode("utf-8"))


def hexbytes_to_str(h):
    return binascii.hexlify(h).decode('utf-8')


def get_now_time():
    return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


# 求最大公约数
def hcf(x, y):
    """该函数返回两个数的最大公约数"""

    # 获取最小值
    if x > y:
        smaller = y
    else:
        smaller = x

    for i in range(1, smaller + 1):
        if (x % i == 0) and (y % i == 0):
            hc = i

    return hc


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


def send_aws_sms_util(aws_access_key_id, aws_secret_access_key, phone_number, message, region_name=None):
    if region_name is None:
        region_name_list = [
            'ap-northeast-1',
            'ap-southeast-1',
            'ap-southeast-2',
            'eu-west-1',
            'us-east-1',
            'us-west-2',
        ]
        region_name = random.sample(region_name_list, 1)[0]
    sns = boto3.client('sns', region_name=region_name, aws_access_key_id=aws_access_key_id,
                       aws_secret_access_key=aws_secret_access_key)
    result = sns.publish(
        PhoneNumber=phone_number,
        Message=message,
    )
    if isinstance(result, dict) and 'ResponseMetadata' in result and 'HTTPStatusCode' in result['ResponseMetadata'] and \
            result['ResponseMetadata']['HTTPStatusCode'] == 200:
        result['region_name'] = region_name
        return True, result
    else:
        result['region_name'] = region_name
        return False, result


def send_aws_sms(mobile, content):
    mobile = '+86' + str(mobile)
    try:
        send_result, response_message = send_aws_sms_util(
            "AKIAJKPANAS5WEWGGGIQ",
            "LDustc/uU3HGv9l/Mpxxs7yP6pnKnLwNgerWb/hu",
            mobile,
            content
        )
    except Exception as e:
        response_message = {
            'send_fail': str(e)
        }
        send_result = False
    if not send_result:
        return False
    return True


def coin_id_to_name(coin_id):
    coin_name = ""
    if coin_id == _COIN_ID_BTC:
        coin_name = "BTC"
    elif coin_id == _COIN_ID_ETH:
        coin_name = "ETH"
    elif coin_id == _COIN_ID_EOS:
        coin_name = "EOS"
    return coin_name


def get_intranet_IP():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    return ip


if __name__ == "__main__":
    pass
