from services.base_service import BaseService
from models.token_coin_model import TokenCoinModel
from tools.mysql_tool import MysqlTools
from common_settings import *


class WalletInteriorService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_coin_list():
        """
        获取币种列表,可以是coin_id
        :return:
        """
        with MysqlTools().session_scope() as session:
            coins = session.query(TokenCoinModel).filter(TokenCoinModel.status == _ONE_S).all()
            if not coins:
                return
            coin_list = {}
            for coin in coins:
                coin_list[coin.coin_id] = {"coin_name": coin.coin_name, "coin_des": coin.coin_des}
        return coin_list


class WalletEthService(WalletInteriorService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test(self):
        pass


class WalletBtcService(WalletInteriorService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test(self):
        pass


