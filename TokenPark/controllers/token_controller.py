from controllers.base_controller import BaseController
from services.wallet_interior_service import WalletInteriorService


class TokenController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self):
        """
        返回币种列表
        :return:
        """
        return WalletInteriorService().get_coin_list()

    def post(self):
        coin_list = {
            "BTC": "0",
            "ETH": "60",
            "EOS": "194",
        }
        return coin_list
