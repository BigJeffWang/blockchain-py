from sqlalchemy import Column, String, Numeric, DateTime, INTEGER
from models.base_model import BaseModel
from utils.util import get_decimal, generate_order_no
from sqlalchemy.dialects.mysql import TINYINT


class AccountChangeRecordModel(BaseModel):
    __tablename__ = "account_change_record"

    change_type_1 = '1'  # 充值
    change_type_2 = '2'  # 提现暂时冻结资产
    change_type_3 = '3'  # 夺宝
    change_type_4 = '4'  # 线上提现成功
    change_type_5 = '5'  # 夺宝后赢币
    change_type_6 = '6'  # 提现失败系统反还
    change_type_7 = '7'  # 线下提现成功
    change_type_13 = '13'  # 取消下注

    change_type_20 = '20'  # 新用户首次抽奖
    change_type_21 = '21'  # 新用户首次充值
    change_type_22 = '22'  # 邀请用户成功
    change_type_23 = '23'  # 受邀用户充值成功

    change_type_31 = '31'  # 扣款
    change_type_32 = '32'  # 返还
    change_type_33 = '33'  # 中奖

    # 即时开类型
    change_type_41 = '41'  # 即时开中奖
    change_type_42 = '42'  # 即时开没中奖

    # 第三方充值
    change_type_51 = '51'  # USDT 充值

    change_type_withdraw_all = '999'  # 提现的占位字段，表示包含提现中、提现完成、提现失败三个字段，不可存入数据库中
    change_type_withdraw_success = '998'  # 所有提现完成的状态，不可存入数据库中
    change_type_gold_experience = '997'  # 所有体验金的状态

    account_change_record_id = Column(String(32), unique=True, nullable=False, server_default="", comment="记录id")
    account_id = Column(String(64), nullable=False, server_default="", comment="账户号")
    account_token_id = Column(String(64), nullable=False, server_default="", comment="accounttoken主键")
    token_id = Column(String(255), nullable=False, server_default="", comment="货币名称BTC、ETH、ETC、EOS……")

    change_type = Column(TINYINT(1), nullable=False, server_default="0", comment="变化类型")
    change_amount = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment='币数')
    change_fee = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment='服务费')
    change_number = Column(INTEGER, nullable=False, server_default="1", comment="变化数量")

    # 由于本表过大，所以不存着几个无用字段，具体字段的变化可以去其对应的record表中查询。对于提现，应该是冻结时生成记录，提现实施，update 该行数据
    # total_recharge = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment='累计充值')
    # total_withdraw = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment='累计提现')
    # total_withdraw_fee = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment='累计提现手续费')
    balance = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment='余额')
    frozon_amount = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment='冻结金额')
    investment_amount = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'), server_default=str(get_decimal('0.000000000000000000')), comment='已投金额')
    # 对于充值，则是打入token的地址，对于提现则是提出token的地址, 对于游戏则是期号
    token_address = Column(String(255), nullable=False, server_default="", default="", comment="收款地址")
    memo = Column(String(512), nullable=False, server_default="", default="", comment="memo")

    # 此操作的开始和结束时间
    begin_time = Column(DateTime, nullable=False, server_default="0000-00-00 00:00:00", comment="开始时间")
    finish_time = Column(DateTime, nullable=False, server_default="0000-00-00 00:00:00", comment="完成时间")
    # 交易单号，用于用户根据一条账户变换记录，反查交易详情
    transaction_id = Column(String(128), nullable=False, server_default="", default="", comment="到账交易号")
    source = Column(String(64), nullable=False, server_default="", comment="资金来源")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account_change_record_id = generate_order_no()

    @staticmethod
    def get_all_show_change_type():
        return [
            AccountChangeRecordModel.change_type_1,
            AccountChangeRecordModel.change_type_3,
            AccountChangeRecordModel.change_type_13,
            AccountChangeRecordModel.change_type_5,
            AccountChangeRecordModel.change_type_withdraw_all,
            AccountChangeRecordModel.change_type_withdraw_success,
            AccountChangeRecordModel.change_type_gold_experience,
            AccountChangeRecordModel.change_type_31,
            AccountChangeRecordModel.change_type_32,
            AccountChangeRecordModel.change_type_33,
            AccountChangeRecordModel.change_type_41,
            AccountChangeRecordModel.change_type_42,
            AccountChangeRecordModel.change_type_51
        ]

    @staticmethod
    def get_all_withdraw_change_type():
        return [
            AccountChangeRecordModel.change_type_2,
            AccountChangeRecordModel.change_type_4,
            AccountChangeRecordModel.change_type_6,
            AccountChangeRecordModel.change_type_7,
        ]

    @staticmethod
    def get_all_withdraw_success_type():
        return [
            AccountChangeRecordModel.change_type_4,
            AccountChangeRecordModel.change_type_7,
        ]

    @staticmethod
    def get_all_gold_experience_type():
        return [
            AccountChangeRecordModel.change_type_20,
            AccountChangeRecordModel.change_type_21,
            AccountChangeRecordModel.change_type_22,
            AccountChangeRecordModel.change_type_23,
        ]
