from sqlalchemy import Column, BigInteger, DateTime
from sqlalchemy import String, Numeric
from sqlalchemy.dialects.mysql import INTEGER

from models.base_model import BaseModel
from utils.util import get_decimal, generate_order_no


# 机器人配置纪录
class RobotConfigRecordModel(BaseModel):
    __tablename__ = "robot_config_record"

    user_id = Column(String(64), comment="用户ID", nullable=False, server_default="")
    nick_name = Column(String(64), nullable=False, server_default="", default="", comment="昵称")

    account_id = Column(String(64), unique=True, nullable=False, server_default="", comment="账户号")
    bet_number = Column(INTEGER, nullable=False, server_default="0", comment="投注数量")
    pay_token = Column(INTEGER, nullable=False, server_default="0", comment="支付币种")
    pay_number = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'),
                        server_default=str(get_decimal('0.000000000000000000')), comment="支付金额")

    game_instance_id = Column(BigInteger, nullable=False, comment="game实例id")
    game_serial = Column(String(64), nullable=False, server_default="", comment="投注期号")

    bet_plan_time = Column(DateTime, nullable=False, server_default="1970-01-01 00:00:00", comment="设定投注时间")

    bet_status = Column(INTEGER, nullable=False, server_default="0", comment="投注状态 0:待投入 1:已完成 2:作废 3:失败")

    time_stamp = Column(BigInteger, nullable=False, comment="时间戳 和 game config配套")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account_id = generate_order_no(k=44)
