from sqlalchemy import Column, String, TEXT, Numeric
from models.base_model import BaseModel
from utils.util import get_decimal, generate_order_no


# 批量提现记录表
class ForeignMultiWithdrawRecordModel(BaseModel):
    __tablename__ = "foreign_multi_withdraw_record"

    record_id = Column(String(32), unique=True, nullable=False, server_default="", default="", comment="提现记录id")
    coin_id = Column(String(128), nullable=False, server_default="", comment="货币id")
    from_address = Column(String(255), nullable=False, server_default="", comment="出款地址")
    amount = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="提现总金额(含手续费)")
    amount_change = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="找零金额")
    gas = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="提现总手续费")
    verified_amount = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="已经验证的 提现总金额里的数额")
    verified_gas = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="已经验证的 提现总手续费的数额")
    withdraw_status = Column(String(8), nullable=False, server_default="0",
                             comment="提现状态: 0-未交易, 1-提现中, 2-提现成功, 3-提现失败, 4-交易失败, 5-部分提现成功, 6-部分交易成功")
    process_record = Column(TEXT, comment="操作报错 业务不合法 交易处理报错等等 记录")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.record_id = generate_order_no()
