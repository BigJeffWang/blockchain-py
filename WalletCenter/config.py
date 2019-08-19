import yaml
import os
import platform
from pathlib import Path


def get_config(file_name="base_config.yaml"):
    file_path = get_file_path(file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    config_dict = yaml.load(content)
    return config_dict


def get_wallet_config(file_name="wallet.yaml", remove_type=True):
    config_dict = get_config(file_name)
    file_path = get_file_path(file_name)
    if remove_type:
        os.remove(file_path)
        print(file_name + " already has been deleted!!!")
    return config_dict


def get_bank_config(file_name="bank_config.yaml"):
    config_dict = get_config(file_name)
    config_dict["bases"] = get_config()["bases"]
    return config_dict


def get_bases_conf():
    return get_config()["bases"]


def get_user_center_conf():
    return get_config()["user_center"]


def get_env():
    return get_config()["env"]


def get_wallet_pub_key():
    return get_config()["wallet"][get_env()]["pub_key"]


def get_wallet_wallet_key():
    return get_config()["wallet"][get_env()]["wallet_key"]


def get_white_list():
    return get_config()["white_list"][get_env()]["ip"]


def replace_path_based_system(path):
    sys_type = platform.system()
    if sys_type == "Windows":
        path = path.replace("/", os.path.sep)
    return path


def get_about_conf(name="mysql_token"):
    return get_config()[name][get_env()]


def get_redis_conf():
    return get_config()["redis"][get_env()]


def get_mongodb_conf():
    return get_config()["mongodb"][get_env()]


def get_file_path(file_name):
    root_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    file_path = replace_path_based_system(os.path.join(root_path, file_name))
    return file_path


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


def get_whether_on_server():
    server_dir = Path("/data/WalletCenter")
    result = server_dir.is_dir()
    return result


if __name__ == "__main__":
    pass
