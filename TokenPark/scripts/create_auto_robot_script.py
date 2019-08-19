import sys
import time
from pathlib import Path

pro_name = "TokenPark"
current_path = str(Path(__file__).resolve())
import_index = current_path.rfind(pro_name)
import_path = current_path[:import_index + len(pro_name)]
path_flag = True if not import_path in sys.path else False
if path_flag:
    sys.path.append(import_path)

from tools.mysql_tool import MysqlTools
from models.robot_account_model import RobotAccountModel
from models.robot_config_record_model import RobotConfigRecordModel
from services.game_bet_in_service import GameBetInServie
from utils.log import Slog


class CreateAutoRobotScript(object):
    slog = Slog("robot_auto_bet")

    def createAutoRobot(self):
        return True


if __name__ == "__main__":
    CreateAutoRobotScript().createAutoRobot()
