from sqlalchemy import Column, String, Numeric
from sqlalchemy.dialects.mysql import INTEGER, TINYINT

from models.base_model import BaseModel
from utils.util import get_decimal


# dice对决记录表 dice_participate_in
class DiceParticipateInModel(BaseModel):
    __tablename__ = "dice_participate_in"

    dice_serial = Column(String(64), unique=True, nullable=False, server_default="", comment="对局编号")
    user_id = Column(String(64), nullable=False, server_default="", comment="参与用户id")
    user_dice = Column(TINYINT, nullable=False, server_default="-1", comment="用户出的是什么")  # 0石头 1剪刀 2布
    banker_dice = Column(TINYINT, nullable=False, server_default="-1", comment="庄家出的是什么")  # 0石头 1剪刀 2布
    channel = Column(String(64), nullable=False, server_default="", comment="用户参与渠道")  # pc:1 wap:2 ios:3 android:4 BS:0
    bet_number = Column(Numeric(21, 4), nullable=False, default=get_decimal('0.0000'),
                        server_default=str(get_decimal('0.0000')), comment="投注数量")
    bet_token = Column(INTEGER, nullable=False, server_default="0", comment="投注币种id")
    reward_token = Column(INTEGER, nullable=False, server_default="0", comment="奖励币种id")
    reward_quantity = Column(Numeric(21, 4), nullable=False, default=get_decimal('0.0000'),
                             server_default=str(get_decimal('0.0000')), comment="奖励数量")
    dice_result = Column(TINYINT, nullable=False, server_default="-1", comment="对局结果")  # 0用户胜 1平局 2庄家胜 -1未知
    dice_timestamp = Column(String(255), nullable=False, server_default="0000-00-00T00:00:00.000", comment="对局时间")
    block_timestamp = Column(String(255), nullable=False, server_default="0000-00-00T00:00:00.000", comment="出块时间")
    block_no = Column(INTEGER, nullable=False, server_default="0", comment="开奖区块号 高度")
    block_hash = Column(String(64), nullable=False, server_default="", comment="开奖区块hash")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
