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


class RobotAutoBetScript(object):
    slog = Slog("robot_auto_bet")

    def autoBet(self):
        now = int(time.time())
        time_struct = time.localtime(now)
        str_time = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)

        self.slog.info("robots  str_time" + str(str_time))

        with MysqlTools().session_scope() as session:
            # 查询机器人配置纪录
            robots = session.query(RobotConfigRecordModel).filter(RobotConfigRecordModel.bet_status == 0,
                                                                  RobotConfigRecordModel.bet_plan_time <= str_time).all()

            if robots is None or len(robots) <= 0:
                self.slog.info("无机器人自动下注配置")
                return

            self.slog.info("robots:" + str(len(robots)))

            for robot in robots:
                self.slog.info("robots_id:" + str(robot.user_id))
                self.slog.info("game_instance_id:" + str(robot.game_instance_id))
                result = GameBetInServie().robot_bet_in(
                    {'game_instance_id': robot.game_instance_id,
                     'user_id': robot.user_id,
                     'conin_id': robot.pay_token,
                     'bet_amount': robot.bet_number,
                     'time_stamp': robot.time_stamp
                     })

                self.slog.info("robots  result:" + str(result))

                if isinstance(result, bool):
                    if result is False:
                        self.slog.info("机器人下注失败script:", str(result) + "----" + str(robot.user_id))

                        user = session.query(RobotAccountModel).filter(
                            RobotAccountModel.user_id == robot.user_id).with_for_update().first()
                        user.status = 0

                        robot.bet_status = 3
                        session.commit()
                    else:
                        self.slog.info("机器人下注成功script:", robot.user_id)

                else:
                    self.slog.info("机器人下注失败script:", str(result) + "----" + str(robot.user_id))

                    user = session.query(RobotAccountModel).filter(
                        RobotAccountModel.user_id == robot.user_id).with_for_update().first()
                    user.status = 0

                    robot.bet_status = 3
                    session.commit()


if __name__ == "__main__":
    RobotAutoBetScript().autoBet()
