import sys
from pathlib import Path

pro_name = "TokenPark"
current_path = str(Path(__file__).resolve())
import_index = current_path.rfind(pro_name)
import_path = current_path[:import_index + len(pro_name)]
path_flag = True if not import_path in sys.path else False
if path_flag:
    sys.path.append(import_path)

from services.game_robot_service import GameRobotServie


class ManualCreateRobot(object):
    def create(self):
        return GameRobotServie().manual_creat_robot({"number": "1000"})


if __name__ == "__main__":
    ManualCreateRobot().create()
