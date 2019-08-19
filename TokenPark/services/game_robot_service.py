import datetime
import json
import random
import string
import time

from models.game_digital_instance_model import GameDigitalInstanceModel
from models.robot_account_model import RobotAccountModel
from models.robot_config_record_model import RobotConfigRecordModel
from models.robot_game_config_record_model import RobotGameConfigRecordModel
from models.robot_info_lib_model import RobotInfoLibModel
from services.base_service import BaseService
from tools.mysql_tool import MysqlTools
from utils.log import raise_logger
from utils.util import get_offset_by_page, get_page_by_offset


# 机器人模块
class GameRobotServie(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_random_str(k=8):
        item_lab = string.ascii_letters + string.digits
        # ran_str = ''.join(random.sample(item_lab, k-1)) + '0'
        ran_str = ''.join(random.sample(item_lab, 7)) + '0'
        ran_str = list(ran_str)
        random.shuffle(ran_str)
        ran_str = ''.join(ran_str)

        return ran_str

    # 添加机器人
    def creat_robot(self, dic):
        number = int(dic.get('number', "0"))
        if (number <= 0):
            return

        with MysqlTools().session_scope() as session:
            while number > 0:
                model = RobotAccountModel()
                # model.user_id = model.uuid()
                # model.account_id = generate_order_no(k=44)
                model.nick_name = self.get_random_str(),
                model.score = dic.get('score', 0),
                model.id_card = dic.get('id_card', ''),
                model.source = int(dic.get('source', '1')),
                model.avatar = dic.get('avatar', ''),
                model.user_mobile = dic.get('user_mobile', ''),
                model.email = dic.get('email', ''),
                model.mobile_country_code = dic.get('mobile_country_code', ''),
                model.user_name = dic.get('user_name', 'user_name'),
                model.status = dic.get("status", 0),

                session.add(model)
                number -= 1

            session.commit()
            return True

    # 选择机器人
    def select_robot(self, dic):
        with MysqlTools().session_scope() as session:
            q = session.query(GameDigitalInstanceModel).filter(
                GameDigitalInstanceModel.game_serial == dic['game_serial']).all()
            if len(q) <= 0:
                return self.return_error(60001)

            q = session.query(GameDigitalInstanceModel).filter(GameDigitalInstanceModel.status == 0).all()
            if len(q) <= 0:
                return self.return_error(60000)

            q = session.query(RobotAccountModel).filter(RobotAccountModel.status == 0).with_for_update().all()
            if len(q) < int(dic['robot_number']):
                return self.return_error(70000)

            robots_arr = []
            arr = random.sample(q, int(dic['robot_number']))
            for i in arr:
                q = session.query(RobotAccountModel).filter(RobotAccountModel.user_id == i.user_id).first()
                q.status = 2

                robots_arr.append(
                    {
                        "user_id": i.user_id,
                        "nick_name": i.nick_name
                    }
                )
            session.commit()

            return robots_arr

    # 添加手动机器人配置
    def add_robot_config(self, dic):
        robots = []
        json_robots = dic.get("robots", "")

        if isinstance(json_robots, str):
            robots = json.loads(json_robots)
        if isinstance(json_robots, list):
            robots = json_robots

        if ~isinstance(robots, list) and len(robots) != int(dic['robot_number']):
            return self.return_error(70001)

        with MysqlTools().session_scope() as session:
            instance = session.query(GameDigitalInstanceModel).filter(
                GameDigitalInstanceModel.game_serial == dic['game_serial'],
                GameDigitalInstanceModel.status == 0).with_for_update().first()
            if instance is None:
                return self.return_error(60001)

            # 按照日期排序
            robots.sort(key=lambda x: x["bet_time"])

            total_bet_number = 0
            time_stamp = int(time.time())
            for robot in robots:
                bet_number = int(robot.get("bet_number", "0"))
                if bet_number <= 0:
                    return self.return_error(70001)

                if robot.get("user_id", "") == "":
                    return self.return_error(70001)
                if robot.get("nick_name", "") == "":
                    return self.return_error(70001)
                if robot.get("bet_number", "") == "":
                    return self.return_error(70001)
                if robot.get("pay_token", "") == "":
                    return self.return_error(70001)
                if robot.get("bet_time", "") == "":
                    return self.return_error(70001)

                # 机器人配置时间是否 > 当前时间
                today = datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y-%m-%d %H:%M:%S')

                if robot['bet_time'] < today:
                    return self.return_error(70004)

                # 添加计划 机器人配置任务 信息
                bet_plan_time = datetime.datetime.strptime(robot['bet_time'], '%Y-%m-%d %H:%M:%S')

                # 累计投注数量
                total_bet_number = total_bet_number + bet_number

                # 修改机器人账户状态
                q = session.query(RobotAccountModel).filter(
                    RobotAccountModel.user_id == robot['user_id']).with_for_update().first()
                if q.status == 1:
                    return self.return_error(70005)
                q.status = 1

                # 添加机器人配置纪录
                robot_config = RobotConfigRecordModel(
                    game_instance_id=instance._id,
                    game_serial=dic['game_serial'],

                    user_id=robot['user_id'],
                    nick_name=robot['nick_name'],
                    bet_number=int(robot['bet_number']),
                    pay_token=int(robot['pay_token']),

                    bet_plan_time=bet_plan_time,
                    bet_status=0,
                    time_stamp=time_stamp
                )
                session.add(robot_config)

            # 添加游戏机器人配置纪录
            robot_game_config_record = RobotGameConfigRecordModel(
                game_instance_id=instance._id,
                game_serial=dic['game_serial'],
                robot_number=int(dic['robot_number']),
                total_bet_number=total_bet_number,

                start_of_plan_time=datetime.datetime.strptime(robots[0].get('bet_time'), '%Y-%m-%d %H:%M:%S'),
                end_of_plan_time=datetime.datetime.strptime(robots[(len(robots) - 1)].get('bet_time'),
                                                            '%Y-%m-%d %H:%M:%S'),
                status=1,
                robot_bet_type=1,
                created_user_id=dic['created_user_id'],
                time_stamp=time_stamp
            )
            session.add(robot_game_config_record)
            session.commit()
            return True

    # 重置 机器人状态
    def reset_robot_config(self, dic):
        robots = []
        json_robots = dic.get("robots", "")

        if isinstance(json_robots, str):
            robots = json.loads(json_robots)
        if isinstance(json_robots, list):
            robots = json_robots

        with MysqlTools().session_scope() as session:
            for robot in robots:
                if robot == "":
                    return self.return_error(70001)

                q = session.query(RobotAccountModel).filter(RobotAccountModel.user_id == robot).first()
                q.status = 1

            session.commit()
            return True

    # 查询 游戏机器人配置
    def search_game_robot_config(self, dic):
        if dic is None:
            dic = {}

        limit = int(dic.get('limit', 10))
        offset = get_offset_by_page(dic.get('offset', 1), limit)
        start_id = dic.get("start_id", None)

        total = 0
        count = 0
        with MysqlTools().session_scope() as session:
            q = session.query(RobotGameConfigRecordModel)
            if dic.get('id', '') != '':
                q = q.filter(RobotGameConfigRecordModel._id == dic['id'])
            if dic.get('game_serial', '') != '':
                q = q.filter(RobotGameConfigRecordModel.game_serial == dic['game_serial'])
            if dic.get('plan_start_time_first', '') != '':
                q = q.filter(RobotGameConfigRecordModel.start_of_plan_time >= dic['start_of_plan_time'])
            if dic.get('plan_start_time_finish', '') != '':
                q = q.filter(RobotGameConfigRecordModel.start_of_plan_time <= dic['start_of_plan_time'])

            if dic.get('plan_end_time_first', '') != '':
                q = q.filter(RobotGameConfigRecordModel.end_of_plan_time >= dic['plan_end_time_first'])
            if dic.get('plan_end_time_finish', '') != '':
                q = q.filter(RobotGameConfigRecordModel.end_of_plan_time <= dic['plan_end_time_first'])

            if dic.get('status', '') != '':
                q = q.filter(RobotGameConfigRecordModel.status == int(dic['status']))

            if dic.get('real_end_time_first', '') != '':
                q = q.filter(RobotGameConfigRecordModel.end_of_real_time == dic['real_end_time_first'])
            if dic.get('real_end_time_finish', '') != '':
                q = q.filter(RobotGameConfigRecordModel.end_of_real_time == dic['real_end_time_finish'])

            if dic.get('robot_bet_type', '') != '':
                q = q.filter(RobotGameConfigRecordModel.robot_bet_type == int(dic['robot_bet_type']))

            total = q.count()
            count = get_page_by_offset(total, limit)

            if start_id is not None:
                q = q.filter(RobotGameConfigRecordModel._id < str(start_id))

            query_result = q.order_by(RobotGameConfigRecordModel._id.desc()).limit(limit).offset(offset).all()

            if len(query_result) <= 0:
                return self.return_error(50001)

            content = []
            for i in query_result:
                robots = session.query(RobotConfigRecordModel).filter(
                    RobotConfigRecordModel.time_stamp == i.time_stamp)
                count = robots.count()
                finish_count = robots.filter(RobotConfigRecordModel.bet_status == 1).count()

                yet_bet_number = 0
                if count != 0:
                    for robot in robots:
                        yet_bet_number = yet_bet_number + robot.bet_number

                end_of_real_time = ''
                if ("1970-01-01 00:00:00" != str(i.end_of_real_time) and "0000-00-00 00:00:00" != str(
                        i.end_of_real_time)):
                    end_of_real_time = str(i.end_of_real_time)

                completion = "0"
                if count != 0:
                    completion = str(finish_count / count * 100) + "%"

                content.append({
                    'id': str(i._id),
                    'game_serial': i.game_serial,
                    'robot_number': str(i.robot_number),
                    'yet_bet_number': str(yet_bet_number),
                    'total_bet_number': str(i.total_bet_number),
                    'created_at': str(i.created_at),
                    'start_of_plan_time': str(i.start_of_plan_time),
                    'end_of_plan_time': str(i.end_of_plan_time),
                    'end_of_real_time': end_of_real_time,
                    'completion': completion,
                    'status': str(i.status),
                    'robot_bet_type': str(i.robot_bet_type),
                    'created_user_id': str(i.created_user_id)
                })

            return {
                'limit': dic.get('limit', 10),
                'offset': dic.get('offset', 1),
                'count': count,
                'total': total,
                'content': content
            }

    # 查询 机器人配置纪录
    def search_robot_config(self, dic):
        limit = int(dic.get('limit', 10))
        offset = get_offset_by_page(dic.get('offset', 1), limit)
        start_id = dic.get("start_id", None)

        total = 0
        count = 0
        with MysqlTools().session_scope() as session:
            game_config = session.query(RobotGameConfigRecordModel).filter(
                RobotGameConfigRecordModel._id == dic['id']).first()
            q = session.query(RobotConfigRecordModel).filter(
                RobotConfigRecordModel.time_stamp == game_config.time_stamp)

            total = q.count()
            count = get_page_by_offset(total, limit)

            if start_id is not None:
                q = q.filter(RobotConfigRecordModel._id < str(start_id))
            query_result = q.order_by(RobotConfigRecordModel._id.asc()).limit(limit).offset(offset).all()

            content = []
            if len(query_result) > 0:
                for i in query_result:
                    content.append({
                        'user_id': str(i.user_id),
                        'nick_name': i.nick_name,
                        'bet_number': str(i.bet_number),
                        'pay_token': str(i.pay_token),
                        'bet_plan_time': str(i.bet_plan_time),
                        'bet_status': str(i.bet_status),
                    })

            return {
                'limit': dic.get('limit', 10),
                'offset': dic.get('offset', 1),
                'count': count,
                'total:': total,
                'content': content
            }

        # 停止游戏机器人配置

    def cancel_robot_config(self, dic):
        id = dic['id']
        with MysqlTools().session_scope() as session:
            game = session.query(RobotGameConfigRecordModel).filter(
                RobotGameConfigRecordModel._id == id).first()
            if game is None:
                return False
            game.status = 4

            q = session.query(RobotConfigRecordModel).filter(
                RobotConfigRecordModel.time_stamp == game.time_stamp).all()
            if len(q) > 0:
                for robot in q:
                    robot.bet_status = 2

            session.commit()
            return True

    # 添加自动机器人配置
    def add_auto_robot_config(self, dic):
        if dic.get('game_serial', '') == '':
            self.return_error(50000)
        if dic.get('robot_numbers', '') == '':
            self.return_error(50000)
        if dic.get('bet_numbers', '') == '':
            self.return_error(50000)
        if dic.get('support_token', '') == '':
            self.return_error(50000)
        if dic.get('start_time', '') == '':
            self.return_error(50000)
        if dic.get('end_time', '') == '':
            self.return_error(50000)
        if dic.get('bet_min', '') == '':
            self.return_error(50000)
        if dic.get('bet_max', '') == '':
            self.return_error(50000)
        if dic.get('created_user_id', '') == '':
            self.return_error(50000)

        game_serial = dic['game_serial']  # 下注期数
        robot_numbers = int(dic['robot_numbers'])  # 机器人数量
        bet_numbers = int(dic['bet_numbers'])  # 总下注数量
        support_token = int(dic['support_token'])  # 下注币种
        start_time = dic['start_time']  # 下注开始时间
        end_time = dic['end_time']  # 下注结束时间
        bet_min = int(dic['bet_min'])  # 最小下注数量
        bet_max = int(dic['bet_max'])  # 最大下注数量
        created_user_id = dic['created_user_id']

        if robot_numbers * bet_max < bet_numbers:
            self.return_error(60021)
        if robot_numbers * bet_min > bet_numbers:
            self.return_error(60022)

        if start_time >= end_time:
            self.return_error(60020)

        today = datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y-%m-%d %H:%M:%S')
        if start_time < today:
            self.return_error(70004)

        with MysqlTools().session_scope() as session:
            instance = session.query(GameDigitalInstanceModel).filter(
                GameDigitalInstanceModel.game_serial == game_serial,
                GameDigitalInstanceModel.status == 0).with_for_update().first()
            if instance is None:
                self.return_error(60001)
            if instance.status != 0:
                self.return_error(60000)

            if bet_numbers > (instance.need - instance.bet_number):
                self.return_error(60004)

            if instance.support_token != -1:
                if support_token != instance.support_token:
                    self.return_error(60018)

            # 配置机器人注数
            bet_arr = [bet_min] * robot_numbers
            bet_numbers = bet_numbers - bet_min * robot_numbers

            while bet_numbers > 0:
                num = random.randint(0, len(bet_arr) - 1)

                if bet_arr[num] >= bet_max:
                    continue
                bet_arr[num] = bet_arr[num] + 1
                bet_numbers = bet_numbers - 1

            # 每个下注数量 bet_arr

            # 时间差 秒
            bet_start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            bet_end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            delta_times = bet_end_time - bet_start_time
            sec = int(delta_times.seconds / 1)

            time_arr = []
            for i in bet_arr:
                delta_time = random.randint(1, sec - 1)
                bet_time = bet_start_time + datetime.timedelta(seconds=delta_time)
                time_arr.append(bet_time.strftime('%Y-%m-%d %H:%M:%S'))

            time_arr.sort()
            # 每个下注时间 time_arr

            q = session.query(RobotAccountModel).filter(RobotAccountModel.status == 0).with_for_update().all()
            if len(q) < robot_numbers:
                return self.return_error(70000)

            i = 0
            tokens = [0, 60]
            robot_arr = []
            while i < len(bet_arr):
                pay_token = -1
                if support_token < 0:
                    pay_token = random.sample(tokens, 1)[0]

                robot_arr.append({"user_id": q[i].user_id,
                                  "nick_name": q[i].nick_name,
                                  "bet_number": bet_arr[i],
                                  "pay_token": pay_token,
                                  "bet_time": time_arr[i]})

                i = i + 1

            # print("bet_arr:", bet_arr)
            # print("time_arr:", time_arr)
            # print("robot_arr:", robot_arr)

            total_bet_number = 0
            time_stamp = time.time()
            count = 0

            try:
                for robot in robot_arr:
                    bet_number = int(robot.get("bet_number", "0"))
                    if bet_number <= 0:
                        return self.return_error(70001)

                    if robot.get("user_id", "") == "":
                        return self.return_error(70001)
                    if robot.get("nick_name", "") == "":
                        return self.return_error(70001)
                    if robot.get("bet_number", "") == "":
                        return self.return_error(70001)
                    if robot.get("pay_token", "") == "":
                        return self.return_error(70001)
                    if robot.get("bet_time", "") == "":
                        return self.return_error(70001)

                    # 机器人配置时间是否 > 当前时间
                    today = datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y-%m-%d %H:%M:%S')
                    if robot['bet_time'] < today:
                        return self.return_error(70004)

                    # 添加计划 机器人配置任务 信息
                    bet_plan_time = datetime.datetime.strptime(robot['bet_time'], '%Y-%m-%d %H:%M:%S')

                    # 累计投注数量
                    total_bet_number = total_bet_number + bet_number

                    # 修改机器人账户状态
                    q = session.query(RobotAccountModel).filter(
                        RobotAccountModel.user_id == robot['user_id']).with_for_update().first()
                    if q.status == 1:
                        return self.return_error(70005)
                    q.status = 1

                    # 添加机器人配置纪录
                    robot_config = RobotConfigRecordModel(
                        game_instance_id=instance._id,
                        game_serial=dic['game_serial'],

                        user_id=robot['user_id'],
                        nick_name=robot['nick_name'],
                        bet_number=int(robot['bet_number']),
                        pay_token=int(robot['pay_token']),

                        bet_plan_time=bet_plan_time,
                        bet_status=0,
                        time_stamp=time_stamp
                    )
                    session.add(robot_config)
                    count = count + 1
                    if count == 100:
                        session.flush()
                        count = 0

                        raise_logger("add_auto_robot_config     flush", "game_publish_lottery", "info")
                        # print("flush")

                # 添加游戏机器人配置纪录
                robot_game_config_record = RobotGameConfigRecordModel(
                    game_instance_id=instance._id,
                    game_serial=game_serial,
                    robot_number=robot_numbers,
                    total_bet_number=total_bet_number,

                    start_of_plan_time=datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S'),
                    end_of_plan_time=datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S'),
                    status=1,
                    robot_bet_type=0,
                    created_user_id=created_user_id,
                    time_stamp=time_stamp
                )
                session.add(robot_game_config_record)
                session.flush()
                session.commit()

                return {
                    'msg': "提交成功",
                    'content': True
                }
            except Exception as e:
                # print("Exception:", e)
                raise_logger("add_auto_robot_config     Exception", "game_publish_lottery", "info")

                session.rollback()
                return {
                    'e': "add_auto_robot_config Exception",
                    'content': False
                }

            return {
                'content': False
            }

    # 添加机器人
    def manual_creat_robot(self, dic):
        count = 0
        number = int(dic.get('number', "0"))
        if number <= 0:
            return
        with MysqlTools().session_scope() as session:
            name_list = session.query(RobotInfoLibModel). \
                filter(RobotInfoLibModel.uid == ''). \
                limit(number).all()
            # while number > 0:
            #     print('name_==-=-=', name_list[number - 1].name)
            #     number -= 1
            while number > 0:
                count += 1
                model = RobotAccountModel()
                model.nick_name = name_list[number - 1].name,
                model.score = dic.get('score', 0),
                model.id_card = dic.get('id_card', ''),
                model.source = int(dic.get('source', '1')),
                model.avatar = dic.get('avatar', ''),
                model.user_mobile = dic.get('user_mobile', ''),
                model.email = dic.get('email', ''),
                model.mobile_country_code = dic.get('mobile_country_code', ''),
                model.user_name = dic.get('user_name', 'user_name'),
                model.status = dic.get("status", 0),

                session.add(model)
                name_list[number - 1].uid = 1
                # print('robot_name==', model.nick_name)
                number -= 1
                if count == 100:
                    session.flush()
                    count = 0

            session.commit()
            return True


if __name__ == "__main__":
    pass
    # temp_time = "12/11/2018 12:57"
    #
    # year = temp_time[0:10]
    # years = year.split("/")
    #
    # y = years[len(years) - 1]
    # m = years[0]
    # d = years[1]
    # new_year = y + "-" + m + "-" + d
    #
    # month = temp_time[11:16]
    # add_time = new_year + " " + month + ":00"
    #
    # print("new_year:" + add_time)

    # =================================================================================================

    # bet_numbers = 20
    # bet_min = 1
    # bet_max = 5
    # robot_numbers = 11
    #
    # bet_numbers = bet_numbers - bet_min * robot_numbers
    # bet_arr = [bet_min] * robot_numbers
    #
    # while bet_numbers > 0:
    #     num = random.randint(0, len(bet_arr) - 1)
    #
    #     if bet_arr[num] >= bet_max:
    #         continue
    #     bet_arr[num] = bet_arr[num] + 1
    #     bet_numbers = bet_numbers - 1
    #
    # print(bet_arr)
    # print("bet_arr长度:", len(bet_arr))
    #
    # # sum = 0
    # # for x in bet_arr:
    # #     sum = sum + x
    # # print("sum:", sum)
    #
    # start_time = "2019-1-2 18:40:00"
    # end_time = "2019-1-2 18:50:00"
    #
    # bet_start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    # bet_end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
    #
    # delta_times = bet_end_time - bet_start_time
    # sec = int(delta_times.seconds / 1)
    #
    # time_arr = []
    # for i in bet_arr:
    #     delta_time = random.randint(1, sec - 1)
    #     bet_time = bet_start_time + datetime.timedelta(seconds=delta_time)
    #
    #     time_arr.append(bet_time.strftime('%Y-%m-%d %H:%M:%S'))
    #
    # time_arr.sort()
    # print("time_arr:", time_arr)
    #
    # tokens = [0, 60, 100000000]
    # print("test:", random.sample(tokens, 1))
    #
    # support_token = -1
    # q = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 11]
    #
    # i = 0
    # tokens = [0, 60, 100000000]
    # robot_arr = []
    # while i < len(bet_arr):
    #     pay_token = -1
    #     if support_token < 0:
    #         pay_token = random.sample(tokens, 1)[0]
    #
    #     robot_arr.append({"user_id": q[i],
    #                       "nick_name": q[i],
    #                       "bet_number": bet_arr[i],
    #                       "pay_token": pay_token,
    #                       "bet_time": time_arr[i]})
    #
    #     print(datetime.datetime.strptime(time_arr[i], '%Y-%m-%d %H:%M:%S'))
    #
    #     i = i + 1
    #
    # print("robot_arr:", robot_arr)

    # =================================================================================================
