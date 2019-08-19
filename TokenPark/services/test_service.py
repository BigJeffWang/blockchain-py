from services.base_service import BaseService
from tools.mysql_tool import MysqlTools
from utils.log import raise_logger


class TestService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def testing(self):
        # self.return_error(10000)
        # a = [0, 1]
        # print(a[2])
        raise Exception("test log ")
        # from models.token_node_conf_model import TokenNodeConfModel
        # with MysqlTools().session_scope() as session:
        #     session.query(TokenNodeConfModel).all()
        #     session.commit()

