from sqlalchemy import Column, String, Numeric
from sqlalchemy.dialects.mysql import TINYINT, INTEGER
from models.base_model import BaseModel


# Game配置模型
class GameDigitalTemplateModel(BaseModel):
    __tablename__ = "game_digital_template"

    game_title = Column(String(128), nullable=False, server_default="", comment="夺宝标题")

    reward_token = Column(INTEGER, nullable=False, server_default="0", comment="奖励币种")
    bet_token = Column(INTEGER, nullable=False, server_default="0", comment="投注币种")  # 注的基础单位
    bet_unit = Column(INTEGER, nullable=False, server_default="0", comment="投注单位")  # 最低加注额度
    reward_quantity = Column(INTEGER, nullable=False, server_default="0", comment="奖励数量")
    need_ceiling = Column(INTEGER, nullable=False, server_default="0", comment="总需上限")
    need_floor = Column(INTEGER, nullable=False, server_default="0", comment="总需下限")
    exceeded_ratio = Column(INTEGER, nullable=False, server_default="0", comment="超募比例")
    experience = Column(INTEGER, nullable=False, server_default="0", comment="体验金占比")
    handling_fee = Column(Numeric(21, 2), nullable=False, server_default="0", comment="手续费")
    merge_threshold = Column(INTEGER, nullable=False, server_default="0", comment="合买最低注数")

    support_token = Column(INTEGER, nullable=False, server_default="0", comment="支持币种")  # -1:全部
    template_status = Column(INTEGER, nullable=False, server_default="0", comment="模板状态")  # 0：停用   1：启用
    auto_release = Column(INTEGER, nullable=False, server_default="0", comment="是否自动发布")  # 0：否   1：是

    game_describe = Column(String(128), nullable=False, server_default="", comment="夺宝描述")

    phase_prefix = Column(String(128), nullable=False, server_default="", comment="期数前缀")
    phase_date = Column(String(128), nullable=False, server_default="", comment="期数日期")
    phase_serial = Column(String(128), nullable=False, server_default="", comment="期数序号")

    agreement_name = Column(String(128), nullable=False, server_default="", comment="协议名称")
    agreement = Column(String(128), nullable=False, server_default="", comment="协议")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
