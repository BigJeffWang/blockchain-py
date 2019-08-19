from sqlalchemy import Column, String, INTEGER, Numeric
from models.base_model import BaseModel

from sqlalchemy.dialects.mysql import TINYINT


# BTC-UTXO
class TxListBtcModel(BaseModel):
    __tablename__ = "tx_list_btc"

    tx_id = Column(String(32), nullable=False, server_default="", comment="DB的txid")
    tx_no = Column(String(255), nullable=False, server_default="", comment="链上的txid")
    vout = Column(INTEGER, nullable=False, comment="个人持有UTXO的索引")
    block_no = Column(INTEGER, nullable=False, default=0, comment="")
    value = Column(Numeric(36, 18), nullable=False, default=0, comment="充值金额")
    address = Column(String(255), nullable=False, server_default="", comment="充值地址 子钱包绑定账户的地址")
    cost_flag = Column(TINYINT(4), default=0, nullable=False, comment="是否已花费:1-是,0-否")
    source_status = Column(String(8), nullable=False, server_default="0", comment="来源: 0-线上, 1-线下")
    do_recharge_result = Column(String(255), nullable=False, server_default="", comment="回调 账户模块 do_recharge 结果记录")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
