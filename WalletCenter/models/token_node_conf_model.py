from urllib import parse, request

import json
from sqlalchemy import Column, String
from models.base_model import BaseModel
from tools.mysql_tool import MysqlTools
from web3 import Web3
from config import get_env
from bitcoinrpc.authproxy import AuthServiceProxy
from web3.middleware import geth_poa_middleware
from common_settings import _ZERO_S, _ONE_S, _SIXTY_S, _COIN_ID_EOS
import requests


class TokenNodeConfModel(BaseModel):
    __tablename__ = "token_node_conf"
    node_env = Column(String(16), nullable=False, server_default="dev", comment="节点: 开发-dev, 正式-pd, 测试-test")
    coin_id = Column(String(128), nullable=False, server_default="", comment="货币id")
    node_url = Column(String(512), nullable=False, server_default="", comment="节点url")
    node_port = Column(String(16), nullable=False, server_default="", comment="节点port")
    server_status = Column(String(16), nullable=False, server_default="0", comment="服务使用状态: 0-未使用, 1-使用中")
    script_status = Column(String(16), nullable=False, server_default="0", comment="脚本使用状态: 0-未使用, 1-使用中")
    mark = Column(String(512), nullable=False, server_default="", comment="备注,如果连接有问题,记录问题信息")
    request_type = Column(String(32), nullable=False, server_default="", comment="请求类型 rpc http")
    email = Column(String(512), nullable=False, server_default="", comment="注册api key的邮箱")
    api_key = Column(String(512), nullable=False, server_default="", comment="api key http请求第三方节点时使用")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_node_url(coin_id, mold="server", node_env=None, pattern=None):
        filters = {}
        if not node_env:
            node_env = get_env()
        filters["coin_id"] = coin_id
        filters["node_env"] = node_env
        if mold == "server":
            filters["server_status"] = _ONE_S
        else:
            filters["script_status"] = _ONE_S
        conn = None
        with MysqlTools().session_scope() as session:
            node = session.query(TokenNodeConfModel).filter_by(**filters).first()
            if node:
                url, port = node.node_url, node.node_port
                if coin_id == _ZERO_S:
                    conn, err = TokenNodeConfModel.check_btc(url, port)
                elif coin_id == _SIXTY_S:
                    conn, err = TokenNodeConfModel.check_eth(url, port)
                elif coin_id == _COIN_ID_EOS:
                    conn, err = TokenNodeConfModel.check_eos(url, port, node.api_key, pattern)

                if conn:
                    if node.mark != "":
                        node.mark = ""
                        session.commit()
                    return conn
                else:
                    if mold == "server":
                        node.server_status = _ZERO_S
                    else:
                        node.script_status = _ZERO_S
                    node.mark = err

            if mold == "server":
                del filters["server_status"]
            else:
                del filters["script_status"]
            node_list = session.query(TokenNodeConfModel).filter_by(**filters).all()
            if not node_list:
                raise Exception("db not have available node!")
            for next_node in node_list:
                url, port = next_node.node_url, next_node.node_port
                if coin_id == _ZERO_S:
                    conn, err = TokenNodeConfModel.check_btc(url, port)
                elif coin_id == _SIXTY_S:
                    conn, err = TokenNodeConfModel.check_eth(url, port)
                elif coin_id == _COIN_ID_EOS:
                    conn, err = TokenNodeConfModel.check_eos(url, port, node.api_key)
                if conn:
                    if mold == "server":
                        next_node.server_status = _ONE_S
                    else:
                        next_node.script_status = _ONE_S
                    if next_node.mark != "":
                        next_node.mark = ""
                    break
                else:
                    next_node.mark = err
            session.commit()
            if conn:
                return conn
        raise Exception("db not have available node!")

    @staticmethod
    def check_eos(url, port, api_key=None, pattern=None):
        try:
            if "http" in url:
                node_url = url + port
            else:
                node_url = "http://%s:%s" % (url, port)
            ec = EosConnect(http_base_url=node_url, http_api_key=api_key)
            if pattern == "fast":
                latest_block = ec.http_get_latest_block()
                return latest_block, None
        except Exception as e:
            return False, str(e)
        return ec, None

    @staticmethod
    def check_eth(url, port):
        try:
            if "http" in url:
                node_url = url + port
            else:
                node_url = "http://%s:%s" % (url, port)
            w3 = Web3(Web3.HTTPProvider(node_url))
            w3.middleware_stack.inject(geth_poa_middleware, layer=0)
            _ = w3.eth.blockNumber
        except Exception as e:
            return False, str(e)
        return w3, None

    @staticmethod
    def check_btc(url, port):
        try:
            if "http" in url:
                node_url = url + port
            else:
                node_url = "http://%s:%s@%s:%s" % ("RPCuser", "RPCpasswd", url, port)
            rpc_connection = AuthServiceProxy(node_url)
            _ = rpc_connection.getblockcount()
        except Exception as e:
            return False, str(e)
        return rpc_connection, None

    @classmethod
    def get_btc_node_server(cls):
        return cls.get_node_url(_ZERO_S, mold="server")

    @classmethod
    def get_btc_node_script(cls):
        return cls.get_node_url(_ZERO_S, mold="script")

    @classmethod
    def get_eth_node_server(cls):
        return cls.get_node_url(_SIXTY_S, mold="server")

    @classmethod
    def get_eth_node_script(cls):
        return cls.get_node_url(_SIXTY_S, mold="script")

    @classmethod
    def get_eos_node_server(cls, pattern=None):
        return cls.get_node_url(_COIN_ID_EOS, mold="server", pattern=pattern)

    @classmethod
    def get_eos_node_script(cls, pattern=None):
        return cls.get_node_url(_COIN_ID_EOS, mold="script", pattern=pattern)


class EosConnect(object):
    def __init__(self, *args, **kwargs):
        super().__init__()
        if "http_base_url" in kwargs:
            self.http_base_url = kwargs["http_base_url"]
            self.http_api_key = kwargs["http_api_key"]

    def do_get(self, params=None, headers=None):
        try:
            url = self.http_base_url
            if params:
                module_action = "?module=%(module)s&action=%(action)s&" % params + "apikey=" + self.http_api_key
                for k, v in params.items():
                    if k not in ["module", "action"]:
                        module_action += "&" + k + "=" + str(v)
                url += module_action
            response = requests.get(url, headers=headers, timeout=3600)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception("http code: " + str(response.status_code))
        except Exception as e:
            print(e)
        return {}

    def do_post(self, body_params=None, params=None, headers=None):
        try:
            data = None
            url = self.http_base_url
            if params:
                module_action = "?module=%(module)s&action=%(action)s&" % params + "apikey=" + self.http_api_key
                for k, v in params.items():
                    if k not in ["module", "action"]:
                        module_action += "&" + k + "=" + str(v)
                url += module_action
            if body_params:
                data = json.dumps(body_params)
            response = requests.post(url, data=data, headers=headers, timeout=3600)
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception as e:
            raise ConnectionError("httpGet failed, detail is: %s" % e)

    def http_get_latest_block(self):
        """

        :return:
        """
        params = {
            "module": "block",
            "action": "get_latest_block",
        }
        res = self.do_get(params)
        err_no = res.get("errno", "")
        if err_no == 0:
            return res.get("data")
        elif err_no != "":
            return {}
        else:
            raise Exception("eos node response error http_get_latest_block")

    def http_get_block_detail(self, block_num):
        """

        :return:
        """
        params = {
            "module": "block",
            "action": "get_block_detail",
            "block_num": str(block_num),
        }
        res = self.do_get(params)
        err_no = res.get("errno", "")
        if err_no == 0:
            return res.get("data")
        elif err_no != "":
            return {}
        else:
            raise Exception("eos node response error http_get_block_detail")

    def http_push_transaction(self, body_params):
        """

        :param body_params:
        :return:
        """
        params = {
            "module": "transaction",
            "action": "push_transaction",
            "fmt": "raw"
        }
        res = self.do_post(body_params=body_params, params=params)
        err_no = res.get("errno", "")
        if err_no == 0:
            return res.get("data")
        elif err_no != "":
            raise Exception("eos http_push_transaction err_no: " + str(res.get("errno", "")) + " errmsg: " + str(res.get("errmsg", "")))
        else:
            raise Exception("eos node response error http_push_transaction")


if __name__ == "__main__":
    pass
    # ecc = TokenNodeConfModel.get_eos_node_server("fast")
    ecc = TokenNodeConfModel.get_eos_node_server()
    # res = ecc.http_get_latest_block()
    # print(ecc.http_get_block_detail(36641100))
    # print(ecc)
    # print(res)
