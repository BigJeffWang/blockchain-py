from sqlalchemy import Column, String, BigInteger

from models.base_model import BaseModel


# 游戏 奖号表
class GameNumbersSetModel(BaseModel):
    __tablename__ = "game_numbers_set"

    game_serial = Column(String(64), nullable=False, server_default="", comment="期号")
    number = Column(BigInteger, nullable=False, comment="奖号")
    time_stamp = Column(BigInteger, nullable=False, default=0, comment="参与时间戳")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
