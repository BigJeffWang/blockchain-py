import time
import sys
from pathlib import Path

pro_name = "TokenPark"
current_path = str(Path(__file__).resolve())
import_index = current_path.rfind(pro_name)
import_path = current_path[:import_index + len(pro_name)]
path_flag = True if not import_path in sys.path else False
if path_flag:
    sys.path.append(import_path)

from services.game_number_set_service import GameNumberSetService
from models.game_digital_instance_model import GameDigitalInstanceModel
from models.game_digital_template_model import GameDigitalTemplateModel
from services.block_chain_info_service import BlockChainInfoService
from tools.mysql_tool import MysqlTools
from config import get_sms_email
from utils.util import send_mail
from tools.request_tools import RequestTools
from utils.log import Slog

from utils.exchange_rate_util import get_exchange_rate
from utils.generate_phase_util import generate_phase
from utils.time_util import get_utc_now


class AutomaticReleaseInstance(object):
    """
    自动发布game实例
    """

    slog = Slog("automatic_release_script")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_tools = RequestTools()

    def automatic_release_instance(self):
        # now = int(time.time())
        # time_struct = time.localtime(now)
        # str_time = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)
        str_time = get_utc_now()

        with MysqlTools().session_scope() as session:
            template_result = session.query(GameDigitalTemplateModel). \
                filter(GameDigitalTemplateModel.template_status == 1,
                       GameDigitalTemplateModel.auto_release == 1).all()
            if len(template_result) > 0:
                for row in template_result:
                    btc_usdt_rate = get_exchange_rate(row.reward_token)['price']
                    ceiling = row.need_ceiling
                    floor = row.need_floor
                    email_config = get_sms_email('common')
                    if email_config == {}:
                        self.return_error(35034)
                    send_email_config = get_sms_email("send_email_config")
                    subject = email_config['email_subject']
                    if btc_usdt_rate > ceiling or btc_usdt_rate < floor:
                        self.slog.info("instantiation fail. rate is ", str(btc_usdt_rate))
                        self.slog.info("game template id is ", str(row._id))
                        # 警告邮件
                        send_mail("game自动实例化失败, GAME模板id:"+str(row._id)+",奖励币种价格:"+str(btc_usdt_rate),
                                  send_email_config['user'], send_email_config['pwd'], email_config['email'],
                                  subject, send_email_config['smtp_server'], send_email_config['smtp_port'])
                    else:
                        template_id = row._id
                        instance_list = session.query(GameDigitalInstanceModel). \
                            filter(GameDigitalInstanceModel.status == 0,
                                   GameDigitalInstanceModel.template_id == template_id).all()
                        if len(instance_list) <= 0:
                            phase_prefix = row.phase_prefix
                            need = btc_usdt_rate * row.reward_quantity * ((100 + row.exceeded_ratio) / 100)
                            game_serial = generate_phase(str(phase_prefix))
                            digital_instance_model = GameDigitalInstanceModel(
                                template_id=template_id,
                                game_serial=game_serial,
                                game_title=row.game_title,
                                bet_token=row.bet_token,
                                bet_unit=row.bet_unit,
                                support_token=row.support_token,
                                reward_token=row.reward_token,
                                reward_quantity=row.reward_quantity,
                                handling_fee=row.handling_fee,
                                game_describe=row.game_describe,
                                experience=row.experience,
                                merge_threshold=row.merge_threshold,
                                release_time=str_time,
                                need=int(need),
                                status=0,
                                release_type=1,
                                chain_status=0
                            )
                            # if create_all_bet_number(game_serial, int(need)) != 2000:
                            #     self.slog.info("create all bet number fail")
                            if not GameNumberSetService().createNumbers(
                                    {"game_serial": game_serial, "total": int(need)}):
                                self.slog.info("create all bet number fail")
                                self.return_error(40015)
                            session.add(digital_instance_model)
                            session.flush()
                            try:
                                # 发布信息上链
                                if BlockChainInfoService().insert_block_chain_info('', str(digital_instance_model._id), 2,
                                                                                   {
                                                                                       "instance_id": digital_instance_model._id,
                                                                                       "template_id": template_id,
                                                                                       "game_serial": game_serial,
                                                                                       "support_token": row.support_token,
                                                                                       "bet_token": row.bet_token,
                                                                                       "bet_unit": row.bet_unit,
                                                                                       "reward_token": row.reward_token,
                                                                                       "reward_quantity": row.reward_quantity,
                                                                                       "handling_fee": str(row.handling_fee),
                                                                                       "game_describe": row.game_describe,
                                                                                       "release_time": str_time.strftime("%Y-%m-%d %H:%M:%S"),
                                                                                       "status": 0,
                                                                                       "need": int(need),
                                                                                       "release_type": 0,
                                                                                   }):
                                    digital_instance_model.chain_status = 1
                                    self.slog.info("insert_block_chain_info success")
                                else:
                                    self.slog.info("insert_block_chain_info fail")
                            except Exception as e:
                                self.slog.info("insert_block_chain_info fail")
                                self.slog.info(f"Exception: {e}")
                                # self.slog.info("automatic_release_instance fail")
                                # session.rollback()
                            session.commit()
                            # send_mail("game自动实例化成功, GAME模板id:" + str(template_id) + ",奖励币种价格:" + str(btc_usdt_rate),
                            #           send_email_config['user'], send_email_config['pwd'],
                            #           email_config['email'],
                            #           subject, send_email_config['smtp_server'], send_email_config['smtp_port'])
                            self.slog.info("automatic_release_instance success")

    def return_error(self, error_code, error_msg=None, status_code=200):
        self.request_tools.return_error(error_code, error_msg, status_code)


if __name__ == "__main__":
    AutomaticReleaseInstance().automatic_release_instance()
