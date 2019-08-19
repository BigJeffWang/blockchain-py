from models.instant_game_instance_model import InstantGameInstanceModel
from models.instant_game_template_model import InstantGameTemplateModel
from models.participate_in_model import ParticipateInModel
from services.base_service import BaseService
from common_settings import *
from tools.mysql_tool import MysqlTools
from tools.tool import is_number
from utils.exchange_rate_util import get_exchange_rate
from utils.generate_phase_util import generate_phase
from utils.log import raise_logger
from utils.time_util import get_utc_now
from utils.util import get_offset_by_page, get_page_by_offset
from sqlalchemy import func


class InstantGameModelService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_coin_name(self, coin_id):
        coin_id = int(coin_id)
        if coin_id == int(_COIN_ID_BTC):
            return 'BTC'
        elif coin_id == int(_COIN_ID_ETH):
            return 'ETH'
        elif coin_id == int(_COIN_ID_EOS):
            return 'EOS'
        elif coin_id == int(_COIN_ID_USDT):
            return 'USDT'
        elif coin_id == int(_COIN_ID_EXP):
            return 'USDT体验金'
        else:
            return 'unknown'

    # 添加数据
    def add_model(self, dic):

        # game_title = dic.get("game_title", "")
        if dic.get('game_title', '') == '':
            return self.return_error(50000)
        if dic.get('reward_token', '') == '':
            return self.return_error(50000)
        if dic.get('bet_token', '') == '':
            return self.return_error(50000)

        if dic.get('bet_unit', "") == '':
            return self.return_error(50000)
        if is_number(dic.get('bet_unit')):
            if "." in dic.get('bet_unit'):
                return self.return_error(50002)
            if int(dic.get('bet_unit')) <= 0:
                return self.return_error(50002)
        else:
            return self.return_error(50002)

        if dic.get('reward_quantity', "") == '':
            return self.return_error(50000)
        if is_number(dic.get('reward_quantity')):
            if "." in dic.get('reward_quantity'):
                return self.return_error(50002)
            if int(dic.get('reward_quantity')) <= 0:
                return self.return_error(50002)
        else:
            return self.return_error(50002)

        if dic.get('need_ceiling', "") == '':
            return self.return_error(50000)
        if is_number(dic.get('need_ceiling')):
            if "." in dic.get('need_ceiling'):
                return self.return_error(50002)
            if int(dic.get('need_ceiling')) <= 0:
                return self.return_error(50002)
        else:
            return self.return_error(50002)

        if dic.get('need_floor', "") == '':
            return self.return_error(50000)
        if is_number(dic.get('need_floor')):
            if "." in dic.get('need_floor'):
                return self.return_error(50002)
            if int(dic.get('need_floor')) <= 0:
                return self.return_error(50002)
        else:
            return self.return_error(50002)

        if dic.get('exceeded_ratio', "") == '':
            return self.return_error(50000)
        if is_number(dic.get('exceeded_ratio')):
            if "." in dic.get('exceeded_ratio'):
                return self.return_error(50002)
            if int(dic.get('exceeded_ratio')) < 0:
                return self.return_error(50002)
        else:
            return self.return_error(50002)

        # if dic.get('handling_fee', "") == '':
        #     return self.return_error(50000)
        # if is_number(dic.get('handling_fee')):
        #     if float(dic.get('handling_fee')) < 0:
        #         return self.return_error(50002)
        # else:
        #     return self.return_error(50002)

        if dic.get('support_token', '') == '':
            return self.return_error(50000)
        if dic.get('template_status', '') == '':
            return self.return_error(50000)
        if dic.get('auto_release', '') == '':
            return self.return_error(50000)
        if dic.get('game_describe', '') == '':
            return self.return_error(50000)
        if dic.get('phase_prefix', '') == '':
            return self.return_error(50000)
        # if dic.get('phase_date', '') == '':
        #     return self.return_error(50000)
        # if dic.get('phase_serial', '') == '':
        #     return self.return_error(50000)
        # if dic.get('agreement', '') == '':
        #     return self.return_error(50000)
        # if dic.get('agreement_name', '') == '':
        #     return self.return_error(50000)

        with MysqlTools().session_scope() as session:
            digital_template_model = InstantGameTemplateModel
            q = session.query(digital_template_model).filter(
                InstantGameTemplateModel.game_title == dic['game_title']).with_for_update().all()
            if len(q) > 0:
                return self.return_error(50003)

            digital_template_model = InstantGameTemplateModel(
                game_title=dic['game_title'],
                reward_token=int(dic['reward_token']),
                bet_token=int(dic['bet_token']),
                bet_unit=int(dic['bet_unit']),
                reward_quantity=int(dic['reward_quantity']),
                need_ceiling=int(dic['need_ceiling']),
                need_floor=int(dic['need_floor']),
                exceeded_ratio=int(dic['exceeded_ratio']),
                experience=int(dic.get('experience', '0')),
                # handling_fee=float(dic['handling_fee']),
                support_token=dic['support_token'],
                template_status=int(dic['template_status']),
                auto_release=int(dic['auto_release']),
                max_bet_ratio=int(dic['max_bet_ratio']),
                game_describe=dic['game_describe'],
                phase_prefix=dic['phase_prefix'],
                phase_date='YYDDMMDD',
                phase_serial='001',
                agreement=dic.get('agreement', ''),
                agreement_name=dic.get('agreement_name', ''),
                merge_threshold=dic.get('merge_threshold', '50')
            )
            session.add(digital_template_model)

            session.commit()
            return True

    # 查询数据
    def search_model(self, dic):
        count = 0
        total = 0
        number_games = []
        object_games = []

        if dic is None:
            dic = {}

        limit = int(dic.get('limit', 10))
        offset = get_offset_by_page(dic.get('offset', 1), limit)
        start_id = dic.get("start_id", None)

        with MysqlTools().session_scope() as session:
            q = session.query(InstantGameTemplateModel)
            if dic.get('id', '') != '':
                q = q.filter(InstantGameTemplateModel._id == dic['id'])
            if dic.get('game_title', '') != '':
                q = q.filter(InstantGameTemplateModel.game_title == dic['game_title'])
            if dic.get('reward_quantity', '') != '':
                q = q.filter(InstantGameTemplateModel.reward_quantity == int(dic['reward_quantity']))

            if dic.get('release_time_start', '') != '':
                q = q.filter(InstantGameTemplateModel.created_at >= dic['release_time_start'])
            if dic.get('release_time_end', '') != '':
                q = q.filter(InstantGameTemplateModel.created_at <= dic['release_time_end'])

            if dic.get('template_status', '') != '':
                q = q.filter(InstantGameTemplateModel.template_status == int(dic['template_status']))
            if dic.get('auto_release', '') != '':
                q = q.filter(InstantGameTemplateModel.auto_release == int(dic['auto_release']))

            total = q.count()
            count = get_page_by_offset(total, limit)

            if start_id is not None:
                q = q.filter(InstantGameTemplateModel._id < str(start_id))

            query_result = q.order_by(InstantGameTemplateModel._id.desc()).limit(limit).offset(offset).all()

            # if len(query_result) == 0:
            #     return self.return_error(50001)
            if len(query_result) >= 0:
                for i in query_result:
                    number_games.append({
                        'id': str(i._id),
                        'game_title': i.game_title,
                        'reward_token': i.reward_token,
                        'bet_token': i.bet_token,
                        'bet_unit': i.bet_unit,
                        'reward_quantity': i.reward_quantity,
                        'need_ceiling': i.need_ceiling,
                        'need_floor': i.need_floor,
                        'exceeded_ratio': i.exceeded_ratio,
                        'experience': i.experience,
                        'merge_threshold': i.merge_threshold,
                        'handling_fee': str(i.handling_fee),
                        'support_token': i.support_token,
                        'template_status': i.template_status,
                        'auto_release': i.auto_release,
                        'game_describe': i.game_describe,
                        'max_bet_ratio': i.max_bet_ratio,
                        # 'phase_date': i.phase_date,
                        'phase_serial': i.phase_prefix + i.phase_date + i.phase_serial,
                        'agreement': i.agreement,
                        'agreement_name': i.agreement_name,
                        'created_at': str(i.created_at),
                        'update_at': str(i.update_at)
                    })
                # print("number_games:", number_games)

        if dic.get("model_type") == "1":
            return {
                'limit': dic.get('limit', 10),
                'offset': dic.get('offset', 1),
                'count': count,
                'total': total,
                'number_games': number_games
            }

        if dic.get("model_type") == "2":
            return {
                'limit': dic.get('limit', 10),
                'offset': dic.get('offset', 1),
                'count': count,
                'total': total,
                'object_games': object_games
            }

        return {
            "data": {
                "number_games": number_games,
                "object_games": object_games
            }
        }

    # 修改数据
    def modify_model(self, dic):
        id = dic.get("id", "")
        if id == '':
            return self.return_error(50001)

        # if dic.get('reward_token', '') == '':
        #     return self.return_error(50000)
        # if dic.get('bet_token', '') == '':
        #     return self.return_error(50000)

        if dic.get('bet_unit', '') == '':
            return self.return_error(50000)
        if is_number(dic.get('bet_unit')):
            if "." in dic.get('bet_unit'):
                return self.return_error(50002)
            if int(dic.get('bet_unit')) <= 0:
                return self.return_error(50002)
        else:
            return self.return_error(50002)

        if dic.get('reward_quantity', '') == '':
            return self.return_error(50000)
        if is_number(dic.get('reward_quantity')):
            if "." in dic.get('reward_quantity'):
                return self.return_error(50002)
            if int(dic.get('reward_quantity')) <= 0:
                return self.return_error(50002)
        else:
            return self.return_error(50002)

        if dic.get('need_ceiling', '') == '':
            return self.return_error(50000)
        if is_number(dic.get('need_ceiling')):
            if "." in dic.get('need_ceiling'):
                return self.return_error(50002)
            if int(dic.get('need_ceiling')) <= 0:
                return self.return_error(50002)
        else:
            return self.return_error(50002)

        if dic.get('need_floor', '') == '':
            return self.return_error(50000)
        if is_number(dic.get('need_floor')):
            if "." in dic.get('need_floor'):
                return self.return_error(50002)
            if int(dic.get('need_floor')) <= 0:
                return self.return_error(50002)
        else:
            return self.return_error(50002)

        if dic.get('exceeded_ratio', '') == '':
            return self.return_error(50000)
        if is_number(dic.get('exceeded_ratio')):
            if "." in dic.get('exceeded_ratio'):
                return self.return_error(50002)
            if int(dic.get('exceeded_ratio')) < 0:
                return self.return_error(50002)
        else:
            return self.return_error(50002)

        # if dic.get('handling_fee', '') == '':
        #     return self.return_error(50000)
        # if is_number(dic.get('handling_fee')):
        #     if float(dic.get('handling_fee')) < 0:
        #         return self.return_error(50002)
        # else:
        #     return self.return_error(50002)

        if dic.get('support_token', '') == '':
            return self.return_error(50000)
        if dic.get('template_status', '') == '':
            return self.return_error(50000)
        if dic.get('auto_release', '') == '':
            return self.return_error(50000)
        if dic.get('game_describe', '') == '':
            return self.return_error(50000)
        if dic.get('phase_prefix', '') == '':
            return self.return_error(50000)
            # if dic.get('phase_date', '') == '':
            #     return self.return_error(50000)
            # if dic.get('phase_serial', '') == '':
            #     return self.return_error(50000)
        # if dic.get('agreement', '') == '':
        #     return self.return_error(50000)
        #
        # if dic.get('agreement_name', '') == '':
        #     return self.return_error(50000)

        with MysqlTools().session_scope() as session:
            model = session.query(InstantGameTemplateModel).filter(
                InstantGameTemplateModel._id == id).with_for_update().first()
            if model is None:
                return self.return_error(50001)

            model.game_title = model.game_title,
            # model.reward_token = int(dic['reward_token']),
            # model.bet_token = int(dic['bet_token']),
            model.bet_unit = int(dic['bet_unit']),
            model.reward_quantity = int(dic['reward_quantity']),
            model.need_ceiling = int(dic['need_ceiling']),
            model.need_floor = int(dic['need_floor']),
            model.exceeded_ratio = dic['exceeded_ratio'],
            model.experience = dic.get('experience', '0'),
            # model.handling_fee = dic['handling_fee'],
            model.support_token = dic['support_token'],
            model.template_status = int(dic['template_status']),
            model.auto_release = int(dic['auto_release']),
            model.max_bet_ratio = int(dic['max_bet_ratio']),
            model.game_describe = dic['game_describe'],
            model.phase_prefix = dic['phase_prefix'],
            model.phase_date = model.phase_date,
            model.phase_serial = model.phase_serial,
            model.agreement = dic.get('agreement', ''),
            model.agreement_name = dic.get('agreement_name', ''),
            model.merge_threshold = dic.get('merge_threshold', '50')

            session.commit()
            return True

    # 删除数据
    def delete_model(self, dic):
        id = dic.get("id", "")
        if id == '':
            return self.return_error(50001)

        with MysqlTools().session_scope() as session:
            model = session.query(InstantGameTemplateModel).filter(
                InstantGameTemplateModel._id == id).delete()
            if model <= 0:
                return self.return_error(50001)

            session.commit()
            return True

    # 停用/启动
    def modify_model_status(self, dic):
        id = dic.get("id", "")
        if id == '':
            return self.return_error(50001)

        with MysqlTools().session_scope() as session:
            model = session.query(InstantGameTemplateModel).filter(
                InstantGameTemplateModel._id == id).with_for_update().first()
            if model is None == 0:
                return self.return_error(50001)

            if model.template_status == 0:
                model.template_status = 1
            else:
                model.template_status = 0

            session.commit()
            return True


# --------------------- 模板结束-----------------------#

    # 手动发布实例
    def manual_release(self, template_id, game_serial, need, game_describe):
        if not need.isdigit():
            self.return_error(40008)
        # now = int(time.time())
        # time_struct = time.localtime(now)
        # str_time = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)
        str_time = get_utc_now()
        with MysqlTools().session_scope() as session:
            template_info = session.query(InstantGameTemplateModel). \
                filter(InstantGameTemplateModel._id == template_id).first()
            if template_info is None:
                self.return_error(50001)
            if int(template_info.need_ceiling) < int(template_info.need_floor):
                self.return_error(40009)
            need = int(need) * template_info.reward_quantity
            digital_instance_model = InstantGameInstanceModel(
                template_id=template_id,
                game_serial=game_serial,
                game_title=template_info.game_title,
                bet_token=template_info.bet_token,
                bet_unit=template_info.bet_unit,
                support_token=template_info.support_token,
                reward_token=template_info.reward_token,
                reward_quantity=template_info.reward_quantity,
                handling_fee=template_info.handling_fee,
                experience=template_info.experience,
                merge_threshold=template_info.merge_threshold,
                game_describe=game_describe,
                release_time=str_time,
                status=0,
                need=int(need),
                release_type=0,
                chain_status=0
            )
            session.add(digital_instance_model)
            # session.flush()
            session.commit()
        return {
            "status": True
        }

    # 自动发布实例
    def automatic_release(self, session, template_id):
        # now = int(time.time())
        # time_struct = time.localtime(now)
        # str_time = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)
        template_id = 1
        str_time = get_utc_now()
        with MysqlTools().session_scope() as session:
            template_info = session.query(InstantGameTemplateModel). \
                filter(InstantGameTemplateModel._id == template_id).first()
            # 判断存在在"启用"状态 且 自动发布的模板
            if template_info.template_status == 1 and template_info.auto_release == 1:
                # 查询btc 与 usdt 转换比
                btc_usdt_rate = get_exchange_rate(template_info.reward_token)['price']
                if btc_usdt_rate > template_info.need_ceiling or btc_usdt_rate < template_info.need_floor:
                    raise_logger("automatic_release out of rate", 'rs', 'error')
                    return {
                        "status": False
                    }
                need = btc_usdt_rate * template_info.reward_quantity
                game_serial = generate_phase(str(template_info.phase_prefix))
                digital_instance_model = InstantGameInstanceModel(
                    template_id=template_id,
                    game_serial=game_serial,
                    game_title=template_info.game_title,
                    bet_token=template_info.bet_token,
                    bet_unit=template_info.bet_unit,
                    support_token=template_info.support_token,
                    reward_token=template_info.reward_token,
                    reward_quantity=template_info.reward_quantity,
                    handling_fee=template_info.handling_fee,
                    game_describe=template_info.game_describe,
                    experience=template_info.experience,
                    merge_threshold=template_info.merge_threshold,
                    max_bet_ratio=template_info.max_bet_ratio,
                    release_time=str_time,
                    need=int(need),
                    status=-1,
                    release_type=1,
                    chain_status=0
                )
                session.add(digital_instance_model)
                # session.flush()
                session.commit()
            return {
                "status": True
            }

    def instant_game_list(self, limit, offset, game_serial='', release_time_start='', release_time_end='',
                          full_load_time_start='', full_load_time_end='',
                          lottery_time_start='', lottery_time_end='',
                          start_id=None):
        offset = get_offset_by_page(offset, limit)
        result_dict = {
            'limit': limit,
            'offset': offset,
            'count': 0,
            'content': [],
            'total': 0
        }
        with MysqlTools().session_scope() as session:
            q = session.query(InstantGameInstanceModel)
            if game_serial != '':
                q = q.filter(InstantGameInstanceModel.game_serial == game_serial)
            if release_time_start != '':
                q = q.filter(InstantGameInstanceModel.created_at >= release_time_start)
            if release_time_end != '':
                q = q.filter(InstantGameInstanceModel.created_at <= release_time_end)
            if full_load_time_start != '':
                q = q.filter(InstantGameInstanceModel.full_load_time >= full_load_time_start)
            if full_load_time_end != '':
                q = q.filter(InstantGameInstanceModel.full_load_time <= full_load_time_end)
            if lottery_time_start != '':
                q = q.filter(InstantGameInstanceModel.lottery_time >= lottery_time_start)
            if lottery_time_end != '':
                q = q.filter(InstantGameInstanceModel.lottery_time <= lottery_time_end)
            record_count = q.count()
            result_dict['total'] = record_count
            result_dict['count'] = get_page_by_offset(record_count, limit)
            if start_id is not None:
                start_id = str(start_id)
                q = q.filter(InstantGameInstanceModel._id < start_id)
            q = q.order_by(InstantGameInstanceModel.created_at.desc())
            query_result = q.limit(limit).offset(offset).all()
            if query_result is not None:
                for i in query_result:
                    total_bet_number = session.query(
                        func.sum(ParticipateInModel.bet_number * ParticipateInModel.bet_unit)). \
                        filter(ParticipateInModel.game_serial == i.game_serial,
                               ParticipateInModel.pay_token != int(_COIN_ID_EXP)).first()
                    total_bet = 0
                    if total_bet_number[0] is not None:
                        total_bet = int(total_bet_number[0])
                    result_dict['content'].append({
                        'id': i._id,
                        'game_serial': i.game_serial,  # 期号
                        'game_title': i.game_title,
                        'bet_unit': i.bet_unit,
                        'bet_token': self.get_coin_name(i.bet_token),
                        'reward_quantity': i.reward_quantity,  # 奖励数量
                        'reward_token': self.get_coin_name(i.reward_token),  # 奖励币种
                        'release_time': str(i.created_at),  # 上线时间
                        'status': i.status,
                        'need': i.need,  # 本期份额
                        'full_load_time': str(i.full_load_time),  # 超募完成时间
                        'lottery_time': str(i.lottery_time),  # 下线时间
                        'release_type': i.release_type,
                        'participation': i.participation,
                        'total_bet': total_bet
                    })
            return result_dict


if __name__ == "__main__":
    pass
    # GamePublishLotteryServie().checkGameSoldOut("97")
