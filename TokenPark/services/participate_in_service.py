from models.participate_in_model import ParticipateInModel
from services.base_service import BaseService


class ParticipateInService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # 查询对应项目 game_instance_id 参与记录
    def search_model(self, session, game_instance_id):
        return session.query(ParticipateInModel).filter(ParticipateInModel.game_instance_id == game_instance_id).all()

