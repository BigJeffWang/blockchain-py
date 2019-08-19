from sqlalchemy import Column, String, INTEGER, Numeric
from models.base_model import BaseModel

from sqlalchemy.dialects.mysql import TINYINT,TEXT


# BTC-UTXO-listening
class TxListeningBtcModel(BaseModel):
    __tablename__ = "tx_listening_btc"

    order_no = Column(String(32), unique=True, nullable=False, server_default="", comment="DBid")
    record_no = Column(String(32), nullable=False, server_default="", comment="是批量转账:multi_withdraw表record_id,非批量转账:withdraw表order_no")
    block_no = Column(INTEGER, nullable=False, default=0, comment="")
    tx_no = Column(String(255), unique=True, nullable=False, server_default="", comment="链上的txid")
    tx_nos = Column(TEXT, comment="本次交易使用的txid")
    withdraw_type = Column(String(8), nullable=False, server_default="", comment="提现类型: 0-用户提现, 1-用户中奖, 2-归集, 3-归集转归集")
    source_status = Column(String(8), nullable=False, server_default="0", comment="来源: 0-线上, 1-线下")
    listen_flag = Column(TINYINT(4), default=1, nullable=False, comment="是否需监听:1-是,0-否")
    multi_flag = Column(TINYINT(4), default=0, nullable=False, comment="是否批量转账(多个to_address):1-是,0-否")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
