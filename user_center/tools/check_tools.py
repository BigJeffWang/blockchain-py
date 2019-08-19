from flask import request
from config import get_whitelist_config, get_conf, get_transfer_platform_ip
from tools.redis_tools import RedisTools
from utils import generate_str
from common_settings import _USER_TYPE_ADMIN_LEAVEL_PURCHASE, _USER_TYPE_ADMIN_LEAVEL_RISK, \
    _USER_TYPE_ADMIN_LEAVEL_FINANCE, _USER_TYPE_ADMIN_LEAVEL_MANAGE, _PLATFORM_ALLOW_LEVEL, \
    _ROOT_ADMIN_LEVEL, _BASE_ADMIN_LEVEL


def check_bg_ip(control_key='all'):
    result = False
    ip = request.remote_addr
    white_list = get_whitelist_config()[control_key]
    ip_list = ip.split(".")
    maybe_list = []

    if len(ip_list) == 4:
        tmp = ''
        for i in range(len(ip_list)):
            if tmp == '':
                tmp += ip_list[i]
            else:
                tmp += '.' + ip_list[i]
            one_ip = tmp
            for j in range(3 - i):
                one_ip += '.' + '*'
            maybe_list.append(one_ip)
    maybe_list.append('*.*.*.*')

    if maybe_list != []:
        for i in maybe_list:
            if isinstance(white_list, str):
                if i == white_list:
                    result = True
                    break
            elif isinstance(white_list, list):
                if i in white_list:
                    result = True
                    break

    return result


def check_transfer_platform_ip():
    result = False
    ip = request.remote_addr
    white_list = get_transfer_platform_ip()
    ip_list = ip.split(".")
    maybe_list = []

    if len(ip_list) == 4:
        tmp = ''
        for i in range(len(ip_list)):
            if tmp == '':
                tmp += ip_list[i]
            else:
                tmp += '.' + ip_list[i]
            one_ip = tmp
            for j in range(3 - i):
                one_ip += '.' + '*'
            maybe_list.append(one_ip)
    maybe_list.append(['*.*.*.*'])

    if maybe_list != []:
        for i in maybe_list:
            if isinstance(white_list, str):
                if i == white_list:
                    result = True
                    break
            elif isinstance(white_list, list):
                if i in white_list:
                    result = True
                    break

    return result


def check_authentication(code):
    env = get_conf('env')
    if env == 'dev' and code == '111111':
        return True
    result = False
    redis_tool = RedisTools()
    authentication_value = str(redis_tool.get('authentication'), encoding='utf8')
    if authentication_value == code:
        result = True
    authentication_value = generate_str()
    redis_tool.set('authentication', authentication_value)
    return result


def check_admin_user_level(level):
    # 根据level值，查看是否符合要求
    if level not in [_USER_TYPE_ADMIN_LEAVEL_PURCHASE, _USER_TYPE_ADMIN_LEAVEL_RISK, _USER_TYPE_ADMIN_LEAVEL_FINANCE,
                     _USER_TYPE_ADMIN_LEAVEL_MANAGE]:
        return False
    return True


def check_admin_user_level_by_byte(level, platform_level_list):
    """
    二进制码，确认用户的权限，只要有一个权限不符合，则返回false
    :param level: 用户的权限
    :param platform_level_list: 所需level的列表
    :return:
    """
    for i in platform_level_list:
        if i & level == 0:
            return False
    return True


def check_admin_user_platform_level(level):
    check_list = []
    for i in _PLATFORM_ALLOW_LEVEL:
        tmp = 0
        for j in i:
            tmp += j
        check_list.append(tmp)
    if int(level) in check_list:
        return True
    return False


def check_admin_user_platform_level_new(level):
    if int(level) not in [_ROOT_ADMIN_LEVEL, _BASE_ADMIN_LEVEL]:
        return False
    return True




