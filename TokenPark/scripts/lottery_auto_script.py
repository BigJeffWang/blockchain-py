import sys
from pathlib import Path

pro_name = "TokenPark"
current_path = str(Path(__file__).resolve())
import_index = current_path.rfind(pro_name)
import_path = current_path[:import_index + len(pro_name)]
path_flag = True if not import_path in sys.path else False
if path_flag:
    sys.path.append(import_path)

from tools.mysql_tool import MysqlTools
from services.game_model_service import GamePublishLotteryServie
from models.game_digital_instance_model import GameDigitalInstanceModel
from utils.log import Slog


class LotteryAutoScript(object):
    slog = Slog("lottery_auto")

    def autoLottery(self):
        with MysqlTools().session_scope() as session:
            # 查询项目是否需要开奖
            models = session.query(GameDigitalInstanceModel).filter(GameDigitalInstanceModel.status == 1).all()
            if models is None or len(models) <= 0:
                return

            for model in models:
                GamePublishLotteryServie().checkGameSoldOut(str(model._id))


if __name__ == "__main__":
    LotteryAutoScript().autoLottery()
