from sqlalchemy import Column, String, INTEGER
from models.base_model import BaseModel

from sqlalchemy.dialects.mysql import TINYINT


# 最新区块信息
class SyncBlockModel(BaseModel):
    __tablename__ = "sync_block"

    block_no = Column(INTEGER, nullable=False, comment="块高度")
    block_hash = Column(String(255), nullable=False, server_default="", comment="块hash")
    status = Column(TINYINT(4), nullable=False, default=0, comment="状态标识:1-已完成,0-未完成")
    coin_id = Column(String(128), nullable=False, server_default="", comment="货币id")
    process = Column(String(8), nullable=False, server_default="", comment="进程索引: 0-第1个进程, 1-第2个进程, 以此类推")
    trace_count = Column(String(255), nullable=False, server_default="0", comment="trace account actions")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
