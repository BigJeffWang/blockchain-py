import sys
import logging
from decimal import Decimal

import pymysql
from pymysql.err import MySQLError

sys.path.append("..")
from config import get_mysql_conf

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
# set console level and formatter
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)

# ------------------------- Define Variable ------------------------------------
# 活动时间
# 比如："2018-01-01 00:00:00" UTC 时区
BEGIN_TIME = '2018-01-01 00:00:00'
END_TIME = '2019-03-01 00:00:00'
USER_LIMIT_NUMBER = 1000

# 活动信息
OPERATIONAL_ACTIVITIES_ID = ''
OPERATIONAL_ACTIVITIES_NAME = ''
## sample: labels = '['test1', 'test2']'
LABELS = ''
# ------------------------------------------------------------------------------


def mysql_connect():
    mysql_paras = get_mysql_conf()
    host = mysql_paras.get('host')
    port = mysql_paras.get('port')
    database = mysql_paras.get('db')
    username = mysql_paras.get('user')
    password = mysql_paras.get('psd')

    # connect to mysql
    conn = pymysql.connect(host=host, user=username, password=password,
                           db=database, port=port,
                           cursorclass=pymysql.cursors.DictCursor)
    return conn


def compute_reward_amount(inviter_code, graph):
    def compute_second_reward_amount(tmp_inviter_code, tmp_graph):
        tmp_amount = 0
        for _, i in enumerate(tmp_graph[tmp_inviter_code]):
            if i in tmp_graph and len(tmp_graph[i]) >= 5:
                tmp_amount += 50
                if tmp_amount == 250:
                    break
        return tmp_amount

    amount = 0
    # 第一级
    if len(graph[inviter_code]) >= 5:
        amount += 100
        # 第二级
        amount += compute_second_reward_amount(inviter_code, graph)
    else:
        # 第二级
        amount += compute_second_reward_amount(inviter_code, graph)
    return amount


if __name__ == '__main__':
    # 流程:
    # 1. 判断执行条件
    # 2. 构造玩家邀请图
    # 3. 查询创世玩家
    # 4. 遍历每个用户，如果用户邀请过其他用户注册，则计算是否符合活动要求

    # 该字典记录用户邀请过哪些用户
    USER_INVITE_GRAPH = dict()

    mysql_conn = mysql_connect()
    try:
        with mysql_conn.cursor() as cursor:
            # 1. 判断执行条件
            sql_1 = "SELECT COUNT(*) FROM `user_account` WHERE `invitee_code` != '' AND `deleted` = FALSE AND `created_at` BETWEEN %s AND %s"
            cursor.execute(sql_1, (BEGIN_TIME, END_TIME))
            result = cursor.fetchone()
            ## 如果所有被邀请用户不足 5 人，提前停止程序
            if list(result.values())[0] < 5:
                raise KeyboardInterrupt

            # 2. 构造玩家邀请图
            sql_2 = "SELECT `inviter_code`, `invitee_code` FROM `user_account` WHERE `deleted` = FALSE AND `created_at` BETWEEN %s AND %s"
            cursor.execute(sql_2, (BEGIN_TIME, END_TIME))
            result_user_graph = cursor.fetchall()
            for row in result_user_graph:
                user_inviter_code = row['inviter_code']
                user_invitee_code = row['invitee_code']
                if user_inviter_code == '':
                    continue
                if user_invitee_code != '':
                    if user_invitee_code in USER_INVITE_GRAPH:
                        USER_INVITE_GRAPH[user_invitee_code].append(user_inviter_code)
                    else:
                        USER_INVITE_GRAPH[user_invitee_code] = [user_inviter_code]

            # 3. 查询创世玩家
            sql_3 = "SELECT `user_id`, `inviter_code` FROM `user_account` WHERE `deleted` = FALSE AND `created_at` BETWEEN %s AND %s ORDER BY created_at LIMIT %s"
            cursor.execute(sql_3, (BEGIN_TIME, END_TIME, USER_LIMIT_NUMBER))
            result_user = cursor.fetchall()

            # 4. 遍历每个用户，如果用户邀请过其他用户注册，则计算是否符合活动要求
            for user in result_user:
                ## 奖励金额
                REWARD_AMOUNT = 0

                user_id = user['user_id']
                user_inviter_code = user['inviter_code']
                if user_inviter_code in USER_INVITE_GRAPH:
                    REWARD_AMOUNT = compute_reward_amount(user_inviter_code, USER_INVITE_GRAPH)

                    # 是否存在运营活动记录
                    sql_4 = "SELECT `amount` FROM `operational_activities` WHERE `deleted` = FALSE AND `user_id`=%s AND `operational_activities_id`=%s"
                    cursor.execute(sql_4, (user_id, OPERATIONAL_ACTIVITIES_ID))
                    result_exist = cursor.fetchone()
                    if result_exist:
                        # 如果存在
                        difference_amount = round(result_exist['amount'] - Decimal(REWARD_AMOUNT))
                        if difference_amount == 0:
                            continue
                        else:
                            sql_5 = "UPDATE `operational_activities` SET `amount`=%s WHERE `deleted` = FALSE AND `user_id`=%s AND `operational_activities_id`=%s"
                            sql_6 = "UPDATE `user_account_token` SET `balance`= `balance` + %s, `total_recharge`= `total_recharge` + %s WHERE `deleted` = FALSE AND `user_id`=%s AND `token_id`='236'"
                            cursor.execute(sql_5, (REWARD_AMOUNT, user_id, OPERATIONAL_ACTIVITIES_ID))
                            cursor.execute(sql_6, (difference_amount, difference_amount, user_id))
                            mysql_conn.commit()
                    else:
                        # 如果不存在
                        sql_7 = "INSERT INTO `operational_activities` (`user_id`, `operational_activities_id`, `operational_activities_name`, `labels`, `amount`) VALUES (%s, %s, %s, %s, %s)"
                        sql_8 = "UPDATE `user_account_token` SET `balance`= `balance` + %s, `total_recharge`= `total_recharge` + %s WHERE `deleted` = FALSE AND `user_id`=%s AND `token_id`='236'"
                        cursor.execute(sql_7, (user_id, OPERATIONAL_ACTIVITIES_ID, OPERATIONAL_ACTIVITIES_NAME, LABELS, REWARD_AMOUNT))
                        cursor.execute(sql_8, (REWARD_AMOUNT, REWARD_AMOUNT, user_id))
                        mysql_conn.commit()
                else:
                    continue
    except KeyboardInterrupt as user_error:
        logger.info("所有被邀请用户不足 5 人，提前停止程序")
    except MySQLError as error:
        mysql_conn.rollback()
        logger.error(f"MySQLError: {error}")
    finally:
        mysql_conn.close()

    logger.info("Success!")
