import json

from sqlalchemy import or_

from common_settings import *
from models.foreign_gather_record_model import ForeignGatherRecordModel
from models.foreign_withdraw_order_record_model import ForeignWithdrawOrderRecordModel
from models.token_coin_model import TokenCoinModel
from models.token_conf_model import TokenConfModel
from models.user_account_model import UserAccountModel
from models.wallet_btc_gather_model import WalletBtcGatherModel
from models.wallet_btc_model import WalletBtcModel
from models.wallet_eth_gather_model import WalletEthGatherModel
from models.wallet_eth_model import WalletEthModel
from services.base_service import BaseService
from services.wallet_foreign_service import WalletForeignService
from tools.mysql_tool import MysqlTools
from utils.util import decimal_to_str
from utils.util import generate_order_no
from utils.util import get_offset_by_page
from services.vcode_service import VcodeService
from config import get_config
import datetime

def operation_gather():
    with MysqlTools().session_scope() as session:
        wallet_list = session.query(WalletBtcModel, UserAccountModel).filter(
            WalletBtcModel.amount >= 0, WalletBtcModel.account_id != "").filter_by().outerjoin(
            UserAccountModel,
            WalletBtcModel.account_id == UserAccountModel.account_id)
        total_amount = 0
        for w in wallet_list:
            amount = w.WalletBtcModel.amount
            total_amount = total_amount + amount

        wfs = WalletForeignService()

operation_gather()