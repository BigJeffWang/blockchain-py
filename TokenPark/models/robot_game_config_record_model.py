from sqlalchemy import BigInteger, DateTime
from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import INTEGER

from models.base_model import BaseModel
from utils.util import generate_order_no


# 机器人 游戏配置纪录
class RobotGameConfigRecordModel(BaseModel):
    __tablename__ = "robot_game_config_record"

    game_instance_id = Column(BigInteger, nullable=False, comment="game实例id")
    game_serial = Column(String(64), nullable=False, server_default="", comment="项目期号")

    robot_number = Column(INTEGER, nullable=False, server_default="0", comment="机器人数量")
    total_bet_number = Column(INTEGER, unique=False, nullable=False, server_default="0", comment="总投注数量")

    start_of_plan_time = Column(DateTime, nullable=False, server_default="1970-01-01 00:00:00", comment="计划开始时间")
    end_of_plan_time = Column(DateTime, nullable=False, server_default="1970-01-01 00:00:00", comment="计划结束时间")
    end_of_real_time = Column(DateTime, nullable=False, server_default="1970-01-01 00:00:00", comment="实际结束时间")

    status = Column(INTEGER, nullable=False, server_default="0",
                    comment="状态 0:待执行 1:进行中 2:已完成 3:自动终止 4:手动终止")

    robot_bet_type = Column(INTEGER, nullable=False, server_default="1", comment="投入方式")  # 0:自动 1:手动

    created_user_id = Column(String(64), nullable=False, comment="创建用户id")  # 后台登陆用户id

    time_stamp = Column(BigInteger, nullable=False, comment="时间戳 和 game config配套")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account_id = generate_order_no(k=44)
