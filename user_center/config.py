import json
import os
import yaml
import platform


def get_config_path():
    path = str(os.path.abspath(os.path.dirname(os.path.realpath(__file__)))) + "/config.json"
    return path


def get_mysql_config():
    conf = get_conf('mysql')
    return conf


def get_rabbitmq_config():
    conf = get_conf('mq')
    return conf


def get_whitelist_config():
    conf = get_conf('whitelist')
    return conf


def get_transfer_platform_ip():
    conf = get_conf('transfer_platform_ip')
    return conf


def get_sms_config():
    conf = get_conf('sms')
    return conf


def get_aws_config():
    conf = get_conf('aws')
    return conf


def get_zt_config():
    conf = get_conf('zt')
    return conf


def get_intl_zt_config():
    conf = get_conf('intel_zt')
    return conf


def get_password_config():
    conf = get_conf('password')
    return conf


def get_use_source_conf():
    conf = get_conf('use_source')
    if conf == {}:
        return ""
    else:
        return conf


def check_use_source(use_source):
    return get_use_source_conf() == use_source


def get_conf(key=''):
    with open(get_config_path(), 'r') as f:
        tmp_json = json.load(f)
        if key == '':
            return tmp_json
        else:
            result = tmp_json.get(key)
            if result is None:
                return {}
            return result


def get_transfer_to_platform_config():
    file_name = "transfer_to_platform.yaml"
    root_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    file_path = replace_path_based_system(os.path.join(root_path, file_name))
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    config_dict = yaml.load(content)
    return config_dict


def replace_path_based_system(path):
    sys_type = platform.system()
    if sys_type == "Windows":
        path = path.replace("/", os.path.sep)
    return path


def get_transfer_to_platform_path(key1, key2):
    conf = get_transfer_to_platform_config()
    default_ip = conf['default_ip']

    if default_ip == "":
        return ""
    key1conf = conf.get(key1, "")
    if key1conf == "" or key1conf is None:
        return ""
    key2conf = key1conf.get(key2, "")
    if key2conf == "" or key2conf is None:
        return ""
    return str(default_ip) + str(key2conf)




