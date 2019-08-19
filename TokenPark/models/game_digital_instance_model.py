from sqlalchemy import Column, String, DateTime, BigInteger, Numeric
from sqlalchemy.dialects.mysql import TINYINT, INTEGER

from models.base_model import BaseModel


# 发布游戏纪录 game_digital_instance
class GameDigitalInstanceModel(BaseModel):
    __tablename__ = "game_digital_instance"

    template_id = Column(BigInteger, comment="模板id")
    game_serial = Column(String(64), unique=True, nullable=False, server_default="", comment="期号")
    game_title = Column(String(255), nullable=False, server_default="", comment="夺宝标题")

    bet_token = Column(INTEGER, nullable=False, server_default="0", comment="投注币种id")  # 0:全部 1:BTC  2:USDT   3:ETH
    bet_unit = Column(INTEGER, nullable=False, server_default="0", comment="投注单位")  # 表示每一注需要几个投注币
    bet_number = Column(INTEGER, nullable=False, server_default="0", comment="在投注数量")  # 当前已经投注的数量
    participation = Column(INTEGER, nullable=False, server_default="0", comment="参与人数")  # 当前版本表示game被参与次数

    need = Column(INTEGER, nullable=False, server_default="0", comment="总需数")  # 满额所需的投注数
    status = Column(TINYINT, nullable=False, server_default="0", comment="状态")  # 0:夺宝中   1:待揭晓  2:已完结

    support_token = Column(INTEGER, nullable=False, server_default="0", comment="支持币种")  # -1:全部
    reward_token = Column(INTEGER, nullable=False, server_default="1", comment="奖励币种id")  # 1:BTC  2:USDT   3:ETH
    reward_quantity = Column(INTEGER, nullable=False, server_default="0", comment="奖励数量")

    release_time = Column(DateTime, nullable=False, server_default="1970-01-01 00:00:00", comment="发布时间")
    full_load_time = Column(DateTime, nullable=False, server_default="1970-01-01 00:00:00", comment="满额时间")
    lottery_time = Column(DateTime, nullable=False, server_default="1970-01-01 00:00:00", comment="开奖时间")
    release_type = Column(TINYINT, nullable=False, server_default="0", comment="发布方式")  # 0:手动  1:自动

    handling_fee = Column(Numeric(21, 2), nullable=False, server_default="0.00", comment="手续费")
    merge_threshold = Column(INTEGER, nullable=False, server_default="0", comment="合买最低注数")

    game_describe = Column(String(255), nullable=False, server_default="", comment="夺宝描述")
    chain_status = Column(INTEGER, nullable=False, server_default="0", comment="上链状态")  # 未上链:0    上链:1

    experience = Column(INTEGER, nullable=False, server_default="0", comment="体验金占比")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

