from sqlalchemy import Column, String, TEXT, Numeric, DateTime
from models.base_model import BaseModel
from utils.util import get_decimal


class ForeignWithdrawOrderRecordModel(BaseModel):
    __tablename__ = "foreign_withdraw_order_record"
    order_no = Column(String(32), unique=True, nullable=False, server_default="", comment="流水记录单号")
    relate_flow_no = Column(String(32), nullable=False, server_default="", comment="记录 提现流水单号 或者 归集流水单号")
    req_no = Column(String(32), nullable=False, server_default="", comment="用户请求单号")
    account_id = Column(String(64), nullable=False, server_default="", comment="账户id")
    coin_id = Column(String(128), nullable=False, server_default="", comment="货币id")
    from_address = Column(String(255), server_default="", comment="出款地址")  # 提现:出款地址/归集地址,归集:出款地址/子账户地址
    withdraw_address = Column(String(255), server_default="", comment="提现地址")  # 提现:收款地址/提现地址,归集:收款地址/归集地址
    withdraw_amount = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="预计提现 金额(含手续费)")
    withdraw_fee = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="预计提现 手续费")
    withdraw_actual_amount = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="提现实际到账 金额")
    withdraw_actual_fee = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="提现实际到账 手续费")
    withdraw_consume_total_fee = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="提现消耗的 手续费累计,但是交易未上块")
    amount_change = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="找零金额 eth交易剩余手续费")
    withdraw_gas_price = Column(Numeric(36, 18), default=get_decimal('0', 18), nullable=False, server_default="0.000000000000000000", comment="提现手续费单价")
    withdraw_type = Column(String(8), nullable=False, server_default="", comment="提现类型: 0-用户提现, 1-用户中奖, 2-归集, 3-归集转归集")
    withdraw_status = Column(String(8), nullable=False, server_default="0", comment="提现状态: 0-未交易, 1-提现中, 2-提现成功, 3-提现失败, 4-交易失败,5-提现拒绝(审核拒绝)")
    audit_status = Column(String(8), nullable=False, server_default="0", comment="审核状态: 0-待审核, 1-审核通过, 2-审核拒绝")
    source_status = Column(String(8), nullable=False, server_default="0", comment="来源: 0-线上, 1-线下")
    do_withdraw_result = Column(String(255), nullable=False, server_default="", comment="回调 账户模块 do_withdraw 结果记录")
    expect_at = Column(DateTime, nullable=False, server_default="0000-00-00 00:00:00", comment="期望到账时间")
    process_record = Column(TEXT, comment="操作报错 业务不合法 交易处理报错等等 记录")
    transfer_at = Column(DateTime, nullable=False, server_default="0000-00-00 00:00:00", comment="转账操作时间")
    audit_at = Column(DateTime, nullable=False, server_default="0000-00-00 00:00:00", comment="审核通过时间")
    remark = Column(TEXT, comment="提现审核拒绝原因")
    audit_user = Column(String(255), nullable=False, server_default="", comment="审核人")
    operation_user = Column(String(255), nullable=False, server_default="", comment="操作人(特指线下转账录入tx的操作)")
    confirm_at = Column(DateTime, nullable=False, server_default="0000-00-00 00:00:00", comment="到账时间")
    memo = Column(String(512), nullable=False, server_default="", comment="备注")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
