from sqlalchemy import Column, String, Numeric
from sqlalchemy.dialects.mysql import TINYINT, CHAR, INTEGER
from models.base_model import BaseModel
from utils.util import get_decimal, generate_order_no


class UserAccountTokenModel(BaseModel):
    __tablename__ = "user_account_token"

    status_on = '1'  # 在用
    status_off = '0'  # 注销

    account_token_id = Column(String(64), unique=True, nullable=False, server_default="", comment="本表主键")
    account_id = Column(String(64), nullable=False, server_default="", comment="账户号")
    user_id = Column(String(64), comment="用户ID", nullable=False, server_default="")
    token_id = Column(String(255), nullable=False, server_default="", comment="货币名称BTC、ETH、ETC、EOS……")

    # --------------------------------------------------
    # 公式是用来对账的，因此实际代码计算的是有严禁用这个公式
    # 充值 - 提现 - 手续费 - 冻结金额 = 余额 + 已投金额
    # --------------------------------------------------
    total_recharge = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment='累计充值')
    total_withdraw = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment='累计提现')
    total_withdraw_fee = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment='累计提现手续费')

    balance = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment='余额')
    frozon_amount = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment='冻结金额')
    investment_amount = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment='已投金额')
    # 用户充值地址
    sub_public_address = Column(String(255), nullable=False, server_default="", comment="子地址")
    memo = Column(String(512), nullable=False, server_default="", comment="memo 信息")

    # 状态
    status = Column(TINYINT(1), nullable=False, server_default=str(status_on), comment="状态 0）注销 1）在用")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account_token_id = generate_order_no(k=44)

    def recharge(self, amount):
        # 充值
        if amount < 0:
            return False
        if self.total_recharge is None:
            self.total_recharge = amount
        else:
            self.total_recharge += amount

        if self.balance is None:
            self.balance = amount
        else:
            self.balance += amount
        return True

    def apply_withdraw(self, amount, fee):
        # 提现暂时冻结资产
        if amount < 0:
            return False
        if fee < 0:
            return False
        all_amount = amount + fee
        # 转账费用从转账金额中扣除
        if self.balance < all_amount:
            return False
        self.balance -= all_amount
        self.frozon_amount += all_amount
        return True

    def bet(self, amount):
        # 下注
        if amount < 0:
            return False
        if self.balance < amount:
            return False
        self.balance -= amount
        self.investment_amount += amount
        return True

    def cancel_bet(self, amount):
        # 取消下注
        if amount < 0:
            return False
        if self.investment_amount < amount:
            return False
        self.balance += amount
        self.investment_amount -= amount
        return True

    def do_withdraw(self, amount, fee, return_balance=0):
        # 提现实施
        if amount < 0:
            return False
        if fee < 0:
            return False
        if return_balance < 0:
            return False
        all_amount = amount + fee + return_balance
        if self.frozon_amount < all_amount:
            return False
        self.frozon_amount -= all_amount
        self.total_withdraw += amount
        self.total_withdraw_fee += fee
        self.balance += return_balance
        return True

    def increase_amount(self, amount):
        # 系统inr(如下注后赢币)
        if amount < 0:
            return False
        self.balance += amount
        return True

    def refuse_withdraw(self, amount, fee, return_balance=0):
        # 提现失败系统反还
        if amount < 0:
            return False
        if fee < 0:
            return False
        if return_balance < 0:
            return False
        all_amount = amount + fee + return_balance
        if self.frozon_amount < all_amount:
            return False
        self.frozon_amount -= all_amount
        self.balance += all_amount
        return True


