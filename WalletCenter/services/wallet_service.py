import sys
from pathlib import Path

pro_name = "WalletCenter"
current_path = str(Path(__file__).resolve())
import_index = current_path.rfind(pro_name)
import_path = current_path[:import_index + len(pro_name)]
path_flag = True if not import_path in sys.path else False
if path_flag:
    sys.path.append(import_path)

from services.base_service import BaseService
from models.wallet_btc_model import WalletBtcModel
from models.wallet_eth_model import WalletEthModel
from models.wallet_eos_model import WalletEosModel
from models.wallet_btc_gather_model import WalletBtcGatherModel
from models.wallet_eth_gather_model import WalletEthGatherModel
from models.wallet_eos_gather_model import WalletEosGatherModel
from models.secret_btc_model import SecretBtcModel
from models.secret_eth_model import SecretEthModel
from models.secret_eos_model import SecretEosModel
from models.secret_btc_gather_model import SecretBtcGatherModel
from models.secret_eth_gather_model import SecretEthGatherModel
from models.secret_eos_gather_model import SecretEosGatherModel
from models.token_coin_model import TokenCoinModel
from models.token_salt_model import TokenSaltModel
from tools.mysql_tool import MysqlTools
from wallet.wallet_util import Wallet
from utils.crypto_utils import super_AES
from config import get_wallet_config, get_about_conf
from utils.crypto_utils import encode_str_hex
from common_settings import *


class WalletService(BaseService):
    symbol_to_token_coin = {
        _BTC: _COIN_ID_BTC,
        _ETH: _COIN_ID_ETH,
        _EOS: _COIN_ID_EOS
    }
    symbol_to_model = {
        _BTC: [WalletBtcModel, SecretBtcModel, WalletBtcGatherModel, SecretBtcGatherModel],
        _ETH: [WalletEthModel, SecretEthModel, WalletEthGatherModel, SecretEthGatherModel],
        _EOS: [WalletEosModel, SecretEosModel, WalletEosGatherModel, SecretEosGatherModel],
    }
    _gather = "gather"
    _normal = "normal"
    interval = _HUNDRED * _ONE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        wc = get_wallet_config(remove_type=False)
        self.wallet = None
        self.chain_model = None
        self.chain_token_model = None
        self.acct_pub_key_b58_aes = None
        self.coin_id = None
        self.symbol = wc["symbol"].upper()
        self.key = str(wc["key"])
        self.nonce = str(wc["nonce"])
        self.mnemonic = wc["mnemonic"]
        self.passphrase = wc["passphrase"]
        self.category = wc.get("category", self._normal).lower()
        self.mysql_token = MysqlTools(get_about_conf())
        self.mysql_wallet = MysqlTools()

    def wallet_init(self):
        """
        :return:
        """
        if self.symbol not in self.symbol_to_model or self.symbol not in self.symbol_to_token_coin:
            raise Exception("There is no corresponding symbol")
        if self.category == self._normal:
            token_model_index = _ZERO
            secret_model_index = _ONE
        elif self.category == self._gather:
            token_model_index = _TWO
            secret_model_index = _THREE
        else:
            raise Exception("The category does not exist")
        self.chain_token_model = self.symbol_to_model[self.symbol][token_model_index]
        self.chain_model = self.symbol_to_model[self.symbol][secret_model_index]
        self.wallet = Wallet(symbol=self.symbol)
        self.wallet.init_acct(self.mnemonic, self.passphrase)
        self.acct_pub_key_b58_aes = super_AES(self.wallet.get_acct_key()["acct_pub_key_b58"], self.key, self.nonce)
        # 查询 token_id
        self.coin_id = self.symbol_to_token_coin[self.symbol]
        with self.mysql_wallet.session_scope() as session:
            # 查询或插入 token_salt
            salt = session.query(TokenSaltModel).filter(TokenSaltModel.public_key_aes == self.acct_pub_key_b58_aes, TokenSaltModel.coin_id == self.coin_id).first()
            if not salt:
                new_salt = TokenSaltModel(
                    coin_id=self.coin_id,
                    public_key_aes=self.acct_pub_key_b58_aes,
                    key_aes=self.key,
                    nonce_aes=self.nonce
                )
                session.add(new_salt)
            else:
                if salt.key_aes != self.key or salt.nonce_aes != self.nonce:
                    raise Exception("Table token_salt contains this key nonce, results already generated cannot be replaced with new key or nonce")
            session.commit()

    def wallet_generate(self, count):
        """
        生成HD子钱包
        :param count: 生成的子钱包个数, 按index顺序生成, 接续数据库索引
        :return:
        """
        remainder = count % self.interval
        times = count // self.interval + _ONE if remainder else count // self.interval
        for num in range(_ONE, times + _ONE):
            count = self.interval
            if num == times:
                if remainder:
                    count = remainder
            # 获取数据库现有索引
            with self.mysql_wallet.session_scope() as session:
                wallets = session.query(self.chain_model).filter(self.chain_model.acct_public_key_aes == self.acct_pub_key_b58_aes).with_for_update().order_by(self.chain_model.sub_index.desc(),
                                                                                                                                                               self.chain_model._id.desc()).first()

                if not wallets:
                    begin = None
                else:
                    begin = int(wallets.sub_index) + _ONE
                print("-" * 20)
                print("The latest index is: " + str(begin - _ONE) if begin else str(_ZERO))

                wallet_list, wallet_token_list = self.chain_model_generate(count, begin)

                with self.mysql_token.session_scope() as session_token:
                    session_token.add_all(wallet_token_list)
                    session_token.commit()

                session.add_all(wallet_list)
                session.commit()
            print("Now we've successfully inserted: " + str(count) + "!!!")
            print("-" * 20)
        return True

    def chain_model_generate(self, count, begin):
        """
        批量生成chain model
        :param count:
        :param begin:
        :return: model list
        """

        sub_key = self.wallet.get_sub_key(count, begin)
        sub_key_aes = {}
        if self.symbol in [_BTC, _ETH]:
            for k, v in sub_key.items():
                sub_key_aes[k] = super_AES(v, self.key, self.nonce)
        elif self.symbol in [_EOS]:
            sub_key_aes = sub_key
        wallet_list = []
        wallet_token_list = []
        for sub_index, index_info in sub_key_aes.items():
            if self.symbol in [_EOS] and self.category == self._gather:
                index_info["sub_private_key"] = super_AES(index_info["sub_private_key"], self.key, self.nonce)
                index_info["sub_address"] = self.mnemonic
            print('  change_index: ' + index_info["change_index"] + " public_address: " + index_info["sub_address"])
            w = self.chain_model(
                sub_index=int(sub_index),
                change_index=index_info["change_index"],
                sub_private_key_aes=index_info["sub_private_key"],
                sub_public_key_aes=index_info["sub_public_key"],
                sub_public_address=index_info["sub_address"],
                acct_public_key_aes=self.acct_pub_key_b58_aes,
                coin_id=self.coin_id
            )
            w_token = self.chain_token_model(
                sub_index=int(sub_index),
                change_index=index_info["change_index"],
                sub_public_address=index_info["sub_address"],
                acct_public_key_aes=self.acct_pub_key_b58_aes,
                coin_id=self.coin_id
            )
            wallet_list.append(w)
            wallet_token_list.append(w_token)
        return wallet_list, wallet_token_list

    @staticmethod
    def generate_key_nonce(key, nonce):
        """
        transform origin args type
        :param key: must be origin
        :param nonce:
        :return:
        """
        return {
            "key": encode_str_hex(key),
            "nonce": encode_str_hex(nonce)
        }


def running(num=1000):
    wallet = WalletService()
    wallet.wallet_init()
    wallet.wallet_generate(num)


if __name__ == "__main__":
    pass

    # print(WalletService.generate_key_nonce("wangye", "7894561230"))

    # running(1)
    running(2000)
