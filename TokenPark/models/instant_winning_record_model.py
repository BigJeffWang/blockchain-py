from sqlalchemy import Column, String, BigInteger
from sqlalchemy.dialects.mysql import INTEGER

from models.base_model import BaseModel


class InstantWinningRecordModel(BaseModel):
    __tablename__ = "instant_winning_record"

    game_instance_id = Column(BigInteger, nullable=False, comment="game实例id")
    game_serial = Column(String(64), nullable=False, server_default="", comment="期号")

    bet_serial = Column(String(64), nullable=False, server_default="", comment="中奖号码")
    bet_hash = Column(String(255), nullable=False, server_default="", comment="第三方区块上链不可逆hash值")

    reward_token = Column(INTEGER, nullable=False, server_default="1", comment="奖励币种id")
    reward_quantity = Column(INTEGER, nullable=False, server_default="0", comment="奖励数量")

    user_id = Column(String(64), nullable=False, server_default="", comment="用户ID")
    bet_token = Column(INTEGER, nullable=False, server_default="0", comment="投注币种id")
    bet_number = Column(INTEGER, nullable=False, server_default="0", comment="用户投注数量")

    user_type = Column(INTEGER, nullable=False, server_default="0", comment="用户类型")  # 真实用户:0    机器人:1

    block_no = Column(INTEGER, nullable=False, server_default="0", comment="第三方区块号")
    timestamp = Column(String(128), nullable=False, server_default="", comment="第三方区块生成时间")
    received_time = Column(String(128), nullable=False, server_default="", comment="第三方区块hash值不可逆时间")
    block_type = Column(String(128), nullable=False, server_default="", comment="第三方区块类型")

    participation = Column(INTEGER, nullable=False, server_default="0", comment="参与人数")
    chain_status = Column(INTEGER, nullable=False, server_default="0", comment="上链状态")

    merge_id = Column(BigInteger, nullable=False, server_default="-1", comment="合并购买记录id")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
