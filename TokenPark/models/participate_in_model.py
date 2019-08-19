from datetime import datetime

from sqlalchemy import Column, String, Numeric, BigInteger, Boolean
from sqlalchemy.dialects.mysql import INTEGER, MEDIUMTEXT, TINYINT

from models.base_model import BaseModel
from utils.util import get_decimal


# 用户参与记录表 participate_in
class ParticipateInModel(BaseModel):
    __tablename__ = "participate_in"

    game_instance_id = Column(BigInteger, nullable=False, comment="game实例id")
    template_id = Column(BigInteger, nullable=False, server_default="0", comment="game模版id")
    game_serial = Column(String(64), nullable=False, server_default="", comment="投注期号")
    game_title = Column(String(255), nullable=False, server_default="", comment="夺宝标题")
    bet_token = Column(INTEGER, nullable=False, server_default="0", comment="投注币种")
    release_type = Column(TINYINT, nullable=False, server_default="0", comment="发布方式")

    user_id = Column(String(64), nullable=False, server_default="", comment="用户id")
    nick_name = Column(String(64), nullable=False, server_default="", default="", comment="昵称")
    channel = Column(String(64), nullable=False, server_default="",
                     comment="用户参与渠道")  # pc:1    wap:2   ios:3   android:4     BS:0
    pay_token = Column(INTEGER, nullable=False, server_default="0", comment="支付币种")
    bet_unit = Column(INTEGER, nullable=False, server_default="0", comment="投注单位")  # 表示每一注需要几个投注币
    bet_number = Column(INTEGER, nullable=False, server_default="0", comment="投注数量")
    pay_number = Column(Numeric(36, 18), nullable=False, default=get_decimal('0.000000000000000000'),
                        server_default=str(get_decimal('0.000000000000000000')), comment="支付金额")
    award_numbers = Column(MEDIUMTEXT, comment="获奖号码")
    win_number = Column(String(64), nullable=False, server_default="", comment="中奖号码")
    result = Column(TINYINT, nullable=False, server_default="0", comment="开奖结果")  # 0未中奖 1中奖

    user_type = Column(INTEGER, nullable=False, server_default="0", comment="用户类型")  # 真实用户:0    机器人:1

    chain_status = Column(INTEGER, nullable=False, server_default="0", comment="上链状态")  # 未上链:0    上链:1
    merge_id = Column(BigInteger, nullable=False, server_default="-1", comment="合并购买记录id")

    block_no = Column(INTEGER, nullable=False, server_default="0", comment="第三方区块号")
    received_time = Column(String(128), nullable=False, server_default="", comment="第三方区块hash值不可逆时间")
    bet_hash = Column(String(255), nullable=False, server_default="", comment="第三方区块上链不可逆hash值")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
