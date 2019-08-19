from services.base_service import BaseService
from models.wallet_btc_model import WalletBtcModel
from models.wallet_eth_model import WalletEthModel
from models.secret_btc_model import SecretBtcModel
from models.secret_eth_model import SecretEthModel
from models.secret_btc_gather_model import SecretBtcGatherModel
from models.secret_eth_gather_model import SecretEthGatherModel
from models.token_coin_model import TokenCoinModel
from models.record_pk_model import RecordPkModel
from tools.mysql_tool import MysqlTools
from utils.util import get_str_from_list
from config import get_about_conf
from common_settings import *
import json


class CentralService(BaseService):
    symbol_to_model = {
        _BTC: [WalletBtcModel, SecretBtcModel, SecretBtcGatherModel],
        _ETH: [WalletEthModel, SecretEthModel, SecretEthGatherModel],
    }
    _gather = "gather"
    _normal = "normal"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mysql_token = MysqlTools(get_about_conf())
        self.coin_id = None

    def get_private_key_from_address(self, args):
        order_no = args["order_no"]
        coin_type = args["type"].upper()
        address = args["address"]
        category = args.get("category", self._normal)

        # 查询coin_id
        with self.mysql_token.session_scope() as session:
            # 查询 token_id
            token = session.query(TokenCoinModel).filter(TokenCoinModel.coin_name == coin_type).first()
            if not token:
                self.return_error(90002)
            self.coin_id = token.coin_id

        # 判断地址合法性
        if isinstance(address, str):
            address = [address]
        else:
            if not isinstance(address, list):
                self.return_error(90001)

        # 判断币种类型合法性
        if coin_type not in self.symbol_to_model:
            self.return_error(90002)

        # 判断地址类型合法性
        if category == self._normal:
            model_index = _ONE
            ret = {"category": self._normal}
        elif category == self._gather:
            model_index = _TWO
            ret = {"category": self._gather}
        else:
            self.return_error(90004)
            ret = {}
            model_index = _ZERO

        # 获取对应model
        chain_model = self.symbol_to_model[coin_type][model_index]

        # 地址转成字符串
        address_record = get_str_from_list(address)

        # 查询结果,并记录流水
        with MysqlTools().session_scope() as session:
            record = session.query(RecordPkModel).filter(RecordPkModel.order_no == order_no).first()
            if record:
                self.return_error(10008)

            wallets = session.query(chain_model).filter(chain_model.sub_public_address.in_(address)).with_for_update().all()
            if not wallets:
                self.return_error(90003)

            for w in wallets:
                public_key_aes = w.acct_public_key_aes
                public_address = w.sub_public_address
                private_key_aes = w.sub_private_key_aes

                if public_key_aes not in ret:
                    ret[public_key_aes] = [{
                        "public_address": public_address,
                        "private_key_aes": private_key_aes,
                    }]
                else:
                    ret[public_key_aes].append(
                        {
                            "public_address": public_address,
                            "private_key_aes": private_key_aes,
                        }
                    )

            record_pk = RecordPkModel(
                order_no=order_no,
                coin_id=self.coin_id,
                address=address_record,
                response=json.dumps(ret),
                category=category
            )
            session.add(record_pk)
            session.commit()

        return ret

