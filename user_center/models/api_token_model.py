from sqlalchemy import Column, String, DateTime
from models.base_model import BaseModel
from sqlalchemy.dialects.mysql import TINYINT


class ApiTokenModel(BaseModel):
    __tablename__ = "api_token"

    source_type_1 = '1'  # pc
    source_type_2 = '2'  # wap
    source_type_3 = '3'  # iphone
    source_type_4 = '4'  # android

    user_id = Column(String(64), comment="用户ID", nullable=False, server_default="")
    token_type = Column(String(32), comment="token类型 AccessToken/RefreshToken", nullable=False, server_default="")
    token = Column(String(128), comment="Token", nullable=False, server_default="")
    expire_at = Column(DateTime, comment="Token过期时间", nullable=False, server_default="0000-00-00 00:00:00")
    user_type = Column(TINYINT(4), nullable=False, server_default="0", comment="用户类型，依据commonsetting设定")
    source = Column(TINYINT(4), nullable=False, comment="用户来源", server_default=source_type_1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_all_source_type():
        return [
            ApiTokenModel.source_type_1,
            ApiTokenModel.source_type_2,
            ApiTokenModel.source_type_3,
            ApiTokenModel.source_type_4,
        ]
