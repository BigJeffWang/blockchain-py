from sqlalchemy import Column, String
from models.base_model import BaseModel

"""
coin_id :  0       60     100000000
coin_name:  BTC     ETH    USDT
"""


# 币种表
class TokenCoinModel(BaseModel):
    __tablename__ = "token_coin"
    coin_id = Column(String(128), unique=True, nullable=False, server_default="", comment="货币id")
    coin_name = Column(String(128), nullable=False, server_default="", comment="货币代号")
    coin_des = Column(String(128), nullable=False, server_default="", comment="货币名称")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
