from sqlalchemy import Column, String, Numeric, Integer
from models.base_model import BaseModel
from utils.util import get_decimal


# 配置表 确认侦听最后区块数 手续费 提现几天失败
# btc,utxo数量与体积:1≈226,2≈374,3≈522,4≈670
class TokenConfModel(BaseModel):
    __tablename__ = "token_conf"
    coin_id = Column(String(128), unique=True, nullable=False, server_default="", comment="货币id")
    confirm_last_block_num = Column(String(8), nullable=False, server_default="", comment="确认最后区块数")
    confirm_last_err_days = Column(String(8), nullable=False, server_default="", comment="确认最后提现失败天数")
    withdraw_fee = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="归集手续费单价/kb")
    gas_lag = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="app用户体现手续费单价-慢")
    gas_routine = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="中")
    gas_prior = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="快")
    gas_limit = Column(Integer, nullable=False, server_default="1", comment="系数:限制可花费gas总量 最多可以是多少个gas price")
    gather_gas = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="归集 计算的最低手续费")
    gather_minimum_amount = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="归集 最小可归集金额")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
