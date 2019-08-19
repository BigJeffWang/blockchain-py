import yaml
import os
import platform
from pathlib import Path


def get_file_path(file_name):
    root_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    file_path = replace_path_based_system(os.path.join(root_path, file_name))
    return file_path


def get_config(file_name="base_config.yaml"):
    file_path = get_file_path(file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    config_dict = yaml.load(content)
    return config_dict


def get_env():
    return get_config()["env"]


def get_bank_config(file_name="bank_config.yaml"):
    config_dict = get_config(file_name)
    config_dict["bases"] = get_config()["bases"]
    return config_dict


def get_bases_conf():
    return get_config()["bases"]


def get_user_center_conf():
    return get_config()["user_center"]


def get_wallet_center():
    wallet_center = get_config()["wallet_center"][get_env()]
    return wallet_center


def replace_path_based_system(path):
    sys_type = platform.system()
    if sys_type == "Windows":
        path = path.replace("/", os.path.sep)
    return path


def get_mysql_conf(env=None):
    if not env:
        return get_config()["mysql"][get_env()]
    return get_config()["mysql"][env]


def get_mysql_eos_conf(env=None):
    if not env:
        return get_config()["mysql_eos"][get_env()]
    return get_config()["mysql_eos"][env]


def get_redis_conf():
    return get_config()["redis"][get_env()]


def get_mongodb_conf():
    return get_config()["mongodb"][get_env()]


def write_yaml_config(data, file_name="wallet.yaml"):
    # 目前只支持一层层级结构
    if not isinstance(data, dict):
        return
    yaml_config = get_config(file_name)
    for k, v in data.items():
        if k in yaml_config:
            if isinstance(yaml_config[k], dict):
                for kk, vv in data[k].items():
                    yaml_config[k][kk] = vv

    with open(get_file_path(file_name), 'w') as f:
        yaml.dump(yaml_config, f, default_flow_style=False)
    return True


def get_private_block_chain_conf():
    return get_config()["private_block_chain"][get_env()]


def get_host_url():
    return get_config()["host_url"][get_env()]


def get_sms_email(key=None):
    if key:
        return get_config()["sms_email"][get_env()].get(key, {})
    else:
        return get_config()["sms_email"][get_env()]


def get_whether_on_server():
    server_dir = Path("/data/TokenPark")
    result = server_dir.is_dir()
    return result


def get_tokenpark_url_conf():
    return get_config()["tokenpark_url"][get_env()]


if __name__ == "__main__":
    # get_config()
    # data = {"eth": {"mnemonic_aes": "`333", "acct_public_key_aes": "2222"}}
    # write_yaml_config(data)
    get_whether_on_server()
