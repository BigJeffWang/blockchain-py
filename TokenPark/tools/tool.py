import datetime
import os
import re
import decimal
from sqlalchemy import false, true
from config import get_bases_conf, replace_path_based_system
from utils.util import decimal_to_client


def get_file_path(file_name, relative_path="./"):
    """

    :param file_name: 文件名 全名带后缀
    :param relative_path: 相对路径, 默认参数是项目下的根路径 比如 RongHaoChe/tools/tool.py, relative_path="tools/"
    :return:
    """
    root_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    file_path = os.path.join(root_path, relative_path, file_name)
    if not os.path.isfile(file_path):
        raise Exception("func get_file_path => No such file or directory: " + file_path)
    return file_path


def super_json_dumps(data, microsecond_digits=3):
    """
    自封装 超级 json.dumps,可以解析多维字典,不丢失float .00 精度, 冒号逗号后边 无空格, 可以解析中文
    :param data:
    :param microsecond_digits:
    :return:
    """
    if isinstance(data, dict):
        tmp_dict = '{'
        for k, v in data.items():
            tmp_dict += '"%s":' % k
            tmp_dict += super_json_dumps(v) + ","
        if tmp_dict[-1] == ",":
            tmp_dict = tmp_dict[:-1]
        tmp_dict += '}'
        return tmp_dict
    elif isinstance(data, list):
        tmp_list = '['
        for item in data:
            tmp_list += super_json_dumps(item) + ","
        if tmp_list[-1] == ",":
            tmp_list = tmp_list[:-1]
        tmp_list += ']'
        return tmp_list
    else:
        if isinstance(data, float):
            tmp_str = "%." + str(microsecond_digits) + "f" % data
        elif isinstance(data, int):
            tmp_str = "%s" % data
        else:
            tmp_str = '"%s"' % data
        return tmp_str


def detect_file(find_file_name, dir_path=None):
    """
    在项目目录下,递归查找文件,找到返回一个字典{"root":"/test", "file":"/test/t.py"},未找到返回FALSE
    :param dir_path: 默认为空时在项目主目录下查找,否则在dir_path目录下查找,dir_path必须是系统真实路径,不能是相对路径
    :param find_file_name: 要查找的文件名,需要带后缀
    :return:
    """
    import os
    if not dir_path:
        server_name = get_bases_conf()["server"]["name"]
        real_path = os.path.realpath(__file__)
        file_index = real_path.rfind(server_name)
        dir_path = os.path.abspath(os.path.join(real_path[:file_index], server_name))
        dir_path = replace_path_based_system(dir_path)
    for root, dirs, files in os.walk(dir_path):
        if find_file_name in files:
            return dict(server_path=dir_path, root=root, file=os.path.abspath(os.path.join(root, find_file_name)))
    raise Exception("The file was not found %s" % find_file_name)


def formate_args(args, format_str=False, format_keys=True,
                 format_eval=True):
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
    formated_args = dict(filter(lambda x: x[1] != '', tmp.items()))
    return formated_args


def checkStringNull(s):
    if s.strip() == '':
        return true

    return false


# 判断是否是数字 浮点数也可以
def is_number(num):
    pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')
    result = pattern.match(num)
    if result:
        return True
    else:
        return False


# 时间排序
def cmp_datetime(a, b):
    a_datetime = datetime.datetime.strptime(a, '%Y-%m-%d %H:%M:%S')
    b_datetime = datetime.datetime.strptime(b, '%Y-%m-%d %H:%M:%S')

    if a_datetime > b_datetime:
        return -1
    elif a_datetime < b_datetime:
        return 1
    else:
        return 0
