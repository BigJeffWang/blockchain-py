from datetime import datetime

from sqlalchemy import Column, String, Numeric, BigInteger, Boolean
from sqlalchemy.dialects.mysql import INTEGER, MEDIUMTEXT, TINYINT

from models.base_model import BaseModel
from utils.util import get_decimal


# 合并参与记录表 merge_participate_in
class MergeParticipateInModel(BaseModel):
    __tablename__ = "merge_participate_in"

    participate_in_id = Column(BigInteger, unique=True, nullable=False, comment="发起参与id")
    initiate_user_id = Column(String(64), nullable=False, server_default="", comment="发起人用户id")
    game_instance_id = Column(BigInteger, nullable=False, comment="game实例id")
    # bet_token = Column(INTEGER, nullable=False, server_default="0", comment="投注币种")
    # bet_unit = Column(INTEGER, nullable=False, server_default="0", comment="投注单位")
    # bet_number = Column(INTEGER, nullable=False, server_default="0", comment="投注数量")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
