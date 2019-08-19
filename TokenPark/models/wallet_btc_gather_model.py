from sqlalchemy import Column, String, Numeric, BigInteger
from sqlalchemy.dialects.mysql import TINYINT
from models.base_model import BaseModel
from utils.util import get_decimal


class WalletBtcGatherModel(BaseModel):
    __tablename__ = "wallet_btc_gather"
    sub_index = Column(BigInteger, nullable=False, comment="归集账户 子钱包索引")
    sub_public_address = Column(String(255), unique=True, nullable=False, server_default="", comment="归集账户 子地址")
    change_index = Column(String(255), nullable=False, server_default="", comment="归集账户 change index")
    acct_public_key_aes = Column(String(255), nullable=False, server_default="", comment="归集账户 主公钥AES加密防止以后有多个助记词生成主秘钥同时使用")
    coin_id = Column(String(128), nullable=False, server_default="", comment="归集账户 货币id")
    account_id = Column(String(64), nullable=False, server_default="", comment="归集账户 主账户ID")
    status = Column(TINYINT(1), nullable=False, server_default="1", comment="归集账户 状态")
    amount = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="可用余额")
    amount_change = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="待找零金额")
    amount_frozen = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="已支付未确认到账(含手续费)")
    desc = Column(String(255), nullable=False, server_default="", comment="归集账户 描述")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
