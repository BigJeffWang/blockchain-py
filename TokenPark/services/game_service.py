import math
import time

from sqlalchemy import distinct, func

from common_settings import *
from config import get_bases_conf, get_tokenpark_url_conf
from models.game_digital_instance_model import GameDigitalInstanceModel
from models.game_digital_template_model import GameDigitalTemplateModel
from models.merge_participate_in_model import MergeParticipateInModel
from models.participate_in_model import ParticipateInModel
from models.robot_account_model import RobotAccountModel
from models.winning_record_model import WinningRecordModel
from services.game_number_set_service import GameNumberSetService
from services.account_service import AccountService
from services.base_service import BaseService
from services.block_chain_info_service import BlockChainInfoService
from tools.mysql_tool import MysqlTools
# 请求的时候, 参数携带
# "limit": 20,  # 每页多少条
# "offset": 1  # 第几页
# 返回的时候:
# 就是处理好的数据
from utils.bet_number_util import create_all_bet_number
from utils.exchange_rate_util import get_exchange_rate
from utils.generate_phase_util import generate_phase
from utils.log import raise_logger
from utils.time_util import get_utc_now
from utils.util import get_offset_by_page, get_page_by_offset, hcf, get_decimal, decimal_to_str


class GameService(BaseService):
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

    def get_game_instance_none_user(self, instance_id):
        with MysqlTools().session_scope() as session:
            instance_info = session.query(GameDigitalInstanceModel). \
                filter(GameDigitalInstanceModel._id == instance_id).first()
            if instance_info is None:
                self.return_error(40005)
            progress = (instance_info.bet_number / instance_info.need) * 100
            # 夺宝进度不足1时 取1
            if 0 < progress < 1:
                progress = 1
            if progress > 1:
                progress = int(progress)
            result = {
                'instance': {
                    'id': instance_info._id,
                    'game_serial': instance_info.game_serial,
                    'game_title': instance_info.game_title,
                    'game_describe': instance_info.game_describe,
                    'progress': progress,
                    'need': instance_info.need,
                    'remain': int(instance_info.need - instance_info.bet_number),
                    'status': instance_info.status,
                    'bet_token': self.get_coin_name(instance_info.bet_token),
                }
            }
            return result

    def get_game_instance(self, instance_id, user_id='', merge_id=''):
        with MysqlTools().session_scope() as session:
            account_service = AccountService()
            instance_info = session.query(GameDigitalInstanceModel). \
                filter(GameDigitalInstanceModel._id == instance_id).first()
            if instance_info is None:
                self.return_error(40005)
            balance_btc = ''
            balance_eth = ''
            balance_usdt = ''
            balance_eos = ''
            balance_exp = ''
            total_bet = 0
            initiate_user_name = ''
            if user_id != '':
                account_balance = account_service.get_user_token_list(user_id, None, 1, 10)['content'][0]
                balance_btc = account_balance['BTC']
                balance_eth = account_balance['ETH']
                if account_balance.get('EOS', None) is not None:
                    balance_eos = account_balance['EOS']
                else:
                    balance_eos = 0
                balance_usdt = account_balance['USDT']
                balance_exp = account_balance['USDT_EXPERIENCE']
            progress = (instance_info.bet_number / instance_info.need) * 100
            # 夺宝进度不足1时 取1
            if 0 < progress < 1:
                progress = 1
            if progress > 1:
                progress = int(progress)
            if merge_id != '':
                total_bet = session.query(func.sum(ParticipateInModel.bet_number * ParticipateInModel.bet_unit). \
                                          label('total')).filter(ParticipateInModel.merge_id == merge_id).first()
                total_bet = int(total_bet.total)
                merge_part_info = session.query(MergeParticipateInModel). \
                    filter(MergeParticipateInModel._id == merge_id).first()
                user_info = account_service.get_inner_user_account_info(session, merge_part_info.initiate_user_id)
                initiate_user_name = user_info['nick_name']
                # user_picture = user_info['profile_picture']
            result = {
                'instance': {
                    'id': instance_info._id,
                    'game_serial': instance_info.game_serial,
                    'game_title': instance_info.game_title,
                    'game_describe': instance_info.game_describe,
                    'progress': progress,
                    'need': instance_info.need,
                    'remain': int(instance_info.need - instance_info.bet_number),
                    'status': instance_info.status,
                    'bet_token': self.get_coin_name(instance_info.bet_token),
                },
                'current_price': {
                    'from': get_exchange_rate(int(_COIN_ID_BTC))['from'],
                    'eth': get_exchange_rate(int(_COIN_ID_ETH))['price'],
                    'btc': get_exchange_rate(int(_COIN_ID_BTC))['price'],
                    'eos': get_exchange_rate(int(_COIN_ID_EOS))['price']
                },
                'balance': {
                    'btc': decimal_to_str(balance_btc, 8),
                    'eth': decimal_to_str(balance_eth, 8),
                    'eos': decimal_to_str(balance_eos, 8),
                    'usdt': decimal_to_str(balance_usdt, 4),
                    'exp': decimal_to_str(balance_exp, 4)
                },
                'merge_info': {
                    'total_bet': total_bet,
                    'bet_token': self.get_coin_name(instance_info.bet_token),
                    'initiate_user_name': initiate_user_name
                }
            }
            return result

    def get_merge_game_instance(self, instance_id, merge_id=''):
        with MysqlTools().session_scope() as session:
            account_service = AccountService()
            instance_info = session.query(GameDigitalInstanceModel). \
                filter(GameDigitalInstanceModel._id == instance_id).first()
            if instance_info is None:
                self.return_error(40005)
            balance_btc = ''
            balance_eth = ''
            balance_usdt = ''
            balance_exp = ''
            total_bet = 0
            initiate_user_name = ''
            progress = (instance_info.bet_number / instance_info.need) * 100
            # 夺宝进度不足1时 取1
            if 0 < progress < 1:
                progress = 1
            if progress > 1:
                progress = int(progress)
            if merge_id != '':
                total_bet = session.query(func.sum(ParticipateInModel.bet_number * ParticipateInModel.bet_unit). \
                                          label('total')).filter(ParticipateInModel.merge_id == merge_id).first()
                total_bet = int(total_bet.total)
                merge_part_info = session.query(MergeParticipateInModel). \
                    filter(MergeParticipateInModel._id == merge_id).first()
                user_info = account_service.get_inner_user_account_info(session, merge_part_info.initiate_user_id)
                initiate_user_name = user_info['nick_name']
                # user_picture = user_info['profile_picture']
            result = {
                'instance': {
                    'id': instance_info._id,
                    'game_serial': instance_info.game_serial,
                    'game_title': instance_info.game_title,
                    'game_describe': instance_info.game_describe,
                    'progress': progress,
                    'need': instance_info.need,
                    'remain': int(instance_info.need - instance_info.bet_number),
                    'status': instance_info.status,
                    'bet_token': self.get_coin_name(instance_info.bet_token),
                },
                'current_price': {
                    'from': get_exchange_rate(int(_COIN_ID_BTC))['from'],
                    'eth': get_exchange_rate(int(_COIN_ID_ETH))['price'],
                    'btc': get_exchange_rate(int(_COIN_ID_BTC))['price']
                },
                'balance': {
                    'btc': balance_btc,
                    'eth': balance_eth,
                    'usdt': balance_usdt,
                    'exp': balance_exp
                },
                'merge_info': {
                    'total_bet': total_bet,
                    'bet_token': self.get_coin_name(instance_info.bet_token),
                    'initiate_user_name': initiate_user_name
                }
            }
            return result

    def get_game_instance_list(self, limit, offset, game_title='', game_serial='', release_time_start='',
                               release_time_end='', full_load_time_start='', full_load_time_end='',
                               status='', release_type='', start_id=None):
        offset = get_offset_by_page(offset, limit)
        result_dict = {
            'limit': limit,
            'offset': offset,
            'count': 0,
            'content': [],
            'total': 0
        }
        with MysqlTools().session_scope() as session:
            q = session.query(GameDigitalInstanceModel)
            if game_title != '':
                q = q.filter(GameDigitalInstanceModel.game_title == game_title)
            if game_serial != '':
                q = q.filter(GameDigitalInstanceModel.game_serial == game_serial)
            if release_time_start != '':
                q = q.filter(GameDigitalInstanceModel.created_at >= release_time_start)
            if release_time_end != '':
                q = q.filter(GameDigitalInstanceModel.created_at <= release_time_end)
            if full_load_time_start != '':
                q = q.filter(GameDigitalInstanceModel.full_load_time >= full_load_time_start)
            if full_load_time_end != '':
                q = q.filter(GameDigitalInstanceModel.full_load_time <= full_load_time_end)
            if status != '':
                q = q.filter(GameDigitalInstanceModel.status == status)
            if release_type != '':
                q = q.filter(GameDigitalInstanceModel.release_type == release_type)
            record_count = q.count()
            result_dict['total'] = record_count
            result_dict['count'] = get_page_by_offset(record_count, limit)
            if start_id is not None:
                start_id = str(start_id)
                q = q.filter(GameDigitalInstanceModel._id < start_id)
            # query_result = q.order_by(GameDigitalInstanceModel.created_at.desc()).limit(limit).offset(offset).all()
            q = q.order_by(GameDigitalInstanceModel.created_at.desc())
            query_result = q.limit(limit).offset(offset).all()
            if query_result is not None:
                for i in query_result:
                    result_dict['content'].append({
                        'id': i._id,
                        'game_serial': i.game_serial,
                        'game_title': i.game_title,
                        'bet_unit': i.bet_unit,
                        'bet_token': self.get_coin_name(i.bet_token),
                        'reward_quantity': i.reward_quantity,
                        'reward_token': self.get_coin_name(i.reward_token),
                        'release_time': str(i.created_at),
                        'status': i.status,
                        'need': i.need,
                        'full_load_time': str(i.full_load_time),
                        'lottery_time': str(i.lottery_time),
                        'release_type': i.release_type,
                        'participation': i.participation
                    })
            return result_dict

    def get_game_template_name_list(self):
        with MysqlTools().session_scope() as session:
            name_arr = []
            name_list = session.query(GameDigitalTemplateModel.game_title,
                                      GameDigitalTemplateModel._id). \
                filter(GameDigitalTemplateModel.template_status == 1).all()
            if name_list is not None:
                for i in name_list:
                    name_arr.append({
                        'id': i._id,
                        'name': i.game_title
                    })
            else:
                self.return_error(40001)
            return name_arr

    def manage_participate_in(self, limit, offset, game_title='', game_serial='', part_in_time_start='',
                              part_in_time_end='', channel='', pay_token='', user_name='', start_id=None,
                              instance_id=''):
        offset = get_offset_by_page(offset, limit)
        result_dict = {
            'limit': limit,
            'offset': offset,
            'count': 0,
            'content': [],
            'total': 0
        }
        with MysqlTools().session_scope() as session:
            account_service = AccountService()
            q = session.query(ParticipateInModel)
            if game_title != '':
                q = q.filter(ParticipateInModel.game_title == game_title)
            if user_name != '':
                q = q.filter(ParticipateInModel.nick_name == user_name)
            if game_serial != '':
                q = q.filter(ParticipateInModel.game_serial == game_serial)
            if part_in_time_start != '':
                q = q.filter(ParticipateInModel.created_at >= part_in_time_start)
            if part_in_time_end != '':
                q = q.filter(ParticipateInModel.created_at <= part_in_time_end)
            if channel != '':
                q = q.filter(ParticipateInModel.channel == channel)
            if pay_token != '':
                q = q.filter(ParticipateInModel.pay_token == pay_token)
            if instance_id != '':
                q = q.filter(ParticipateInModel.game_instance_id == instance_id)
            record_count = q.count()
            result_dict['total'] = record_count
            result_dict['count'] = get_page_by_offset(record_count, limit)
            if start_id is not None:
                start_id = str(start_id)
                q = q.filter(ParticipateInModel._id < start_id)
            q = q.order_by(ParticipateInModel.created_at.desc())
            participate_in_list = q.limit(limit).offset(offset).all()
            for participate in participate_in_list:
                # user_type 0:真实用户  1:机器人
                if participate.user_type == 0:
                    user_info = account_service.get_inner_user_account_info(session, participate.user_id)
                    user_name = user_info['nick_name']
                else:
                    user_name = participate.nick_name
                result_dict['content'].append({
                    'id': participate._id,
                    'game_serial': participate.game_serial,
                    'game_title': participate.game_title,
                    "user": user_name,
                    "bet_time": str(participate.created_at),
                    "channel": participate.channel,
                    "release_type": participate.release_type,
                    # "bet_token": participate.bet_token,
                    # "bet_unit": participate.bet_unit,
                    "bet_number": participate.bet_number,
                    "pay_token": participate.pay_token,
                    "pay_number": str(participate.pay_number)
                })
        return result_dict

    def get_participate_in_list(self, limit, offset, game_instance_id='', start_id=None):
        offset = get_offset_by_page(offset, limit)
        result_dict = {
            'limit': limit,
            'offset': offset,
            'count': 0,
            'content': [],
            'total': 0
        }
        with MysqlTools().session_scope() as session:
            account_service = AccountService()
            q = session.query(ParticipateInModel)
            if game_instance_id != '':
                q = q.filter(ParticipateInModel.game_instance_id == game_instance_id)
            record_count = q.count()
            result_dict['total'] = record_count
            result_dict['count'] = get_page_by_offset(record_count, limit)
            if start_id is not None:
                start_id = str(start_id)
                q = q.filter(ParticipateInModel._id < start_id)
            q = q.order_by(ParticipateInModel.created_at.desc())
            participate_in_list = q.limit(limit).offset(offset).all()
            for participate in participate_in_list:
                # user_type 0:真实用户  1:机器人
                if participate.user_type == 0:
                    user_info = account_service.get_inner_user_account_info(session, participate.user_id)
                    user_name = user_info['nick_name']
                else:
                    user_name = participate.nick_name
                result_dict['content'].append({
                    "id": participate._id,
                    "user": user_name,
                    "bet_time": str(participate.created_at),
                    "channel": participate.channel,
                    "bet_token": participate.bet_token,
                    "bet_unit": participate.bet_unit,
                    "bet_number": participate.bet_number,
                    "pay_token": participate.pay_token,
                    "pay_number": str(participate.pay_number)
                })
        return result_dict

    def current_period_info(self, instance_id):
        bet_serial = '----'
        user_name = '----'
        with MysqlTools().session_scope() as session:
            instance_info = session.query(GameDigitalInstanceModel). \
                filter(GameDigitalInstanceModel._id == instance_id).first()
            if instance_info is None:
                self.return_error(40005)
            template_info = session.query(GameDigitalTemplateModel). \
                filter(GameDigitalTemplateModel._id == instance_info.template_id).first()
            if template_info is None:
                self.return_error(50001)
            winning_info = session.query(WinningRecordModel). \
                filter(WinningRecordModel.game_instance_id == instance_id).first()
            if winning_info is not None:
                bet_serial = winning_info.bet_serial
                account_service = AccountService()
                user_info = account_service.get_inner_user_account_info(session, winning_info.user_id)
                user_name = user_info['nick_name']
            result = {
                'template_info': {
                    'game_title': template_info.game_title,
                    'created_at': str(template_info.created_at),
                    'update_at': str(template_info.update_at),
                    'bet_token': template_info.bet_token,
                    'reward_token': template_info.reward_token,
                    'bet_unit': template_info.bet_unit,
                    'reward_quantity': template_info.reward_quantity,
                    'support_token': template_info.support_token,
                    'need': str(template_info.need_floor) + '~' + str(template_info.need_ceiling),
                    'phase': str(template_info.phase_prefix + 'YYMMDD0001'),
                    'template_status': template_info.template_status,
                    'auto_release': template_info.auto_release,
                    'handling_fee': str(template_info.handling_fee) + '%',
                    'exceeded_ratio': str(template_info.exceeded_ratio) + '%',
                    'agreement': template_info.agreement,
                    'game_describe': template_info.game_describe
                },
                'instance_info': {
                    'game_serial': instance_info.game_serial,
                    'status': instance_info.status,
                    'release_time': str(instance_info.created_at),
                    'full_load_time': str(instance_info.full_load_time),
                    'release_type': instance_info.release_type,
                    'need': instance_info.need,
                    'lottery_time': str(instance_info.lottery_time),
                    'bet_serial': bet_serial,
                    'user_name': user_name
                }
            }
        return result

    def get_manual_release_info(self, template_id):
        with MysqlTools().session_scope() as session:
            template_info = session.query(GameDigitalTemplateModel). \
                filter(GameDigitalTemplateModel._id == template_id).first()
            if template_info is None:
                self.return_error(50001)
            game_serial = generate_phase(template_info.phase_prefix)
            result = {
                'template_info': {
                    'game_title': template_info.game_title,
                    'created_at': str(template_info.created_at),
                    'update_at': str(template_info.update_at),
                    'bet_token': template_info.bet_token,
                    'bet_unit': template_info.bet_unit,
                    'reward_token': template_info.reward_token,
                    'reward_quantity': template_info.reward_quantity,
                    'support_token': template_info.support_token,
                    'need': str(template_info.need_floor) + '~' + str(template_info.need_ceiling),
                    'phase': str(template_info.phase_prefix + 'YYMMDD0001'),
                    'template_status': template_info.template_status,
                    'auto_release': template_info.auto_release,
                    'handling_fee': str(template_info.handling_fee) + '%',
                    'exceeded_ratio': str(template_info.exceeded_ratio) + '%',
                    'agreement': template_info.agreement,
                    'game_describe': template_info.game_describe
                },
                'game_serial': game_serial
            }
        return result

    # 手动发布实例
    def manual_release(self, template_id, game_serial, need, game_describe):
        if not need.isdigit():
            self.return_error(40008)
        # now = int(time.time())
        # time_struct = time.localtime(now)
        # str_time = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)
        str_time = get_utc_now()
        with MysqlTools().session_scope() as session:
            template_info = session.query(GameDigitalTemplateModel). \
                filter(GameDigitalTemplateModel._id == template_id).first()
            if template_info is None:
                self.return_error(50001)
            if int(template_info.need_ceiling) < int(template_info.need_floor):
                self.return_error(40009)
            need = int(need) * template_info.reward_quantity * ((100 + template_info.exceeded_ratio) / 100)
            digital_instance_model = GameDigitalInstanceModel(
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
            # if create_all_bet_number(game_serial, int(need)) != 2000:
            #     self.return_error(40015)
            if not GameNumberSetService().createNumbers({"game_serial": game_serial, "total": int(need)}):
                self.return_error(40015)
            session.add(digital_instance_model)
            session.flush()
            try:
                # 项目发布数据上链
                if BlockChainInfoService().insert_block_chain_info('', str(digital_instance_model._id), 2,
                                                                   {
                                                                       "instance_id": digital_instance_model._id,
                                                                       "template_id": template_id,
                                                                       "game_serial": game_serial,
                                                                       "bet_token": template_info.bet_token,
                                                                       "bet_unit": template_info.bet_unit,
                                                                       "reward_token": template_info.reward_token,
                                                                       "reward_quantity": template_info.reward_quantity,
                                                                       "handling_fee": str(template_info.handling_fee),
                                                                       "game_describe": template_info.game_describe,
                                                                       "release_time": str_time.strftime(
                                                                           "%Y-%m-%d %H:%M:%S"),
                                                                       "status": 0,
                                                                       "need": int(need),
                                                                       "release_type": 0,
                                                                   }):
                    digital_instance_model.chain_status = 1
                else:
                    raise_logger("insert_block_chain_info fail", 'rs_error')
            except Exception as e:
                # raise_logger("manual_release fail", 'rs', 'error')
                raise_logger("insert_block_chain_info fail", 'rs', 'error')
                # session.rollback()
                # self.return_error(40010)
            session.commit()
        return {
            "status": True
        }

    # 自动发布实例
    def automatic_release(self, session, template_id):
        # now = int(time.time())
        # time_struct = time.localtime(now)
        # str_time = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)
        str_time = get_utc_now()
        with MysqlTools().session_scope() as session:
            template_info = session.query(GameDigitalTemplateModel). \
                filter(GameDigitalTemplateModel._id == template_id).first()
            # 判断存在在"启用"状态 且 自动发布的模板
            if template_info.template_status == 1 and template_info.auto_release == 1:
                # 查询btc 与 usdt 转换比
                btc_usdt_rate = get_exchange_rate(template_info.reward_token)['price']
                if btc_usdt_rate > template_info.need_ceiling or btc_usdt_rate < template_info.need_floor:
                    raise_logger("automatic_release out of rate", 'rs', 'error')
                    return {
                        "status": False
                    }
                instance_info = session.query(GameDigitalInstanceModel). \
                    filter(GameDigitalInstanceModel.template_id == template_id,
                           # GameDigitalInstanceModel.release_type == 1,  # 自动发布
                           GameDigitalInstanceModel.status == 0).all()  # 夺宝中
                if instance_info is None or len(instance_info) <= 0:
                    need = btc_usdt_rate * template_info.reward_quantity * \
                           ((100 + template_info.exceeded_ratio) / 100)
                    game_serial = generate_phase(str(template_info.phase_prefix))
                    digital_instance_model = GameDigitalInstanceModel(
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
                        release_time=str_time,
                        need=int(need),
                        status=0,
                        release_type=1,
                        chain_status=0
                    )
                    # if create_all_bet_number(game_serial, int(need)) != 2000:
                    #     self.return_error(40015)
                    if not GameNumberSetService().createNumbers({"game_serial": game_serial, "total": int(need)}):
                        self.return_error(40015)
                    session.add(digital_instance_model)
                    session.flush()
                    try:
                        # 项目发布数据上链
                        if BlockChainInfoService().insert_block_chain_info('', str(digital_instance_model._id), 2,
                                                                           {
                                                                               "instance_id": digital_instance_model._id,
                                                                               "template_id": template_id,
                                                                               "game_serial": game_serial,
                                                                               "bet_token": template_info.bet_token,
                                                                               "bet_unit": template_info.bet_unit,
                                                                               "reward_token": template_info.reward_token,
                                                                               "reward_quantity": template_info.reward_quantity,
                                                                               "handling_fee": str(
                                                                                   template_info.handling_fee),
                                                                               "game_describe": template_info.game_describe,
                                                                               "release_time": str_time.strftime(
                                                                                   "%Y-%m-%d %H:%M:%S"),
                                                                               "status": 0,
                                                                               "need": int(need),
                                                                               "release_type": 0,
                                                                           }):
                            digital_instance_model.chain_status = 1
                        else:
                            raise_logger("insert_block_chain_info fail", 'rs', 'error')
                    except Exception as e:
                        raise_logger("automatic_release fail", 'rs', 'error')
                        # session.rollback()
                    session.commit()
            return {
                "status": True
            }

    def get_winning_record(self, timezone, instance_id=''):
        with MysqlTools().session_scope() as session:
            winning_user = '----'
            if instance_id == '':
                instance_info = session.query(GameDigitalInstanceModel). \
                    filter(GameDigitalInstanceModel.status == 2). \
                    order_by(GameDigitalInstanceModel.lottery_time.desc()).first()
                if instance_info is None:
                    return {
                        'is_empty': True
                    }
            else:
                instance_info = session.query(GameDigitalInstanceModel). \
                    filter(GameDigitalInstanceModel._id == instance_id).first()
                if instance_info is None:
                    self.return_error(40005)
            winning_record = session.query(WinningRecordModel). \
                filter(WinningRecordModel.game_instance_id == instance_info._id).first()
            if winning_record is None:
                self.return_error(40006)

            if winning_record.user_type == 0:
                account_service = AccountService()
                user_info = account_service.get_inner_user_account_info(session, winning_record.user_id)
                winning_user = user_info['nick_name']
            if winning_record.user_type == 1:
                robot = session.query(RobotAccountModel).filter(
                    RobotAccountModel.user_id == winning_record.user_id).first()
                winning_user = robot.nick_name
            hc = hcf(int(winning_record.bet_number), int(instance_info.need))
            block_info = BlockChainInfoService().project_block_info(instance_info._id, timezone)
            result = {
                'is_empty': False,
                'instance_id': instance_info._id,
                'game_serial': instance_info.game_serial,
                'reward_token': instance_info.reward_token,
                'reward_quantity': instance_info.reward_quantity,
                'winning_user': winning_user,
                'lottery_time': str(instance_info.lottery_time),
                'full_load_time': str(instance_info.full_load_time),
                'participation': instance_info.participation,
                'bet_serial': winning_record.bet_serial,
                'need': instance_info.need,
                'probability': str(int(int(winning_record.bet_number) / hc)) + '/' + str(
                    int(int(instance_info.need) / hc)),
                'bet_hash': winning_record.bet_hash,
                'merge_id': winning_record.merge_id,
                'block_info': block_info
            }
        return result

    def instance_blockchain_info(self, instance_id, timezone):
        release_time = '---------------'
        full_load_time = '---------------'
        lottery_time = '---------------'
        with MysqlTools().session_scope() as session:
            winning_info = {
                'winning_user': '----',
                'probability': '',
                'bet_serial': '',
                'bet_hash': ''
            }
            instance_info = session.query(GameDigitalInstanceModel). \
                filter(GameDigitalInstanceModel._id == instance_id).first()
            if instance_info is None:
                self.return_error(40005)
            if instance_info.status == 2:
                release_time = str(instance_info.release_time)
                full_load_time = str(instance_info.full_load_time)
                lottery_time = str(instance_info.lottery_time)
            elif instance_info.status == 0:
                release_time = str(instance_info.release_time)
            elif instance_info.status == 1:
                release_time = str(instance_info.release_time)
                full_load_time = str(instance_info.full_load_time)
            winning_record = session.query(WinningRecordModel). \
                filter(WinningRecordModel.game_instance_id == instance_info._id).first()
            if winning_record is not None:
                if winning_record.user_type == 0:
                    account_service = AccountService()
                    user_info = account_service.get_inner_user_account_info(session, winning_record.user_id)
                    winning_info['winning_user'] = user_info['nick_name']
                if winning_record.user_type == 1:
                    robot = session.query(RobotAccountModel).filter(
                        RobotAccountModel.user_id == winning_record.user_id).first()
                    winning_info['winning_user'] = robot.nick_name
                hc = hcf(int(winning_record.bet_number), int(instance_info.need))
                winning_info['probability'] = str(int(int(winning_record.bet_number) / hc)) + '/' + str(
                    int(int(instance_info.need) / hc))
                winning_info['bet_serial'] = winning_record.bet_serial
                winning_info['bet_hash'] = winning_record.bet_hash
            block_info = BlockChainInfoService().project_block_info(instance_info._id, timezone)
            progress = (instance_info.bet_number / instance_info.need) * 100
            if 0 < progress < 1:
                progress = 1
            if progress > 1:
                progress = int(progress)
            result = {
                'game_title': instance_info.game_title,
                'instance_id': instance_info._id,
                'game_serial': instance_info.game_serial,
                'winning_user': winning_info['winning_user'],
                'release_time': release_time,
                'lottery_time': lottery_time,
                'full_load_time': full_load_time,
                'participation': instance_info.participation,
                'bet_serial': winning_info['bet_serial'],
                'need': instance_info.need,
                'probability': winning_info['probability'],
                'progress': progress,
                'remain': int(instance_info.need - instance_info.bet_number),
                'bet_token': self.get_coin_name(instance_info.bet_token),
                'bet_hash': winning_info['bet_hash'],
                'block_info': block_info
            }
        return result

    def hero_list(self):
        account_service = AccountService()
        with MysqlTools().session_scope() as session:
            heroes_list = session.query(WinningRecordModel.user_id, WinningRecordModel.reward_token,
                                        WinningRecordModel.user_type,
                                        func.sum(WinningRecordModel.reward_quantity).label('total_reward')). \
                group_by(WinningRecordModel.user_id). \
                order_by(func.sum(WinningRecordModel.reward_quantity).desc()).limit(5).all()
            result_dict = []
            for i in heroes_list:
                if i.user_type == 0:
                    user_info = account_service.get_inner_user_account_info(session, i.user_id)
                    user_name = user_info['nick_name']
                else:
                    robot = session.query(RobotAccountModel).filter(
                        RobotAccountModel.user_id == i.user_id).first()
                    user_name = robot.nick_name
                result_dict.append({
                    "user_name": user_name,
                    "total_reward": str(i.total_reward)
                })
        return result_dict

    # 获取实时币价
    @staticmethod
    def get_current_price():
        return {
            'eth': get_exchange_rate(int(_COIN_ID_ETH))['price'],
            'btc': get_exchange_rate(int(_COIN_ID_BTC))['price']
        }

    # 数字Game实体 添加已投注数 和 人数
    def modifyDigitalInstance(self, model, dic: dict):
        if model is None:
            return False
        try:
            sum_bet_number = model.bet_number + dic.get("add_bet_number", 0)
            model.bet_number = sum_bet_number
            model.participation = model.participation + dic.get("add_people", 0)
            if model.need == sum_bet_number and model.status == 0:
                model.status = 1
                # now = int(time.time())
                # time_struct = time.localtime(now)
                # full_time = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)

                # full_time = get_utc_now()
                full_time = dic.get("full_load_time", get_utc_now())
                model.full_load_time = full_time

            if dic.get("lottery_time", "") != "":
                model.lottery_time = dic.get("lottery_time")
                model.status = 2

            return True

        except Exception as e:
            # print("return_error---modifyDigitalInstance")

            return False

    def merge_participate_in_list(self, limit, offset, game_instance_id, start_id=None):
        offset = get_offset_by_page(offset, limit)
        result_dict = {
            'limit': limit,
            'offset': offset,
            'count': 0,
            'content': [],
            'total': 0
        }
        with MysqlTools().session_scope() as session:
            account_service = AccountService()
            q = session.query(MergeParticipateInModel). \
                filter(MergeParticipateInModel.game_instance_id == game_instance_id)
            record_count = q.count()
            result_dict['total'] = record_count
            result_dict['count'] = get_page_by_offset(record_count, limit)
            if start_id is not None:
                start_id = str(start_id)
                q = q.filter(MergeParticipateInModel._id < start_id)
            q = q.order_by(MergeParticipateInModel.created_at.desc())
            merge_participate_in_list = q.limit(limit).offset(offset).all()
            partin_info_list = session.query(ParticipateInModel). \
                filter(ParticipateInModel.game_instance_id == game_instance_id).all()
            for participate in merge_participate_in_list:
                participation = 0
                bet_token = ''
                bet_unit = 1
                bet_number = 0
                user_info = account_service.get_inner_user_account_info(session, participate.initiate_user_id)
                user_name = user_info['nick_name']
                user_picture = user_info['profile_picture']
                for partin_info in partin_info_list:
                    if participate._id == partin_info.merge_id:
                        participation += 1
                        bet_number += partin_info.bet_number
                        bet_token = partin_info.bet_token
                        bet_unit = partin_info.bet_unit
                result_dict['content'].append({
                    "id": participate._id,
                    "initiate_user": user_name,
                    "user_picture": user_picture,
                    "participation": participation,
                    "bet_number_total": bet_number * bet_unit,
                    "bet_token": self.get_coin_name(bet_token),
                    # "bet_unit": bet_unit
                })
        return result_dict

    def initiate_merge(self, user_id, instance_id, part_in_id):
        conf = get_tokenpark_url_conf()
        merge_id = 0
        user_name = ''
        account_service = AccountService()
        with MysqlTools().session_scope() as session:
            try:
                part_in_info = session.query(ParticipateInModel). \
                    filter(ParticipateInModel._id == part_in_id).first()
                if part_in_info is None:
                    self.return_error(40016)
                # if part_in_info.bet_number * part_in_info.bet_unit < 100:
                #     self.return_error(40017)
                user_info = account_service.get_inner_user_account_info(session, user_id)
                user_name = user_info['nick_name']
                merge_participate_in = MergeParticipateInModel(
                    initiate_user_id=user_id,
                    game_instance_id=instance_id,
                    participate_in_id=part_in_id
                )
                session.add(merge_participate_in)
                session.flush()
                part_in_info.merge_id = merge_participate_in._id
                merge_id = merge_participate_in._id
                session.commit()
            except Exception as e:
                raise_logger("initiate_merge fail", 'rs', 'error')
                session.rollback()
                self.return_error(40019)
        return {
            "status": True,
            "url": str(conf['url']) + str(instance_id) + '/' + str(merge_id),
            "initiate_user_name": user_name
        }

    def merge_info_list(self, limit, offset, merge_id, game_instance_id):
        offset = get_offset_by_page(offset, limit)
        result_dict = {
            'limit': limit,
            'offset': offset,
            'count': 0,
            'content': [],
            'total': 0,
            'total_bet': 0,
            'bet_token': self.get_coin_name(_COIN_ID_USDT),
        }
        with MysqlTools().session_scope() as session:
            account_service = AccountService()
            winning_record = session.query(WinningRecordModel.reward_token,
                                           WinningRecordModel.reward_quantity). \
                filter(WinningRecordModel.game_instance_id == game_instance_id).first()
            if winning_record is None:
                self.return_error(40006)
            total_bet = session.query(func.sum(ParticipateInModel.bet_number * ParticipateInModel.bet_unit). \
                                      label('total')).filter(ParticipateInModel.merge_id == merge_id).first()
            result_dict['total_bet'] = int(total_bet.total)
            q = session.query(ParticipateInModel). \
                filter(ParticipateInModel.merge_id == merge_id)
            record_count = q.count()
            result_dict['total'] = record_count
            result_dict['count'] = get_page_by_offset(record_count, limit)
            q = q.order_by(ParticipateInModel.created_at.asc())
            participate_in_list = q.limit(limit).offset(offset).all()
            for participate in participate_in_list:
                pay_number = participate.bet_number / int(total_bet.total) * winning_record.reward_quantity
                if participate.user_type == 0:
                    user_info = account_service.get_inner_user_account_info(session, participate.user_id)
                    user_name = user_info['nick_name']
                else:
                    user_name = participate.nick_name
                result_dict['content'].append({
                    "user_name": user_name,
                    "bet_token": self.get_coin_name(participate.bet_token),
                    "bet_unit": participate.bet_unit,
                    "bet_number": participate.bet_number,
                    "reward_token": self.get_coin_name(winning_record.reward_token),
                    "pay_number": decimal_to_str(pay_number, 8),
                })
        return result_dict

    def latest_available_instance(self):
        with MysqlTools().session_scope() as session:
            instance_info = session.query(GameDigitalInstanceModel). \
                filter(GameDigitalInstanceModel.status == 0). \
                order_by(GameDigitalInstanceModel.created_at.desc()).first()
            if instance_info is None:
                self.return_error(40018)
        return {
            "instance_id": instance_info._id
        }

    def merge_detail_list(self, limit, offset, game_instance_id, merge_id, start_id=None):
        offset = get_offset_by_page(offset, limit)
        result_dict = {
            'limit': limit,
            'offset': offset,
            'count': 0,
            'content': [],
            'total': 0
        }
        with MysqlTools().session_scope() as session:
            account_service = AccountService()
            merge_info = session.query(MergeParticipateInModel). \
                filter(MergeParticipateInModel._id == merge_id).first()
            q = session.query(ParticipateInModel). \
                filter(ParticipateInModel.game_instance_id == game_instance_id,
                       ParticipateInModel.merge_id == merge_id)
            record_count = q.count()
            result_dict['total'] = record_count
            result_dict['count'] = get_page_by_offset(record_count, limit)
            if start_id is not None:
                start_id = str(start_id)
                q = q.filter(ParticipateInModel._id < start_id)
            q = q.order_by(ParticipateInModel.created_at.desc())
            merge_detail_list = q.limit(limit).offset(offset).all()
            for detail in merge_detail_list:
                is_init_user = False
                if detail.user_id == merge_info.initiate_user_id:
                    is_init_user = True
                user_info = account_service.get_inner_user_account_info(session, detail.user_id)
                result_dict['content'].append({
                    'id': detail._id,
                    'is_init_user': is_init_user,
                    'user_name': user_info['nick_name'],
                    'user_picture': user_info['profile_picture'],
                    # 'part_in_time': detail.created_at.strftime("%m/%d %H:%M:%S"),
                    'part_in_time': str(detail.created_at),
                    'bet_number': detail.bet_number,
                    'bet_unit': detail.bet_unit,
                    'bet_token': self.get_coin_name(detail.bet_token),
                })
        return result_dict
