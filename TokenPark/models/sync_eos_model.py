from sqlalchemy import Column, String, INTEGER, Numeric
from models.base_model import BaseModel

from sqlalchemy.dialects.mysql import TINYINT


# 最新区块信息
class SyncEosModel(BaseModel):
    __tablename__ = "sync_eos"

    block_num = Column(INTEGER, unique=True, nullable=False, comment="区块号 高度")
    block_hash = Column(String(255), nullable=False, server_default="", comment="区块hash")
    time_stamp = Column(String(255), nullable=False, server_default="0000-00-00T00:00:00.000", comment="块生成时间 字符串")
    time_stamp_decimal = Column(Numeric(21, 3), unique=True, comment="块生成时间 时间戳")
    previous = Column(String(255), nullable=False, server_default="", comment="父区块hash")
    status = Column(TINYINT(4), nullable=False, default=0, comment="同步状态标识:1-已完成,0-未完成")
    process = Column(String(8), nullable=False, server_default="", comment="进程索引: 0-第1个进程, 1-第2个进程, 以此类推")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
