from sqlalchemy import Column, String, BigInteger, INTEGER, Numeric
from sqlalchemy.dialects.mysql import TINYINT
from models.base_model import BaseModel


# 游戏 开奖 时 返回区块对应信息
class GameGetLotteryBlockInfoEosModel(BaseModel):
    __tablename__ = "game_get_lottery_block_info_eos"

    game_instance_id = Column(BigInteger, nullable=False, comment="game实例id")
    base_block_num = Column(INTEGER, unique=True, comment="满额时 基准的区块号 高度")
    base_time_stamp = Column(Numeric(21, 3), unique=True, comment="块生成时间 时间戳")
    block_num = Column(INTEGER, default=0, comment="开奖区块号 高度")
    block_hash = Column(String(64), nullable=False, server_default="", index=True, comment="开奖区块hash")
    time_stamp = Column(String(255), nullable=False, server_default="0000-00-00T00:00:00.000", comment="块生成时间 字符串")
    confirm_block_num = Column(INTEGER, default=0, comment="开奖区块号 高度")
    status = Column(TINYINT(4), nullable=False, default=0, comment="同步状态标识:1-已完成,0-未完成")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
