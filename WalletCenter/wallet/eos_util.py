from models.token_node_conf_model import TokenNodeConfModel
from utils.time_util import str_to_timestamp, timestamp_to_str
import requests
from tools.tool import super_json_dumps
import json
from utils.log import raise_logger
from config import get_wallet_pub_key, get_wallet_wallet_key


class EosUnit(object):
    def __init__(self):
        self.ec = TokenNodeConfModel.get_eos_node_server()
        self.http_base_url = "https://api.eospark.com"
        self.rpc_base_wallet_url = "http://127.0.0.1:8899/v1/wallet"
        self.http_api_key = "779b305423258ed0fec69b29a06aeb4f"
        self.eos_pub_key = get_wallet_pub_key()
        self.wallet_key = get_wallet_wallet_key()
        self.expired_second = 120

    def rpc_get(self, api, unit=None):
        try:
            url = None
            if unit == "wallet":
                url = self.rpc_base_wallet_url + api
            response = requests.get(url, timeout=3600)
            if response.status_code in (200, 201):
                return response.json()
            else:
                raise Exception("http code: " + str(response.status_code))
        except Exception as e:
            raise_logger("Exception rpc_get: " + str(e), "wallet", "error")
        return {}

    def rpc_post(self, api, params=None, headers=None, form=None, unit=None, format_str=None):
        try:
            data = None
            url = None

            if format_str:
                data = super_json_dumps(params)
            else:
                if params:
                    data = json.dumps(params)
                elif form:
                    data = form
            if unit == "wallet":
                url = self.rpc_base_wallet_url + api
            response = requests.post(url, data=data, headers=headers, timeout=3600)
            if response.status_code in (200, 201):
                return response.json()
            else:
                if api != "/unlock":
                    raise Exception("http code: " + str(response.status_code))
        except Exception as e:
            raise_logger("Exception rpc_post: " + str(e), "wallet", "error")
        return {}

    def http_get(self, params=None, headers=None, api=None):
        try:
            url = self.http_base_url
            if not api:
                if params:
                    module_action = "/api?module=%(module)s&action=%(action)s&" % params + "apikey=" + self.http_api_key
                    for k, v in params.items():
                        if k not in ["module", "action"]:
                            module_action += "&" + k + "=" + str(v)
                    url += module_action
            else:
                url += "/v1/chain/" + api + "?apikey=" + self.http_api_key

            response = requests.get(url, headers=headers, timeout=3600)
            if response.status_code in (200, 201):
                return response.json()
            else:
                raise Exception("http code: " + str(response.status_code))
        except Exception as e:
            raise_logger("Exception http_get: " + str(e), "wallet", "error")
        return {}

    def http_post(self, params=None, headers=None, api=None):
        try:
            data = None
            url = self.http_base_url
            if api:
                url += "/v1/chain/" + api + "?apikey=" + self.http_api_key
            if params:
                data = super_json_dumps(params)

            response = requests.post(url, data=data, headers=headers, timeout=3600)
            if response.status_code in (200, 201):
                return response.json()
            else:
                raise Exception("http code: " + str(response.status_code))
        except Exception as e:
            raise_logger("Exception http_post: " + str(e), "wallet", "error")
        return {}

    def http_abi_json_to_bin(self, params):
        """
        3. 将交易信息由JSON格式序列化为BIN格式字符串
        :return:
        """
        api = "/abi_json_to_bin"
        sign_args = {
            "code": "eosio.token",
            "action": "transfer",
            "args": {
                "from": params["from"],
                "to": params["to"],
                "quantity": params["quantity"],
                "memo": params["memo"]
            }
        }
        res = self.http_post(params=sign_args, api=api)
        bin_data = res.get("binargs", "")
        if not bin_data:
            raise Exception("Exception http_abi_json_to_bin: EOSPark node has error!")
        return bin_data

    def get_sign_transaction(self, params):
        """
        签署交易
        :return:
        """
        api = "/sign_transaction"
        res = self.rpc_post(api, params=params, unit="wallet", format_str=True)
        return res

    def wallet_list(self):
        """
        查看钱包锁的状态
        :return:
        """
        api = "/list_wallets"
        res = self.rpc_get(api, unit="wallet")
        if not res or not isinstance(res, list):
            raise Exception("Exception wallet_list: localhost wallet node has error!")
        wallet_status = False
        if "*" in res[0]:
            wallet_status = True
        return wallet_status

    def wallet_unlock(self, params=None):
        """
        钱包解锁
        :param params:
        :return:
        """
        if not self.wallet_list():
            api = "/unlock"
            if not params:
                params = ["default", self.wallet_key]
            unlock_status = self.rpc_post(api, params=params, unit="wallet", format_str=True)
            if unlock_status:
                raise Exception("Exception wallet_unlock: localhost wallet node has error!")
        return

    def http_get_info(self):
        """
        获取chain_id
        :return:
        """
        api = "/get_info"
        res = self.http_get(api=api)
        chain_id = res.get("chain_id", "")
        if not chain_id:
            raise Exception("Exception http_get_info: EOSPark node has error!")
        return chain_id

    def get_base_trx_args(self):
        """
        拼接基础参数
        :return:
        """
        base_trx_args = {}
        try:
            latest_block = self.ec.http_get_latest_block()
            base_trx_args["chain_id"] = self.http_get_info()
            base_trx_args["pub_key"] = self.eos_pub_key
            base_trx_args["expiration"] = timestamp_to_str(str_to_timestamp(latest_block["timestamp"]) + float(self.expired_second), format_style="%Y-%m-%dT%H:%M:%S.%f")
            base_trx_args["ref_block_num"] = latest_block["block_num"]
            base_trx_args["ref_block_prefix"] = latest_block["ref_block_prefix"]
        except Exception as e:
            raise_logger("Exception get_base_trx_args: " + str(e), "wallet", "error")
        return base_trx_args

    def get_sign(self, base_trx_args, sign_args):
        """
        获取签名
        :param base_trx_args:
        :param sign_args:
        :return:
        """
        bin_data = self.http_abi_json_to_bin(sign_args)
        params = [{
            "ref_block_num": base_trx_args["ref_block_num"],
            "ref_block_prefix": base_trx_args["ref_block_prefix"],
            "expiration": base_trx_args["expiration"],
            "actions": [{
                "account": "eosio.token",
                "name": "transfer",
                "authorization": [{
                    "actor": sign_args["from"],
                    "permission": "active"
                }],
                "data": bin_data
            }],
            "signatures": []
        },
            [base_trx_args["pub_key"]],
            base_trx_args["chain_id"]
        ]
        sign = self.get_sign_transaction(params)
        return sign

    def send_transaction(self, sign_args):
        """
        推送交易
        :param sign_args:
        :return:
        """
        base_trx_args = self.get_base_trx_args()
        try:
            sign_data = self.get_sign(base_trx_args, sign_args)
            print("sign_data = ")
            print(sign_data)
            transaction_res = self.ec.http_push_transaction(sign_data)
        except Exception as e:
            raise_logger("Exception send_transaction: " + str(e), "wallet", "error")
            return {"err": str(e)}
        return transaction_res


if __name__ == "__main__":
    eu = EosUnit()
    eu.wallet_unlock()
    # sign_args = {
    #     "from": "eosluckypark",
    #     "to": "bigjeffwangy",
    #     "quantity": "0.0100 EOS",
    #     "memo": "1000001",
    # }
    sign_args = {"from": "eosluckypark", "to": "yangyue12345", "quantity": "0.9800 EOS", "memo": "1234566"}
    tx_res = eu.send_transaction(sign_args)
    print(tx_res)
