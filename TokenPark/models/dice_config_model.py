from sqlalchemy import Column, String, Numeric, BigInteger, Boolean
from sqlalchemy.dialects.mysql import INTEGER, MEDIUMTEXT, TINYINT

from models.base_model import BaseModel

# 猜拳游戏相关配置
from utils.util import get_decimal


class DiceConfigModel(BaseModel):
    __tablename__ = "dice_config"

    support_token_id = Column(INTEGER, nullable=False, server_default="-1", comment="支持币种id")
    support_token_name = Column(String(64), nullable=False, server_default="", comment="支持币种name")
    default_bet_volume = Column(Numeric(21, 4), nullable=False, default=get_decimal('0.0000'),
                                server_default=str(get_decimal('0.0000')), comment="默认投注量")
    lower_bet_volume = Column(Numeric(21, 4), nullable=False, default=get_decimal('0.0000'),
                              server_default=str(get_decimal('0.0000')), comment="投注量下限")
    ceiling_bet_volume = Column(Numeric(21, 4), nullable=False, default=get_decimal('0.0000'),
                                server_default=str(get_decimal('0.0000')), comment="投注量上限")
    handling_fee = Column(INTEGER, nullable=False, server_default="0", comment="手续费率")
    status = Column(TINYINT, nullable=False, server_default="0", comment="支持币种状态")   # 0不可用  1可用

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
