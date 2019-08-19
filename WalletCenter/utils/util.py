import binascii
import decimal
import datetime
import random
import string
import urllib
import requests
from urllib import parse, request
import json
from sqlalchemy import false, true


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
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + "".join(random.choices(string.digits, k=k))


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


def do_post(url, params=None, headers=None):
    if not headers:
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.3'
                           '6 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36'
                           ),
        }
    try:
        if params:
            postdata = urllib.parse.urlencode(params)
        else:
            postdata = params
        response = requests.post(url, postdata, headers=headers, timeout=3600)
        if response.status_code == 200:
            return response.json()
        else:
            return
    except Exception as e:
        raise ConnectionError("HTTP POST failed, detail is:%s" % e)


def to_int(data):
    """
    强转字符串,如果是str,就转int
    :param data:
    :return:
    """
    if isinstance(data, str):
        data = int(data)
    return data


def check_string_null(s):
    if s.strip() == '':
        return true

    return false


def get_str_from_list(data):
    ret = ""
    if isinstance(data, list):
        for item in data:
            ret += str(item) + ","
        return "[" + ret[:-1] + "]"
    return ret


def hexbytes_to_str(h):
    return binascii.hexlify(h).decode('utf-8')
