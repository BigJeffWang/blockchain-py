from utils.crypto_utils import super_AES
from tools.mysql_tool import MysqlTools
from models.secret_btc_gather_model import SecretBtcGatherModel
from models.wallet_btc_gather_model import WalletBtcGatherModel
from models.secret_btc_model import SecretBtcModel
from models.wallet_btc_model import WalletBtcModel


def get_wallet_mysql(arg):
    db_conf = {
        "wallet": {
            "db": "WalletCenter",
            "host": "test.cgvynnfmwcpw.ap-northeast-1.rds.amazonaws.com",
            "port": "3306",
            "user": "Xe3r7TMs2UeY",
            "psd": "X88Db3jLBXki"
        },
        "token": {
            "db": "TokenPark",
            "host": "test.cgvynnfmwcpw.ap-northeast-1.rds.amazonaws.com",
            "port": "3306",
            "user": "H34pHJ2jdtGC",
            "psd": "BF1xE960ivNd"
        }
    }
    tools = MysqlTools(db_conf[arg])
    return tools


def read_file(file_name):
    ret_list = []
    with open(file_name, "r") as f:
        rows = f.readlines()
        row_count = len(rows)
        for i in range(row_count):
            tmp_row = rows[i].strip('\n')
            if tmp_row:
                ret_list.append(tmp_row)
    return ret_list


def aes_process(pri_key_list):
    key = "77616e677965"
    nonce = "37383934353631323330"
    ret_list = []
    for pri_key in pri_key_list:
        if pri_key:
            res_super_aes = super_AES(pri_key, key, nonce)
            ret_list.append(res_super_aes)
    return ret_list


def work():
    pub_key_file = "pub_key.txt"
    pri_key_file = "pri_key.txt"

    pub_key_list = read_file(pub_key_file)
    pri_key_list = read_file(pri_key_file)
    pri_key_aes_list = aes_process(pri_key_list)

    print(pri_key_aes_list)
    wallet_tools = get_wallet_mysql("wallet")
    token_tools = get_wallet_mysql("token")

    with wallet_tools.session_scope() as wallet_session:
        wallet_model = wallet_session.query(SecretBtcModel).filter().all()
        for i in range(120):
            wallet_model[i].sub_private_key_aes = pri_key_aes_list[i]
            wallet_model[i].sub_public_address = pub_key_list[i]
        wallet_session.commit()

    with token_tools.session_scope() as token_session:
        token_model = token_session.query(WalletBtcModel).filter().all()
        for i in range(120):
            token_model[i].sub_public_address = pub_key_list[i]
        token_session.commit()

    return


if __name__ == "__main__":
    work()
