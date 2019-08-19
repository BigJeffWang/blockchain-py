from sqlalchemy import Column, String, TEXT, Numeric
from models.base_model import BaseModel
from utils.util import get_decimal, generate_order_no


#归集记录表
class ForeignGatherRecordModel(BaseModel):
    __tablename__ = "foreign_gather_record"

    record_id = Column(String(32), unique=True, nullable=False, server_default="", default="", comment="归集记录id")
    coin_id = Column(String(128), nullable=False, server_default="", comment="货币id")
    public_address = Column(String(255), nullable=False, server_default="", comment="归集账户地址")
    conditions = Column(String(255), nullable=False, server_default="", comment="归集条件")
    purpose_amount = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="归集计算出的 目标金额(含手续费)")
    actual_amount = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="已上链 实际金额 累计")
    actual_fee = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="已上链 实际手续费 累计")
    gather_status = Column(String(8), nullable=False, server_default="0", comment="归集状态: 0-未归集, 1-归集中, 2-归集成功, 3-归集失败, 4-交易失败, 5-部分归集成功, 6-部分交易成功")
    process_record = Column(TEXT, comment="操作报错 业务不合法 交易处理报错等等 记录")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.record_id = generate_order_no()


