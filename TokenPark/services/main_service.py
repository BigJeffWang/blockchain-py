from models.announcement_manage_model import AnnouncementManageModel
from models.app_upgrade_model import AppUpgradeModel
from models.banner_manage_model import BannerManageModel
from models.game_digital_instance_model import GameDigitalInstanceModel
from models.instant_game_instance_model import InstantGameInstanceModel
from models.merge_participate_in_model import MergeParticipateInModel
from models.participate_in_model import ParticipateInModel
from models.robot_account_model import RobotAccountModel
from models.winning_record_model import WinningRecordModel
from services.account_service import AccountService
from services.base_service import BaseService
from tools.mysql_tool import MysqlTools
from utils.util import get_offset_by_page, get_page_by_offset, hcf, decimal_to_str
from common_settings import *
from sqlalchemy import func, distinct
import re
import math


class MainService(BaseService):
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

    def main_page(self):
        with MysqlTools().session_scope() as session:
            account_service = AccountService()
            banners = []
            announcements = []
            participates = []
            instance_info = {}
            merges = []
            banner_list = session.query(BannerManageModel). \
                filter(BannerManageModel.status == 1).all()
            if len(banner_list) > 0:
                for banner in banner_list:
                    banners.append({
                        'image': banner.image,
                        'site': banner.site
                    })
            announcement_list = session.query(AnnouncementManageModel). \
                filter(AnnouncementManageModel.status == 1).all()
            if len(announcement_list) > 0:
                for announcement in announcement_list:
                    announcements.append({
                        'title': announcement.title,
                        'site': announcement.site
                    })
            participate_list = session.query(ParticipateInModel). \
                order_by(ParticipateInModel.created_at.desc()).limit(5).offset(0).all()
            if len(participate_list) > 0:
                for participate in participate_list:
                    if participate.user_type == 0:
                        user_info = account_service.get_inner_user_account_info(session, participate.user_id)
                        user_name = user_info['nick_name']
                    else:
                        user_name = participate.nick_name
                    participates.append({
                        "user": user_name,
                        "bet_time": str(participate.created_at),
                        "channel": participate.channel,
                        "bet_token": participate.bet_token,
                        "bet_number": participate.bet_number,
                        "pay_token": participate.pay_token,
                        "pay_number": str(participate.pay_number)
                    })
            instance = session.query(GameDigitalInstanceModel). \
                order_by(GameDigitalInstanceModel.status.asc(),
                         GameDigitalInstanceModel.created_at.desc()).first()

            ins_instance = session.query(InstantGameInstanceModel). \
                order_by(InstantGameInstanceModel.status.asc(),
                         InstantGameInstanceModel.created_at.desc()).first()
            if ins_instance is None:
                ins_instance = {
                    'id': '',
                    'game_serial': '',
                    # 'game_title': instance.game_title,
                    # 'game_describe': instance.game_describe,
                    # 'status': instance.status,
                    'support_token': '',
                    'reward_token': '',
                    'reward_quantity': '',
                }
            else:
                ins_instance = {
                    'id': ins_instance._id,
                    'game_serial': ins_instance.game_serial,
                    'support_token': ins_instance.support_token,
                    'reward_token': ins_instance.reward_token,
                    'reward_quantity': ins_instance.reward_quantity,
                }
            winner = ''
            bet_serial = ''
            bet_number = 0
            merge_id = -1
            if instance is not None:
                merge_list = session.query(MergeParticipateInModel). \
                    filter(MergeParticipateInModel.game_instance_id == instance._id). \
                    order_by(MergeParticipateInModel.created_at.desc()).limit(3).offset(0).all()
                if len(merge_list) > 0:
                    merge_id = 1
                    for merge in merge_list:
                        initiate_user = account_service.get_inner_user_account_info(session, merge.initiate_user_id)
                        merges.append({
                            'merge_id': merge._id,
                            'name': initiate_user['nick_name'],
                            'portrait': initiate_user['profile_picture']
                        })
                if instance.status == 2:
                    winning_record = session.query(WinningRecordModel). \
                        filter(WinningRecordModel.game_instance_id == instance._id).first()
                    if winning_record is not None:
                        if winning_record.user_type == 0:
                            account_service = AccountService()
                            user_info = account_service.get_inner_user_account_info(session, winning_record.user_id)
                            winner = user_info['nick_name']
                        elif winning_record.user_type == 1:
                            robot = session.query(RobotAccountModel).filter(
                                RobotAccountModel.user_id == winning_record.user_id).first()
                            winner = robot.nick_name
                        else:
                            winner = 'X@17Yau8'
                        bet_serial = winning_record.bet_serial
                        merge_id = winning_record.merge_id
                        bet_number = winning_record.bet_number
                # progress = 0
                progress = (instance.bet_number / instance.need) * 100
                if 0 < progress < 1:
                    progress = 1
                if progress > 1:
                    progress = int(progress)
                result = {
                    'banner_list': banners,
                    'announcement_list': announcements,
                    'ins_instance': ins_instance,
                    'instance': {
                        'id': instance._id,
                        'game_serial': instance.game_serial,
                        'game_title': instance.game_title,
                        'game_describe': instance.game_describe,
                        'progress': progress,
                        'remain': int(instance.need - instance.bet_number),
                        'status': instance.status,
                        'lottery_time': str(instance.lottery_time),
                        'winners': winner,
                        'bet_serial': bet_serial,
                        'bet_token': self.get_coin_name(instance.bet_token),
                        'bet_number': bet_number,
                        'reward_token': self.get_coin_name(instance.reward_token),
                        'reward_quantity': instance.reward_quantity,
                        'merge_id': merge_id,
                        'merge_list': merges
                    },
                    'participate': participates
                }
            else:
                result = {
                    'banner_list': banners,
                    'announcement_list': announcements,
                    'instance': {},
                    'participate': participates
                }
        return result

    def game_instance_info_list(self, limit, offset, status='', start_id=None):
        offset = get_offset_by_page(offset, limit)
        result_dict = {
            'limit': limit,
            'offset': offset,
            'count': 0,
            'content': []
        }
        account_service = AccountService()
        with MysqlTools().session_scope() as session:
            if status != '':
                q = session.query(GameDigitalInstanceModel). \
                    order_by(GameDigitalInstanceModel.status.asc(),
                             GameDigitalInstanceModel.created_at.desc(),
                             GameDigitalInstanceModel._id != 0)
                q = q.filter(GameDigitalInstanceModel.status == status)
            else:
                q = session.query(GameDigitalInstanceModel). \
                    order_by(GameDigitalInstanceModel.created_at.desc(),
                             GameDigitalInstanceModel._id != 0)
            record_count = q.count()
            result_dict['count'] = get_page_by_offset(record_count, limit)
            if start_id is not None:
                start_id = str(start_id)
                q = q.filter(GameDigitalInstanceModel._id < start_id)
            query_result = q.limit(limit).offset(offset).all()
            winner = ''
            bet_serial = ''
            bet_number = 0
            # --------------- 即时开 --------------- #
            if status == '':
                ins_instance = session.query(InstantGameInstanceModel). \
                    order_by(InstantGameInstanceModel.created_at.desc()).first()
                if ins_instance is not None:
                    result_dict['content'].append({
                        'id': ins_instance._id,
                        'created_at': str(ins_instance.created_at),
                        'game_serial': ins_instance.game_serial,
                        'game_title': ins_instance.game_title,
                        'progress': 0,
                        'remain': 0,
                        'bet_token': self.get_coin_name(ins_instance.bet_token),
                        'bet_number': 0,
                        'reward_token': self.get_coin_name(ins_instance.reward_token),
                        'reward_quantity': ins_instance.reward_quantity,
                        'support_token': ins_instance.support_token,
                        'status': -1,
                        'lottery_time': str(ins_instance.lottery_time),
                        'winners': '',
                        'bet_serial': '',
                        'game_describe': ins_instance.game_describe,
                        'participation': ins_instance.participation,
                        'merge_id': -1,
                        'merge_list': []
                    })
            # --------------- 即时开end --------------- #
            for i in query_result:
                merge_id = -1
                merges = []
                merge_list = session.query(MergeParticipateInModel). \
                    filter(MergeParticipateInModel.game_instance_id == i._id). \
                    order_by(MergeParticipateInModel.created_at.desc()).limit(3).offset(0).all()
                if len(merge_list) > 0:
                    merge_id = 1
                    for merge in merge_list:
                        initiate_user = account_service.get_inner_user_account_info(session, merge.initiate_user_id)
                        merges.append({
                            'merge_id': merge._id,
                            'name': initiate_user['nick_name'],
                            'portrait': initiate_user['profile_picture']
                        })
                if i.status == 2:
                    winning_record = session.query(WinningRecordModel). \
                        filter(WinningRecordModel.game_instance_id == i._id).first()
                    if winning_record is not None:
                        if winning_record.user_type == 0:
                            account_service = AccountService()
                            user_info = account_service.get_inner_user_account_info(session, winning_record.user_id)
                            winner = user_info['nick_name']
                        elif winning_record.user_type == 1:
                            robot = session.query(RobotAccountModel).filter(
                                RobotAccountModel.user_id == winning_record.user_id).first()
                            winner = robot.nick_name
                        else:
                            winner = 'X@17Yau8'
                        bet_serial = winning_record.bet_serial
                        merge_id = winning_record.merge_id
                        bet_number = winning_record.bet_number
                progress = 0
                progress = (i.bet_number / i.need) * 100
                if 0 < progress < 1:
                    progress = 1
                if progress > 1:
                    progress = int(progress)

                result_dict['content'].append({
                    'id': i._id,
                    'created_at': str(i.created_at),
                    'game_serial': i.game_serial,
                    'game_title': i.game_title,
                    'progress': progress,
                    'remain': int(i.need - i.bet_number),
                    'bet_token': self.get_coin_name(i.bet_token),
                    'bet_number': bet_number,
                    'reward_token': self.get_coin_name(i.reward_token),
                    'reward_quantity': i.reward_quantity,
                    'support_token': i.support_token,
                    'status': i.status,
                    'lottery_time': str(i.lottery_time),
                    'winners': winner,
                    'bet_serial': bet_serial,
                    'game_describe': i.game_describe,
                    'participation': i.participation,
                    'merge_id': merge_id,
                    'merge_list': merges
                })
        return result_dict

    def indiana_record(self, limit, offset, user_id, start_id=None):
        offset = get_offset_by_page(offset, limit)
        result_dict = {
            'limit': limit,
            'offset': offset,
            'count': 0,
            'content': []
        }
        with MysqlTools().session_scope() as session:
            q = session.query(ParticipateInModel._id,
                              ParticipateInModel.game_instance_id, ParticipateInModel.game_serial,
                              ParticipateInModel.bet_token,
                              (ParticipateInModel.bet_unit * ParticipateInModel.bet_number).label(
                                  'total_bet'),
                              ParticipateInModel.merge_id, ParticipateInModel.created_at,
                              ParticipateInModel.pay_token, ParticipateInModel.pay_number). \
                filter(ParticipateInModel.user_id == user_id). \
                order_by(ParticipateInModel.created_at.desc())
            record_count = q.count()
            result_dict['count'] = get_page_by_offset(record_count, limit)
            if start_id is not None:
                start_id = str(start_id)
                q = q.filter(ParticipateInModel._id < start_id)
            participate_list = q.limit(limit).offset(offset).all()
            for i in participate_list:
                instance_info = session.query(GameDigitalInstanceModel.need, GameDigitalInstanceModel.status,
                                              GameDigitalInstanceModel.bet_token,
                                              GameDigitalInstanceModel.participation). \
                    filter(GameDigitalInstanceModel._id == i.game_instance_id).first()
                if instance_info is None:
                    continue
                total = instance_info.participation
                lower = session.query((func.count(ParticipateInModel._id)).label('lower_users')). \
                    filter(ParticipateInModel.game_instance_id == i.game_instance_id,
                           ParticipateInModel.bet_unit * ParticipateInModel.bet_number < int(i.total_bet)). \
                    first()
                hc = hcf(int(i.total_bet), int(instance_info.need))
                probability = str(int(int(i.total_bet) / hc)) + '/' + str(
                    int(int(instance_info.need) / hc))
                if lower is None:
                    lower = total
                else:
                    lower = lower.lower_users
                if int(i.pay_token) == int(_COIN_ID_EXP):
                    pay_number = int(i.pay_number)
                else:
                    pay_number = decimal_to_str(i.pay_number, 8)
                result_dict['content'].append({
                    'instance_id': i.game_instance_id,
                    'participate_id': i._id,
                    'game_serial': i.game_serial,
                    'bet_token': self.get_coin_name(i.bet_token),
                    'total_bet': int(i.total_bet),
                    'need': instance_info.need,
                    'status': instance_info.status,
                    'need_token': self.get_coin_name(instance_info.bet_token),
                    'probability': probability,
                    'ranking': math.ceil((lower / total) * 100),
                    'merge_id': i.merge_id,
                    'part_in_time': str(i.created_at),
                    "pay_token": self.get_coin_name(i.pay_token),
                    "pay_number": pay_number
                })

        return result_dict

    def indiana_record_new(self, limit, offset, user_id, start_id=None):
        offset = get_offset_by_page(offset, limit)
        result_dict = {
            'limit': limit,
            'offset': offset,
            'count': 0,
            'content': []
        }
        with MysqlTools().session_scope() as session:
            q = session.query(ParticipateInModel._id,
                              ParticipateInModel.game_instance_id, ParticipateInModel.game_serial,
                              ParticipateInModel.bet_token,
                              ParticipateInModel.award_numbers,
                              ParticipateInModel.win_number,
                              (ParticipateInModel.bet_unit * ParticipateInModel.bet_number).label(
                                  'total_bet'),
                              ParticipateInModel.merge_id, ParticipateInModel.created_at,
                              ParticipateInModel.pay_token, ParticipateInModel.pay_number). \
                filter(ParticipateInModel.user_id == user_id). \
                order_by(ParticipateInModel.created_at.desc())
            record_count = q.count()
            result_dict['count'] = get_page_by_offset(record_count, limit)
            if start_id is not None:
                start_id = str(start_id)
                q = q.filter(ParticipateInModel._id < start_id)
            participate_list = q.limit(limit).offset(offset).all()
            for i in participate_list:
                award_numbers_list = i.award_numbers
                if i.game_instance_id == 0:
                    instance_info = session.query(InstantGameInstanceModel.need, InstantGameInstanceModel.status,
                                                  InstantGameInstanceModel.bet_token,
                                                  InstantGameInstanceModel.participation). \
                        filter(InstantGameInstanceModel.game_serial == i.game_serial).first()
                    if instance_info is None:
                        continue
                    if i.win_number in award_numbers_list:
                        is_win = True
                    else:
                        is_win = False
                else:
                    instance_info = session.query(GameDigitalInstanceModel.need, GameDigitalInstanceModel.status,
                                                  GameDigitalInstanceModel._id,
                                                  GameDigitalInstanceModel.bet_token,
                                                  GameDigitalInstanceModel.participation). \
                        filter(GameDigitalInstanceModel._id == i.game_instance_id).first()
                    if instance_info is None:
                        continue
                    if instance_info.status == 2:
                        winning_record = session.query(WinningRecordModel). \
                            filter(WinningRecordModel.game_instance_id == instance_info._id).first()
                        if winning_record.bet_serial in award_numbers_list:
                            is_win = True
                        else:
                            is_win = False
                    else:
                        is_win = False
                if int(i.pay_token) == int(_COIN_ID_EXP):
                    pay_number = int(i.pay_number)
                else:
                    pay_number = decimal_to_str(i.pay_number, 8)
                result_dict['content'].append({
                    'is_win': is_win,
                    'instance_id': i.game_instance_id,
                    'participate_id': i._id,
                    'game_serial': i.game_serial,
                    'bet_token': self.get_coin_name(i.bet_token),
                    'total_bet': int(i.total_bet),
                    # 'need': instance_info.need,
                    'status': instance_info.status,
                    'need_token': self.get_coin_name(instance_info.bet_token),
                    # 'probability': probability,
                    # 'ranking': math.ceil((lower / total) * 100),
                    'merge_id': i.merge_id,
                    'part_in_time': str(i.created_at),
                    "pay_token": self.get_coin_name(i.pay_token),
                    "pay_number": pay_number
                })

        return result_dict

    def indiana_number(self, participate_id):
        with MysqlTools().session_scope() as session:
            par = session.query(ParticipateInModel). \
                filter(ParticipateInModel._id == participate_id).first()
            pattern = re.compile(r'[\[\]\s]')
            merge_total = 0
            merge_mine = par.bet_number * par.bet_unit
            if par.merge_id == -1:
                award_numbers_list = par.award_numbers
                indiana_numbers = pattern.sub('', award_numbers_list).split(',')
            else:
                indiana_numbers = []
                merge_participate_list = session.query(ParticipateInModel). \
                    filter(ParticipateInModel.merge_id == par.merge_id).all()
                for merge_participate in merge_participate_list:
                    merge_total += merge_participate.bet_number * merge_participate.bet_unit
                    indiana_numbers += pattern.sub('', merge_participate.award_numbers).split(',')
            win_record = session.query(WinningRecordModel). \
                filter(WinningRecordModel.game_serial == par.game_serial).first()
            number_list = []
            win_serial = '-1'
            if win_record is not None:
                win_serial = win_record.bet_serial
            for i in indiana_numbers:
                if i == win_serial:
                    status = True
                else:
                    status = False
                number_list.append({
                    'number': i,
                    'is_win': status
                })
        return {
            'game_serial': par.game_serial,
            'indiana_time': str(par.created_at),
            'indiana_numbers': number_list,
            'win_record': win_serial,
            'merge_mine': merge_mine,
            'merge_total': merge_total,
            'merge_id': par.merge_id,
            'bet_toekn': self.get_coin_name(par.bet_token),
        }

    def indiana_number_new(self, participate_id):
        with MysqlTools().session_scope() as session:
            par = session.query(ParticipateInModel). \
                filter(ParticipateInModel._id == participate_id).first()
            pattern = re.compile(r'[\[\]\s]')
            merge_total = 0
            merge_mine = par.bet_number * par.bet_unit
            award_numbers_list = par.award_numbers
            indiana_numbers = pattern.sub('', award_numbers_list).split(',')
            number_list = []
            win_serial = par.win_number
            for i in indiana_numbers:
                if i == win_serial:
                    status = True
                else:
                    status = False
                number_list.append({
                    'number': i,
                    'is_win': status
                })
        return {
            'game_serial': par.game_serial,
            'indiana_time': str(par.created_at),
            'indiana_numbers': number_list,
            'win_record': win_serial,
            'merge_mine': merge_mine,
            'merge_total': merge_total,
            'merge_id': par.merge_id,
            'bet_toekn': self.get_coin_name(par.bet_token),
        }

    def indiana_detail(self, instance_id, participate_id):
        release_time = '---------------'
        full_load_time = '---------------'
        lottery_time = '---------------'
        with MysqlTools().session_scope() as session:
            instance_info = session.query(GameDigitalInstanceModel). \
                filter(GameDigitalInstanceModel._id == instance_id).first()
            if instance_info is None:
                self.return_error(40005)
            bet_serial = ''
            if instance_info.status == 2:
                release_time = str(instance_info.release_time)
                full_load_time = str(instance_info.full_load_time)
                lottery_time = str(instance_info.lottery_time)
                # 中奖号
                winning_info = session.query(WinningRecordModel). \
                    filter(WinningRecordModel.game_instance_id == instance_id).first()
                bet_serial = winning_info.bet_serial
            elif instance_info.status == 0:
                release_time = str(instance_info.release_time)
            elif instance_info.status == 1:
                release_time = str(instance_info.release_time)
                full_load_time = str(instance_info.full_load_time)
            part_info = session.query(ParticipateInModel). \
                filter(ParticipateInModel._id == participate_id).first()
            if part_info is None:
                self.return_error(40016)
            if int(part_info.pay_token) == int(_COIN_ID_EXP):
                pay_number = str(int(part_info.pay_number))
            else:
                pay_number = decimal_to_str(part_info.pay_number, 8)
        return {
            'game_serial': instance_info.game_serial,
            'status': instance_info.status,
            'need': instance_info.need,
            'bet_token': instance_info.bet_token,
            'bet_unit': instance_info.bet_unit,
            'reward_token': instance_info.reward_token,
            'reward_quantity': instance_info.reward_quantity,
            'release_time': release_time,
            'full_load_time': full_load_time,
            'lottery_time': lottery_time,
            'bet_serial': bet_serial,
            'participation': instance_info.participation,
            'part_in_time': str(part_info.created_at),
            'bet_number': part_info.bet_number,
            'merge_id': part_info.merge_id,
            'pay_token': part_info.pay_token,
            'pay_number': pay_number
        }

    def app_version_check(self, version_code):
        with MysqlTools().session_scope() as session:
            version_info = session.query(AppUpgradeModel). \
                filter(AppUpgradeModel.status == 1). \
                order_by(AppUpgradeModel._id.desc()).first()
            if version_info is None:
                self.return_error(40020)
            # 有更新版本
            if version_info.version_code > int(version_code):
                return {
                    'new_version': True,
                    'version_info': {
                        'version_name': version_info.version_name,
                        'upgrade_describe': version_info.upgrade_describe,
                        'download_link': version_info.download_link,
                        'forced_update': version_info.forced_update,
                        'status': version_info.status
                    }
                }
            else:
                return {
                    'new_version': False
                }

