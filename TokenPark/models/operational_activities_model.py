from sqlalchemy import Column, String, Numeric
from sqlalchemy.dialects.mysql import TEXT

from models.base_model import BaseModel
from utils.util import get_decimal


# 运营活动
class OperationalActivitiesModel(BaseModel):
    __tablename__ = "operational_activities"

    user_id = Column(String(64), comment="用户ID", nullable=False,
                     server_default="")
    operational_activities_id = Column(String(128), comment="运营活动ID",
                                       nullable=False, server_default="")
    operational_activities_name = Column(String(128), comment="运营活动简称",
                                         nullable=False, server_default="")
    labels = Column(TEXT, comment="标签")

    amount = Column(Numeric(16, 2), default=get_decimal('0', 18),
                    nullable=False, server_default="0.00", comment="奖励金额")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
