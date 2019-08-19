
from services.base_service import BaseService
from models.wallet_btc_model import WalletBtcModel
from models.wallet_eth_model import WalletEthModel
from models.wallet_eos_model import WalletEosModel
from models.secret_btc_model import SecretBtcModel
from models.secret_eth_model import SecretEthModel
from models.secret_eos_model import SecretEosModel
from models.secret_btc_gather_model import SecretBtcGatherModel
from models.secret_eth_gather_model import SecretEthGatherModel
from models.secret_eos_gather_model import SecretEosGatherModel
from models.record_sign_model import RecordSignModel
from models.token_salt_model import TokenSaltModel
from models.token_node_conf_model import TokenNodeConfModel
from tools.mysql_tool import MysqlTools
from utils.util import hexbytes_to_str
from utils.crypto_utils import super_deAES
from wallet.eos_util import EosUnit
from common_settings import *
import json


class TransactionService(BaseService):
    symbol_to_model = {
        _ZERO_S: [WalletBtcModel, SecretBtcModel, SecretBtcGatherModel],
        _SIXTY_S: [WalletEthModel, SecretEthModel, SecretEthGatherModel],
        _COIN_ID_EOS: [WalletEosModel, SecretEosModel, SecretEosGatherModel],
    }
    category = {
        "account": _ONE,
        "gather": _TWO
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def send_transaction(self, args):
        """
        "order_no", "parameter", "sign"
        :param args:
        :return:
        """
        order_no = args.get("order_no", "")
        parameter = args.get("parameter", "")
        sign = args.get("sign", "")
        check_flag = None
        coin_id = None
        symbol = None
        address = None
        calc = None
        if not order_no or not sign:
            self.return_error(20003)
        if isinstance(sign, dict):
            sign_tmp = sign
            for k, v in sign_tmp.items():
                if isinstance(v, bytes):
                    sign_tmp[k] = str(v, encoding="utf8")
            sign_log = json.dumps(sign_tmp)
        else:
            sign_log = str(sign)

        if isinstance(parameter, dict):
            coin_id = parameter.get("coin_id", "")
            address = parameter.get("address", "")
            symbol = parameter.get("symbol", "")
            calc = parameter.get("calc", "")
            if coin_id and address and symbol:
                check_flag = True
        if not check_flag:
            self.return_error(20003)

        # 判断币种类型合法性
        if coin_id not in self.symbol_to_model:
            self.return_error(90002)

        # 判断钱包类型合法性
        if symbol not in self.category:
            self.return_error(90004)

        # 获取对应model
        chain_model = self.symbol_to_model[coin_id][self.category[symbol]]

        # 查询结果,并记录流水
        with MysqlTools().session_scope() as session:
            record = session.query(RecordSignModel).filter(RecordSignModel.order_no == order_no).first()
            if record:
                self.return_error(10008)

            wallet = session.query(chain_model).filter(chain_model.sub_public_address == address).first()
            if not wallet:
                self.return_error(90003)

            public_key_aes = wallet.acct_public_key_aes
            private_key_aes = wallet.sub_private_key_aes

            salt = session.query(TokenSaltModel).filter(TokenSaltModel.public_key_aes == public_key_aes).first()
            if not salt:
                self.return_error(90005)
            key = salt.key_aes
            nonce = salt.nonce_aes

            record_sign = RecordSignModel(
                order_no=order_no,
                coin_id=coin_id,
                parameter=json.dumps(parameter),
                sign=sign_log
            )
            session.add(record_sign)
            session.commit()

        # 处理私钥
        sub_private_key = None
        if coin_id in [_ZERO_S, _SIXTY_S]:
            try:
                sub_private_key = super_deAES(private_key_aes, key, nonce)
            except Exception as e:
                self.return_error(90005, str(e))

        # 发送交易
        if coin_id == _ZERO_S:
            # btc交易
            tx_info, do_result = self.btc_send_tx(sign, sub_private_key, calc)
        elif coin_id == _SIXTY_S:
            # eth交易
            tx_info, do_result = self.eth_send_tx(sign, sub_private_key)
        elif coin_id == _COIN_ID_EOS:
            # eos交易
            tx_info, do_result = self.eos_send_tx(sign)
        else:
            tx_info = do_result = ""

        # 记录结果
        response = {
            "data": tx_info,
            "status": do_result
        }
        with MysqlTools().session_scope() as session:
            record_finally = session.query(RecordSignModel).filter(RecordSignModel.order_no == order_no).first()
            record_finally.response = json.dumps(response)
            record_finally.do_result = do_result
            session.commit()
        return response

    @staticmethod
    def btc_send_tx(sign, sub_private_key, calc):
        try:
            rpc = TokenNodeConfModel.get_btc_node_server()
            new_tx_encoded = rpc.signrawtransactionwithkey(sign, [sub_private_key])
            do_result = True
            if calc:
                return new_tx_encoded.get("hex"), do_result
            tx_hash = rpc.sendrawtransaction(new_tx_encoded.get("hex"), False)
        except Exception as e:
            if isinstance(e, dict):
                tx_hash = json.dumps(e)
            else:
                tx_hash = str(e)
            do_result = False
        print("tx_hash=")
        print(tx_hash)
        return tx_hash, do_result

    @staticmethod
    def eth_send_tx(sign, sub_private_key):
        try:
            w3 = TokenNodeConfModel.get_eth_node_server()
            signed_txn = w3.eth.account.signTransaction(sign, sub_private_key)
            tx_hash_hex_bytes = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            tx_hash = hexbytes_to_str(tx_hash_hex_bytes)
            do_result = True
        except Exception as e:
            if isinstance(e, dict):
                tx_hash = json.dumps(e)
            else:
                tx_hash = str(e)
            do_result = False
        print("tx_hash=")
        print(tx_hash)
        return tx_hash, do_result

    @staticmethod
    def eos_send_tx(sign):
        """
        sign = {
                "from": "luckyparkchn",
                "to": "eosluckypark",
                "quantity": "0.1000 EOS",
                "memo": "1000001",
            }
        :param sign:
        :return:
        """
        try:
            eu = EosUnit()
            eu.wallet_unlock()
            tx_res = eu.send_transaction(sign)
            do_result = True
            if "err" in tx_res:
                tx_hash = tx_res.get("err", "")
                do_result = False
            else:
                tx_hash = tx_res.get("transaction_id", "")
        except Exception as e:
            if isinstance(e, dict):
                tx_hash = json.dumps(e)
            else:
                tx_hash = str(e)
            do_result = False
        print("tx_hash=")
        print(tx_hash)
        return tx_hash, do_result

