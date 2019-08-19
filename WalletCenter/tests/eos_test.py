import json

import requests

from tools.tool import super_json_dumps


class EosOperation(object):
    def __init__(self):
        super().__init__()
        # self.rpc_base_url = "http://3.17.69.57:8888/v1/chain"
        self.rpc_base_url = "http://18.223.229.212:8888/v1/chain"
        self.rpc_base_wallet_url = "http://127.0.0.1:8899/v1/wallet"
        # self.rpc_base_url = "http://peer.main.alohaeos.com:8888/v1/chain"
        # self.rpc_base_url = "http://api.eosnewyork.io/v1/chain"
        # self.rpc_base_url = "https://api.eosdetroit.io:443/v1/chain"
        # self.rpc_base_url = "https://user-api.eoseoul.io:443/v1/chain"
        # self.rpc_base_url = "http://bp.cryptolions.io:8888/v1/chain"
        self.http_base_url = "https://api.eospark.com"
        self.http_api_key = "779b305423258ed0fec69b29a06aeb4f"

    def rpc_post(self, api, params=None, headers=None, form=None, unit=None, format_str=None):
        try:
            data = None
            if params:
                data = json.dumps(params)
            if form:
                data = form
            if format_str:
                data = super_json_dumps(params)
                print(data)
            url = None
            if not unit:
                url = self.rpc_base_url + api
            elif unit == "wallet":
                url = self.rpc_base_wallet_url + api
            response = requests.post(url, data=data, headers=headers, timeout=3600)
            if response.status_code in (200, 201):
                return response.json()
            else:
                raise Exception("http code: " + str(response.status_code))
        except Exception as e:
            print(e)
        return

    def http_get(self, params=None, headers=None):
        try:
            url = self.http_base_url
            if params:
                module_action = "/api?module=%(module)s&action=%(action)s&" % params + "apikey=" + self.http_api_key
                for k, v in params.items():
                    if k not in ["module", "action"]:
                        module_action += "&" + k + "=" + str(v)
                url += module_action

            response = requests.get(url, headers=headers, timeout=3600)
            if response.status_code not in [400, 500]:
                return response.json()
            else:
                raise Exception("http code: " + str(response.status_code))
        except Exception as e:
            print(e)
        return

    def http_post(self, params=None, headers=None, api=None):
        try:
            url = self.http_base_url
            if params:
                url += "/v1/chain/" + api + "?apikey=" + self.http_api_key

            response = requests.post(url, data=params, headers=headers, timeout=3600)
            if response.status_code not in [400, 500]:
                return response.json()
            else:
                raise Exception("http code: " + str(response.status_code))
        except Exception as e:
            print(e)
        return

    def get_trx_from_pubkey(self, account_name):
        pubkey_lib = {
            "bigjeffwangy": "EOS7RmEQ7VRav5xGM3Q6sQxcY3R74qnuQFYtuhDQyjwxVEkkvFPBw",
            "eosluckypark": "EOS8gYAfKyzW69y6nJfL3t1fGoP9Rpiji4xEYHjNF74BcHjB4xPf5"
        }
        pubkey = pubkey_lib.get(account_name, "")
        return pubkey

    def get_currency_balance(self, account="eosluckypark"):
        """
        获取用户余额
        :param account:
        :return:
        """
        params = {"code": "eosio.token", "account": account, "symbol": "eos"}
        api = "/get_currency_balance"
        res = self.rpc_post(api, params)
        return res

    def get_info(self):
        """
        1.获取节点详情
        :return:
        """
        api = "/get_info"
        res = self.rpc_post(api)
        return res

    def get_block(self, block_id):
        """
        2.获取块信息
        :return:
        """
        api = "/get_block"
        params = {"block_num_or_id": str(block_id)}
        res = self.rpc_post(api, params)
        return res

    def abi_json_to_bin(self, params):
        """
        3. 将交易信息由JSON格式序列化为BIN格式字符串
        "args": {
                "from": "testnetyy111",
                "to": "testneths111",
                "quantity": "100.0000 EOS",
                "memo": "hi there"
            }
        :return:
        """
        api = "/abi_json_to_bin"
        sign_args = {
            "code": "eosio.token",
            "action": "transfer",
            "args": params
        }
        res = self.rpc_post(api, sign_args)
        return res

    def get_sign_transaction(self, params):
        """
        签署交易
        :return:
        """
        api = "/sign_transaction"
        res = self.rpc_post(api, params=params, unit="wallet", format_str=True)
        return res

    def wallet_unlock(self, params):
        """

        :param params:
        :return:
        """
        api = "/unlock"
        res = self.rpc_post(api, params=params, unit="wallet", format_str=True)
        return res

    def http_get_account_balance(self, account="eosluckypark"):
        """

        """
        params = {
            "module": "account",
            "action": "get_account_balance",
            "account": str(account),
        }
        res = self.http_get(params)
        print(res)

    def http_get_block_detail(self, block_num):
        """

        :return:
        """
        params = {
            "module": "block",
            "action": "get_block_detail",
            "block_num": str(block_num),
        }
        res = self.http_get(params)
        return res

    def http_get_latest_block(self):
        """

        :return:
        """
        params = {
            "module": "block",
            "action": "get_latest_block",
        }
        res = self.http_get(params)
        return res

    def http_abi_json_to_bin(self, params):
        """

        :param args:
        :return:
        """
        api = "abi_json_to_bin"

        sign_args = {
            "code": "eosio.token",
            "action": "transfer",
            "args": params
        }
        data = super_json_dumps(sign_args)
        res = self.http_post(params=data, api=api)
        return res


if __name__ == "__main__":
    ep = EosOperation()
    # account_balance = ep.get_currency_balance()
    # # account_balance = ep.get_currency_balance("bigjeffwangy")
    # print(account_balance)
    # eos_info = ep.get_info()
    # print(eos_info)

    # params = {
    #     "code": "eosio.token",
    #     "action": "transfer",
    #     "args": {
    #         "from": "luckyparkchn",
    #         "to": "eosluckypark",
    #         "quantity": "0.1 EOS",
    #         "memo": "1000001"
    #     }}
    # json_to_bin = ep.abi_json_to_bin(params)
    # print(json_to_bin)

    # wparams = ["default", "PW5K3uB1PWKsUALWbHSygTzFfyxWFiuXBgeWTPXHVcHt33dpuzQMn"]
    # res = ep.wallet_unlock(wparams)
    # print(res)

    # params = [{
    #     "ref_block_num": 13800828,
    #     "ref_block_prefix": 171729965,
    #     "expiration": "2018-09-11T05:59:10.000",
    #     "actions": [{
    #         "account": "eosio.token",
    #         "name": "transfer",
    #         "authorization": [{
    #             "actor": "testnetyy111",
    #             "permission": "active"
    #         }],
    #         "data": "1042f03eab99b1ca1042c02dab99b1ca40420f000000000004454f5300000000086869207468657265"
    #     }],
    #     "signatures": []
    # },
    #     ["EOS6Z7mUQeFC2cQTT3xMyZh2wsLQoHih1bTMgRhr3dbichprTi7Rc"], "038f4b0fc8ff18a4f0842a8f0564611f6e96e8535901dd45e43ac8691a1c4dca"
    # ]
    # sign = ep.get_sign_transaction(params)
    # print(sign)

    #

    # ep.http_get_account_balance()
    #
    # last_block_num = eos_info.get("head_block_num", "")
    # print(last_block_num)
    # last_head_block_id = eos_info.get("head_block_id", "")
    # print(last_head_block_id)
    #
    # eos_block = ep.get_block(last_block_num)
    # print(eos_block)

    trx_info = {
        "from": "bigjeffwangy",
        "to": "eosluckypark",
        "quantity": "1.100 EOS",
        "memo": "1000101"
    }

    # trx_info_bin = ep.abi_json_to_bin(trx_info)
    # print(trx_info_bin)

    # http_trx_info_bin = ep.http_abi_json_to_bin(trx_info)
    # print(http_trx_info_bin)
    #
    http_latest_block = ep.http_get_latest_block()
    print(http_latest_block)
    #
    # http_latest_block_num = http_latest_block.get("data").get("block_num")
    # print(http_latest_block_num)
    #
    # http_latest_ref_block_prefix = http_latest_block.get("data").get("ref_block_prefix")
    # print(http_latest_ref_block_prefix)
    #
    # http_latest_timestamp = http_latest_block.get("data").get("timestamp")
    # print(http_latest_timestamp)
    #
    # http_latest_id = http_latest_block.get("data").get("id")
    # print(http_latest_id)
    #
    # # print("***********************")
    # http_latest_block_detail = ep.http_get_block_detail(37725796)
    # print(http_latest_block_detail)
    #
    # trx_pubkey = ep.get_trx_from_pubkey("bigjeffwangy")
    # print(trx_pubkey)
