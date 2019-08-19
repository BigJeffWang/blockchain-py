from sqlalchemy import Column, String, Numeric, DateTime
from models.base_model import BaseModel
from utils.util import get_decimal, generate_order_no
from sqlalchemy.dialects.mysql import TINYINT


class AccountWithdrawRecordModel(BaseModel):
    __tablename__ = "account_withdraw_record"

    status_1 = '1'  # 进行中
    status_2 = '2'  # 成功
    status_3 = '3'  # 失败

    account_withdraw_record_id = Column(String(32), unique=True, nullable=False, server_default="", default="", comment="记录id")
    account_change_record_id = Column(String(64), nullable=False, server_default="", default="", comment="账户变换记录id")
    account_id = Column(String(64), nullable=False, server_default="", default="", comment="账户号")
    user_id = Column(String(64), comment="用户ID", nullable=False, server_default="")
    token_address = Column(String(255), nullable=False, server_default="", default="", comment="对方收款地址")
    memo = Column(String(512), nullable=False, server_default="", default="", comment="memo")
    withdraw_amount = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment="应到账token")
    withdraw_fee = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment="服务费")
    transaction_id = Column(String(128), nullable=False, server_default="", default="", comment="到账交易号")
    token_id = Column(String(255), nullable=False, server_default="", default="", comment="货币名称BTC、ETH、ETC、EOS……")
    status = Column(TINYINT(1), nullable=False, server_default=status_1, default=status_1, comment="状态")
    begin_time = Column(DateTime, nullable=False, server_default="0000-00-00 00:00:00", comment="开始时间")
    finish_time = Column(DateTime, nullable=False, server_default="0000-00-00 00:00:00", comment="完成时间")

    # 记录此次操作的账户状态
    balance = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment='余额')
    frozon_amount = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment='冻结金额')
    investment_amount = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment='已投金额')
    total_recharge = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment='累计充值')
    total_withdraw = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment='累计提现')
    total_withdraw_fee = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment='累计提现手续费')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account_withdraw_record_id = generate_order_no()


