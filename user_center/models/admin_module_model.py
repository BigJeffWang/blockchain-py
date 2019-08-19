from sqlalchemy import Column, Integer, String
from models.base_model import BaseModel
from utils import generate_order_no


# 后台模块
class AdminModuleModel(BaseModel):

    __tablename__ = "admin_module"

    origin_module_level = '0'  # 最高一级的模块等级

    module_id = Column(String(32), nullable=False, unique=True, comment="模块ID", server_default="")
    name = Column(String(64), nullable=False, comment="模块名", server_default="")
    module_url = Column(String(128), nullable=False, comment="模块地址", server_default="")
    # level 格式是id_id_id从高到低列出level的父系关系,如2_6_18
    level = Column(String(64), nullable=False, comment="父模块ID", server_default=origin_module_level, default=origin_module_level)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

