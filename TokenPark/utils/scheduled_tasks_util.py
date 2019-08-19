from apscheduler.schedulers.background import BackgroundScheduler

from models.robot_config_record_model import RobotConfigRecordModel
from services.game_bet_in_service import GameBetInServie
from tools.mysql_tool import MysqlTools
from utils.log import raise_logger


def action_bet(time, user_id):
    raise_logger(time)

    with MysqlTools().session_scope() as session:
        # 查询机器人配置纪录
        robot = session.query(RobotConfigRecordModel).filter(
            RobotConfigRecordModel.user_id == user_id,
            RobotConfigRecordModel.bet_plan_time == time,
            RobotConfigRecordModel.bet_status == 0
        ).first()

        if robot is None:
            return

        if GameBetInServie().robot_bet_in(
                {'game_instance_id': robot.game_instance_id,
                 'user_id': robot.user_id,
                 'conin_id': robot.pay_token,
                 'bet_amount': robot.bet_number,
                 'time_stamp': robot.time_stamp
                 }
        ) is False:
            raise_logger("机器人下注失败", "game_bet_in", "info")

        raise_logger("机器人下注成功", "game_bet_in", "info")


def add_task(dates):
    job_defaults = {
        'coalesce': False,
        'max_instances': 10
    }

    try:
        scheduler = BackgroundScheduler(job_defaults=job_defaults)
        for date in dates:
            print("date:", type(date))
            print("date:", date['time'])

            scheduler.add_job(action_bet, 'date', run_date=date['time'],
                              args=[date['time'], date['user_id']])
        scheduler.start()

    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print('Exit The Job!')
        return False

    return True
