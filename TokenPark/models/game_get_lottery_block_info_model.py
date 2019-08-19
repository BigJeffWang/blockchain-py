from sqlalchemy import Column, String, BigInteger

from models.base_model import BaseModel


# 游戏 开奖 时 返回区块对应信息
class GameGetLotteryBlockInfoModel(BaseModel):
    __tablename__ = "game_get_lottery_block_info"

    game_instance_id = Column(BigInteger, nullable=False, comment="game实例id")
    time_stamp = Column(BigInteger, nullable=False, comment="获取区块时 传入的时间戳")
    block_hash = Column(String(64), nullable=False, server_default="", comment="区块hash值")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
