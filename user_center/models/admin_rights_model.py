from sqlalchemy import Column, Integer, String
from models.base_model import BaseModel


# 后台权限
class AdminRightsModel(BaseModel):

    __tablename__ = "admin_rights"

    rights_id = Column(String(4), nullable=False, unique=True, comment="权限ID", server_default="")
    name = Column(String(64), nullable=False, comment="权限名", server_default="")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

