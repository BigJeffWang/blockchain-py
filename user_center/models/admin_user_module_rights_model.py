from sqlalchemy import Column, String
from models.base_model import BaseModel
from utils import generate_order_no


# 后台用户模块权限
class AdminUserModuleRightsModel(BaseModel):

    __tablename__ = "admin_user_module_rights"

    user_mudule_rights_id = Column(String(32), nullable=False, unique=True, doc="主键", server_default="")
    user_id = Column(String(64), nullable=False, doc="用户ID", server_default="")
    module_id = Column(String(32), nullable=False, comment="模块ID", server_default="")
    rights_id_list = Column(String(64), nullable=False, comment="权限列表", server_default="")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_mudule_rights_id = generate_order_no()
