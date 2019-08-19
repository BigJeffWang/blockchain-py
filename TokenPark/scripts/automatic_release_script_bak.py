#!/usr/bin/python3
import datetime
import time
import pymysql

from scripts.mq_consume_script import send_mail
from utils.bet_number_util import create_all_bet_number
from utils.exchange_rate_util import get_exchange_rate
from utils.generate_phase_util import generate_phase


def automatic_release_instance():
    now = int(time.time())
    time_struct = time.localtime(now)
    str_time = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)

    # current_date = datetime.datetime.utcnow()
    db = pymysql.connect("rm-2zes47ke8wo3utd54.mysql.rds.aliyuncs.com",
                         "H34pHJ2jdtGC", "BF1xE960ivNd", "tokenpark")
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    # cursor = db.cursor()
    template_sql = "SELECT * FROM TokenPark.game_digital_template WHERE template_status = 1 AND auto_release = 1"
    try:
        cursor.execute(template_sql)
        template_result = cursor.fetchall()
        if len(template_result) > 0:
            for row in template_result:
                btc_usdt_rate = get_exchange_rate(row['reward_token'])['price']
                ceiling = row['need_ceiling']
                floor = row['need_floor']
                if btc_usdt_rate > ceiling or btc_usdt_rate < floor:
                    # TODO 发警告邮件
                    send_mail('未实例化成功')
                else:
                    template_id = row['_id']
                    instance_sql = "SELECT * FROM TokenPark.game_digital_instance \
                      WHERE game_digital_instance.status = 0 AND \
                      game_digital_instance.template_id = %d" % template_id
                    cursor.execute(instance_sql)
                    instance_result = cursor.fetchall()
                    if len(instance_result) <= 0:
                        reward_quantity = row['reward_quantity']
                        exceeded_ratio = row['exceeded_ratio']
                        # game_serial = row['game_serial']
                        game_title = row['game_title']
                        bet_token = row['bet_token']
                        bet_unit = row['bet_unit']
                        reward_token = row['reward_token']
                        handling_fee = row['handling_fee']
                        game_describe = row['game_describe']
                        # status = row['status']
                        # release_type = row['release_type']
                        phase_prefix = row['phase_prefix']
                        need = btc_usdt_rate * reward_quantity * ((100 + exceeded_ratio) / 100)
                        game_serial = generate_phase(str(phase_prefix))
                        create_all_bet_number(game_serial, int(need))
                        release_sql = "INSERT INTO game_digital_instance(template_id,game_serial,game_title,bet_token\
                            ,bet_unit,reward_token,reward_quantity, release_time,need,status,release_type, handling_fee,\
                            game_describe) \
                            VALUES('%d','%s','%s','%d','%d','%d','%d','%s','%d','%d','%d','%d','%s')" % \
                                      (template_id, game_serial, game_title, bet_token, bet_unit,
                                       reward_token, reward_quantity, str_time, int(need), 0, 1, handling_fee
                                       , game_describe)
                        cursor.execute(release_sql)
        db.commit()
    except:
        print("Error: unable to fetch data")
        db.rollback()

    # 关闭数据库连接
    db.close()


if __name__ == "__main__":
    automatic_release_instance()
