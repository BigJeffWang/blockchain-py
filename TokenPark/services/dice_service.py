import datetime
import decimal
import math

from models.dice_config_model import DiceConfigModel
from models.dice_participate_in_model import DiceParticipateInModel
from models.sync_eos_model import SyncEosModel
from models.token_node_conf_model import TokenNodeConfModel
from scripts.token_sync_lottery_script import TokenSyncLotteryScript
from services.account_service import AccountService
from services.base_service import BaseService
from tools.mysql_tool import MysqlTools
from common_settings import *
from sqlalchemy import func, distinct, or_

from utils.generate_phase_util import dice_generate_phase
from utils.log import raise_logger
from utils.time_util import get_utc_now, get_timestamp, timestamp_to_str, str_to_timestamp
from utils.util import get_offset_by_page, get_page_by_offset, get_decimal, decimal_to_str


class DiceService(BaseService):
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

    def dice_records(self, limit, offset, user_id='', start_id=None):
        offset = get_offset_by_page(offset, limit)
        result_dict = {
            'limit': limit,
            'offset': offset,
            'count': 0,
            'content': []
        }
        account_service = AccountService()
        with MysqlTools().session_scope() as session:
            q = session.query(DiceParticipateInModel). \
                order_by(DiceParticipateInModel.created_at.desc())
            if user_id != '':
                q = q.filter(DiceParticipateInModel.user_id == user_id)
            record_count = q.count()
            result_dict['count'] = get_page_by_offset(record_count, limit)
            if start_id is not None:
                start_id = str(start_id)
                q = q.filter(DiceParticipateInModel._id < start_id)
            participate_list = q.limit(limit).offset(offset).all()
            for i in participate_list:
                user_info = account_service.get_inner_user_account_info(session, i.user_id)
                user_name = user_info['nick_name']
                result = {
                    'id': i._id,
                    'user_name': user_name,
                    'dice_result': i.dice_result,
                    'dice_time': timestamp_to_str(int(float(i.dice_timestamp)), format_style="%Y-%m-%d %H:%M:%S"),
                    'reward_token': self.get_coin_name(i.reward_token),
                    'reward_quantity': decimal_to_str(i.reward_quantity, 6)
                }
                if i.reward_token == int(_COIN_ID_USDT):
                    result['reward_quantity'] = decimal_to_str(i.reward_quantity, 4)
                result_dict['content'].append(result)

        return result_dict

    def dice_records_get(self, limit, offset, start_id=None):
        offset = get_offset_by_page(offset, limit)
        result_dict = {
            'limit': limit,
            'offset': offset,
            'count': 0,
            'content': []
        }
        account_service = AccountService()
        with MysqlTools().session_scope() as session:
            q = session.query(DiceParticipateInModel). \
                order_by(DiceParticipateInModel.created_at.desc())
            record_count = q.count()
            result_dict['count'] = get_page_by_offset(record_count, limit)
            if start_id is not None:
                start_id = str(start_id)
                q = q.filter(DiceParticipateInModel._id < start_id)
            participate_list = q.limit(limit).offset(offset).all()
            for i in participate_list:
                user_info = account_service.get_inner_user_account_info(session, i.user_id)
                user_name = user_info['nick_name']
                response = {
                    'id': i._id,
                    'user_name': user_name,
                    'dice_result': i.dice_result,
                    'dice_time': timestamp_to_str(int(float(i.dice_timestamp)), format_style="%Y-%m-%d %H:%M:%S"),
                    'reward_token': self.get_coin_name(i.reward_token),
                    'reward_quantity': decimal_to_str(i.reward_quantity, 6)
                }
                if i.reward_token == int(_COIN_ID_USDT):
                    response['reward_quantity'] = decimal_to_str(i.reward_quantity, 4)

                result_dict['content'].append(response)

        return result_dict

    def dice_info(self, dice_part_id):
        with MysqlTools().session_scope() as session:
            dice_info = session.query(DiceParticipateInModel). \
                filter(DiceParticipateInModel._id == dice_part_id).first()
            if dice_info is None:
                self.return_error(40021)
            if dice_info.block_timestamp != '0000-00-00T00:00:00.000':
                block_timestamp = timestamp_to_str(
                    str_to_timestamp(dice_info.block_timestamp, format_style="%Y-%m-%dT%H:%M:%S.%f"),
                    format_style="%Y-%m-%d %H:%M:%S")
            else:
                block_timestamp = ''
        return {
            'dice_serial': dice_info.dice_serial,
            'dice_time': timestamp_to_str(int(float(dice_info.dice_timestamp)), format_style="%Y-%m-%d %H:%M:%S"),
            'reward_token': self.get_coin_name(dice_info.reward_token),
            'reward_quantity': str(dice_info.reward_quantity),
            'bet_number': str(dice_info.bet_number),
            'bet_token': self.get_coin_name(dice_info.bet_token),
            'user_dice': dice_info.user_dice,
            'banker_dice': dice_info.banker_dice,
            'dice_result': dice_info.dice_result,
            # 'calc': int(dice_info.block_hash, 16) / 3,
            'eos_block_info': {
                'block_no': dice_info.block_no,
                'block_hash': dice_info.block_hash,
                'block_timestamp': block_timestamp
            }
        }

    def dice_chip_in(self, user_id, user_channel_id, coin_id, bet_amount, user_dice):
        with MysqlTools().session_scope() as session:
            # 查询用户资产
            account_service = AccountService()
            user_info = account_service.get_inner_user_account_by_token(session, user_id, coin_id)
            if isinstance(user_info, int):
                if user_info == 20001:
                    return self.return_error(20001)

            balance = get_decimal(user_info.get("balance"), digits=8, decimal_type="down")
            # 账户余额 < 需要下注金额
            bet_number = get_decimal(bet_amount, digits=4, decimal_type="down")
            if balance < bet_number:
                return self.return_error(60005)
            dice_serial = dice_generate_phase()
            block_no = ''
            # 获取最新eos区块，计算开奖区块高度
            dice_time = get_timestamp()
            latest_eos_block_info = session.query(SyncEosModel). \
                order_by(SyncEosModel._id.desc()).first()
            latest_eos_block_no = latest_eos_block_info.block_num
            latest_eos_block_time = latest_eos_block_info.time_stamp_decimal
            block_delay = math.ceil((dice_time - latest_eos_block_time) / decimal.Decimal(0.5))
            block_no = latest_eos_block_no + block_delay + 1
            # raise_logger("最新区块高度=" + str(latest_eos_block_no) + "时间:" + get_utc_now().strftime(
            #     "%Y-%m-%d %H:%M:%S.%f"), "game_bet_in", "info")
            # raise_logger("最新区块时间=" + str(latest_eos_block_time) + "时间:" + get_utc_now().strftime(
            #     "%Y-%m-%d %H:%M:%S.%f"), "game_bet_in", "info")
            # raise_logger("时间延迟=" + str(block_delay) + "时间:" + get_utc_now().strftime(
            #     "%Y-%m-%d %H:%M:%S.%f"), "game_bet_in", "info")
            dice_part_in_model = DiceParticipateInModel(
                dice_serial=dice_serial,
                user_id=user_id,
                user_dice=user_dice,
                channel=user_channel_id,
                bet_number=bet_number,
                bet_token=coin_id,
                reward_token=coin_id,
                reward_quantity=bet_number,
                dice_timestamp=dice_time,
                block_no=block_no
            )
            session.add(dice_part_in_model)
            session.flush()
            # raise_logger("添加dice参与记录成功, id= " + str(dice_part_in_model._id) + "时间:" + get_utc_now().strftime(
            #     "%Y-%m-%d %H:%M:%S.%f"), "game_bet_in", "info")
            # 提交扣款申请
            dice_part_id = dice_part_in_model._id
            result = account_service.do_bet(session,
                                            user_id,
                                            coin_id,
                                            bet_number,
                                            'dice_bet' + str(dice_part_in_model._id),
                                            1,
                                            dice_serial,
                                            user_channel_id)
            if result != 0:
                session.rollback()
                raise_logger("do_bet result" + str(result), "game_bet_in", "info")
            # raise_logger("提交扣款申请成功 " + "时间:" + get_utc_now().strftime(
            #     "%Y-%m-%d %H:%M:%S.%f"), "game_bet_in", "info")
            session.commit()
        return {
            # 'result': True,
            'dice_timestamp': timestamp_to_str(dice_time, format_style="%Y-%m-%d %H:%M:%S"),
            'dice_id': dice_part_id,
            'dice_serial': dice_serial
        }

    def check_dice_sold_out_by_eos(self):
        # raise_logger("sold_out开始" + " 时间:" + get_utc_now().strftime(
        #     "%Y-%m-%d %H:%M:%S.%f"), "game_bet_in", "info")
        with MysqlTools().session_scope() as session:
            account_service = AccountService()
            not_lottery_list = session.query(DiceParticipateInModel). \
                filter(DiceParticipateInModel.dice_result == -1).all()
            if len(not_lottery_list) > 0:
                for not_lottery in not_lottery_list:
                    # raise_logger("需开奖记录id=" + str(not_lottery._id) + " 时间:" + get_utc_now().strftime(
                    #     "%Y-%m-%d %H:%M:%S.%f"), "game_bet_in", "info")
                    lottery_block = not_lottery.block_no
                    lottery_eos_block_info = session.query(SyncEosModel). \
                        filter(SyncEosModel.block_num == lottery_block).first()
                    if lottery_eos_block_info is not None:
                        # raise_logger("找到开奖区块lottery_block" + str(
                        #     lottery_eos_block_info.block_hash) + " 时间:" + get_utc_now().strftime(
                        #     "%Y-%m-%d %H:%M:%S.%f"), "game_bet_in", "info")
                        not_lottery.block_timestamp = lottery_eos_block_info.time_stamp
                        not_lottery.block_hash = lottery_eos_block_info.block_hash
                        dice_result = -1
                        banker_dice = int(not_lottery.block_hash, 16) % 3  # 0石头 1剪刀 2布
                        user_dice = not_lottery.user_dice  # 0石头 1剪刀 2布
                        if banker_dice == user_dice:
                            dice_result = 1  # 0用户胜 1平局 2庄家胜 -1未知
                        else:
                            if banker_dice == 0 and user_dice == 1:
                                dice_result = 2
                            elif banker_dice == 0 and user_dice == 2:
                                dice_result = 0
                            elif banker_dice == 1 and user_dice == 0:
                                dice_result = 0
                            elif banker_dice == 1 and user_dice == 2:
                                dice_result = 2
                            elif banker_dice == 2 and user_dice == 0:
                                dice_result = 2
                            elif banker_dice == 2 and user_dice == 1:
                                dice_result = 0
                        not_lottery.banker_dice = banker_dice
                        not_lottery.dice_result = dice_result
                        session.flush()
                        if dice_result in [0, 1]:
                            reward_quantity = 0
                            dice_config = session.query(DiceConfigModel). \
                                filter(DiceConfigModel.support_token_id == not_lottery.bet_token).first()
                            if dice_config is None:
                                return self.return_error(40022)
                            if dice_result == 0:
                                # 用户获胜 中奖金额为投注金额+奖励金额(投注金额=奖励金额) 扣除手续费
                                reward_quantity = (not_lottery.reward_quantity + not_lottery.bet_number) * (
                                        100 - dice_config.handling_fee) / 100
                            elif dice_result == 1:
                                # 平局 中奖金额为投注金额
                                reward_quantity = not_lottery.bet_number
                            result = account_service.do_win(session,
                                                            not_lottery.user_id,
                                                            not_lottery.reward_token,
                                                            reward_quantity,
                                                            'dice_win' + str(not_lottery._id),
                                                            not_lottery.user_dice,
                                                            not_lottery.dice_serial)
                            if isinstance(result, int) is False:
                                raise_logger("dice分钱失败" + "user:" + str(not_lottery.user_id), "game_publish_lottery",
                                             "info")
                                session.rollback()
                                return False
                            if result != 0:
                                raise_logger("dice分钱失败" + "user:" + str(not_lottery.user_id), "game_publish_lottery",
                                             "info")
                                session.rollback()
                                return False
                session.commit()
            # raise_logger("sold_out结束" + " 时间:" + get_utc_now().strftime(
            #     "%Y-%m-%d %H:%M:%S.%f"), "game_bet_in", "info")
        return {
            'result': True
        }

    def get_dice_award_rate(self, user_id):
        with MysqlTools().session_scope() as session:
            account_service = AccountService()
            award_rate_info = session.query(DiceParticipateInModel.user_dice,
                                            func.count(DiceParticipateInModel._id).label('total_award')). \
                filter(DiceParticipateInModel.dice_result == 0). \
                group_by(DiceParticipateInModel.user_dice).all()
            stone = 0
            scissors = 0
            cloth = 0
            # balance_btc = ''
            # balance_eth = ''
            # balance_usdt = ''
            # balance_eos = ''
            # balance_exp = ''
            # print(award_rate_info)
            account_balance = account_service.get_user_token_list(user_id, None, 1, 10)['content'][0]
            balance_btc = account_balance['BTC']
            balance_eth = account_balance['ETH']
            if account_balance.get('EOS', None) is not None:
                balance_eos = account_balance['EOS']
            else:
                balance_eos = 0
            balance_usdt = account_balance['USDT']
            balance_exp = account_balance['USDT_EXPERIENCE']
            if len(award_rate_info) > 0:
                award_total = 0
                for award_rate in award_rate_info:
                    award_total += award_rate[1]
                    if award_rate[0] == 0:
                        stone = award_rate[1]
                    elif award_rate[0] == 1:
                        scissors = award_rate[1]
                    elif award_rate[0] == 2:
                        cloth = award_rate[1]
                stone_rate = stone / award_total * 100
                scissors_rate = scissors / award_total * 100
                cloth_rate = cloth / award_total * 100
                result = {
                    'stone': decimal_to_str(stone_rate, 2),
                    'scissors': decimal_to_str(scissors_rate, 2),
                    'cloth': decimal_to_str(cloth_rate, 2),
                    'balance': {
                        'btc': decimal_to_str(balance_btc, 8),
                        'eth': decimal_to_str(balance_eth, 8),
                        'eos': decimal_to_str(balance_eos, 8),
                        'usdt': decimal_to_str(balance_usdt, 4),
                        'exp': decimal_to_str(balance_exp, 4)
                    }
                }
                # print(result)
                return result
            else:
                return {
                    'stone': '',
                    'scissors': '',
                    'cloth': '',
                    'balance': {
                        'btc': decimal_to_str(balance_btc, 8),
                        'eth': decimal_to_str(balance_eth, 8),
                        'eos': decimal_to_str(balance_eos, 8),
                        'usdt': decimal_to_str(balance_usdt, 4),
                        'exp': decimal_to_str(balance_exp, 4)
                    }
                }

    def dice_chip_in_fast(self, user_id, user_channel_id, coin_id, bet_amount, user_dice):
        change_type_31 = '31'  # 扣款
        change_type_32 = '32'  # 返还
        change_type_33 = '33'  # 中奖
        with MysqlTools().session_scope() as session:
            # 查询用户资产
            account_service = AccountService()
            user_info = account_service.get_inner_user_account_by_token(session, user_id, coin_id)
            if isinstance(user_info, int):
                if user_info == 20001:
                    return self.return_error(20001)

            balance = get_decimal(user_info.get("balance"), digits=8, decimal_type="down")
            # 账户余额 < 需要下注金额
            bet_number = get_decimal(bet_amount, digits=4, decimal_type="down")
            if balance < bet_number:
                return self.return_error(60005)
            dice_serial = dice_generate_phase()
            # 获取最新eos区块，计算开奖区块高度
            dice_time = get_timestamp()
            ec = TokenNodeConfModel.get_eos_node_script(script_unit=_THREE_S)
            latest_eos_block_info = ec.http_get_latest_block()
            # print('latest_eos_block_info=-=-=', latest_eos_block_info)
            block_no = latest_eos_block_info['block_num']

            dice_part_in_model = DiceParticipateInModel(
                dice_serial=dice_serial,
                user_id=user_id,
                user_dice=user_dice,
                channel=user_channel_id,
                bet_number=bet_number,
                bet_token=coin_id,
                reward_token=coin_id,
                reward_quantity=bet_number,
                dice_timestamp=dice_time,
                block_no=block_no
            )
            session.add(dice_part_in_model)
            session.flush()
            # 提交扣款申请
            dice_part_id = dice_part_in_model._id
            result = account_service.do_bet(session,
                                            user_id,
                                            coin_id,
                                            bet_number,
                                            'dice_bet' + str(dice_part_in_model._id),
                                            1,
                                            dice_serial,
                                            user_channel_id,
                                            change_type_31)
            if result != 0:
                session.rollback()
                raise_logger("do_bet result" + str(result), "game_bet_in", "info")

            # -------------------------------- 开奖 -------------------------------- #
            block_timestamp = latest_eos_block_info['timestamp']
            block_hash = latest_eos_block_info['id']
            dice_result = -1
            banker_dice = int(block_hash, 16) % 3  # 0石头 1剪刀 2布
            user_dice = int(user_dice)
            if banker_dice == user_dice:
                dice_result = 1  # 0用户胜 1平局 2庄家胜 -1未知
            else:
                if banker_dice == 0 and user_dice == 1:
                    dice_result = 2
                elif banker_dice == 0 and user_dice == 2:
                    dice_result = 0
                elif banker_dice == 1 and user_dice == 0:
                    dice_result = 0
                elif banker_dice == 1 and user_dice == 2:
                    dice_result = 2
                elif banker_dice == 2 and user_dice == 0:
                    dice_result = 2
                elif banker_dice == 2 and user_dice == 1:
                    dice_result = 0
            dice_part_in_model.banker_dice = banker_dice
            dice_part_in_model.dice_result = dice_result
            dice_part_in_model.block_hash = block_hash
            dice_part_in_model.block_timestamp = block_timestamp
            # session.flush()
            change_type = change_type_32

            # ------------ 中奖控制 ------------ #
            winning_control = 0
            if dice_result in [0, 1]:
                win_dice_num = session.query(func.count(DiceParticipateInModel._id)). \
                    filter(DiceParticipateInModel.user_id == user_id,
                           DiceParticipateInModel.dice_result == 0,
                           func.date_format(DiceParticipateInModel.created_at, "%Y-%m-%d") ==
                           func.date_format(get_utc_now(), "%Y-%m-%d")).first()
                if win_dice_num[0] >= decimal.Decimal(500):
                    raise_logger("dice winning control userid = " + str(user_id), "game_bet_in", "info")
                    dice_part_in_model.banker_dice = user_dice
                    dice_part_in_model.dice_result = 1
                    dice_result = 1
                    winning_control = 1
            # ------------ 中奖控制结束 ------------ #

            if dice_result in [0, 1]:
                reward_quantity = 0
                dice_config = session.query(DiceConfigModel). \
                    filter(DiceConfigModel.support_token_id == dice_part_in_model.bet_token).first()
                if dice_config is None:
                    return self.return_error(40022)
                if dice_result == 0:
                    change_type = change_type_33
                    # 用户获胜 中奖金额为投注金额+奖励金额(投注金额=奖励金额) 扣除手续费
                    reward_quantity = (dice_part_in_model.reward_quantity + dice_part_in_model.bet_number) * (
                            100 - dice_config.handling_fee) / 100
                elif dice_result == 1:
                    change_type = change_type_32
                    # 平局 中奖金额为投注金额
                    reward_quantity = dice_part_in_model.bet_number
                result = account_service.do_win(session,
                                                dice_part_in_model.user_id,
                                                dice_part_in_model.reward_token,
                                                reward_quantity,
                                                'dice_win' + str(dice_part_in_model._id),
                                                dice_part_in_model.user_dice,
                                                dice_part_in_model.dice_serial,
                                                change_type)
                if isinstance(result, int) is False:
                    raise_logger("dice分钱失败" + "user:" + str(dice_part_in_model.user_id), "game_publish_lottery",
                                 "info")
                    session.rollback()
                    return False
                if result != 0:
                    raise_logger("dice分钱失败" + "user:" + str(dice_part_in_model.user_id), "game_publish_lottery",
                                 "info")
                    session.rollback()
                    return False
            # -------------------------------- 开奖结束 -------------------------------- #

            session.commit()
            if winning_control == 1:
                return self.return_error(40023)
        return {
            'dice_result': dice_result,
            'banker_dice': banker_dice,
            'user_dice': user_dice,
            'dice_timestamp': timestamp_to_str(dice_time, format_style="%Y-%m-%d %H:%M:%S"),
            'dice_id': str(dice_part_id),
            'dice_serial': dice_serial,
            'reward_token': self.get_coin_name(coin_id),
            'reward_quantity': decimal_to_str(str((bet_number + bet_number) * decimal.Decimal(0.99)), 6)
        }

    def dice_chip_in_new(self, user_id, user_channel_id, coin_id, bet_amount, user_dice):
        change_type_31 = '31'  # 扣款
        change_type_32 = '32'  # 返还
        change_type_33 = '33'  # 中奖
        with MysqlTools().session_scope() as session:
            # 查询用户资产
            account_service = AccountService()
            user_info = account_service.get_inner_user_account_by_token(session, user_id, coin_id)
            if isinstance(user_info, int):
                if user_info == 20001:
                    return self.return_error(20001)

            balance = get_decimal(user_info.get("balance"), digits=8, decimal_type="down")
            # 账户余额 < 需要下注金额
            bet_number = get_decimal(bet_amount, digits=4, decimal_type="down")
            if balance < bet_number:
                return self.return_error(60005)
            dice_serial = dice_generate_phase()
            dice_time = get_timestamp()
            dice_part_in_model = DiceParticipateInModel(
                dice_serial=dice_serial,
                user_id=user_id,
                user_dice=user_dice,
                channel=user_channel_id,
                bet_number=bet_number,
                bet_token=coin_id,
                reward_token=coin_id,
                reward_quantity=bet_number,
                dice_timestamp=dice_time
            )
            session.add(dice_part_in_model)
            session.flush()
            # 提交扣款申请
            dice_part_id = dice_part_in_model._id
            result = account_service.do_bet(session,
                                            user_id,
                                            coin_id,
                                            bet_number,
                                            'dice_bet' + str(dice_part_in_model._id),
                                            1,
                                            dice_serial,
                                            user_channel_id,
                                            change_type_31)
            if result != 0:
                session.rollback()
                raise_logger("do_bet result" + str(result), "game_bet_in", "info")
            session.commit()
        return {
            'user_dice': user_dice,
            'dice_timestamp': timestamp_to_str(dice_time, format_style="%Y-%m-%d %H:%M:%S"),
            'dice_id': str(dice_part_id),
            'dice_serial': dice_serial
        }

    def dice_sold_out_new(self, dice_id):
        change_type_31 = '31'  # 扣款
        change_type_32 = '32'  # 返还
        change_type_33 = '33'  # 中奖
        reward_quantity = decimal.Decimal(0)
        with MysqlTools().session_scope() as session:
            account_service = AccountService()
            dice_info = session.query(DiceParticipateInModel). \
                filter(DiceParticipateInModel._id == dice_id).first()
            if dice_info is None:
                self.return_error(40021)
            ec = TokenNodeConfModel.get_eos_node_script(script_unit=_THREE_S)
            latest_eos_block_info = ec.http_get_latest_block()
            # print('latest_eos_block_info=-=-=', latest_eos_block_info)
            dice_info.block_no = latest_eos_block_info.get('block_num', None)
            dice_info.block_timestamp = latest_eos_block_info.get('timestamp', None)
            dice_info.block_hash = latest_eos_block_info.get('id', None)
            if dice_info.block_no is None or \
                    dice_info.block_timestamp is None or \
                    dice_info.block_hash is None:
                self.return_error(40024)
            else:
                dice_result = -1
                banker_dice = int(dice_info.block_hash, 16) % 3  # 0石头 1剪刀 2布
                user_dice = dice_info.user_dice  # 0石头 1剪刀 2布
                if banker_dice == user_dice:
                    dice_result = 1  # 0用户胜 1平局 2庄家胜 -1未知
                else:
                    if banker_dice == 0 and user_dice == 1:
                        dice_result = 2
                    elif banker_dice == 0 and user_dice == 2:
                        dice_result = 0
                    elif banker_dice == 1 and user_dice == 0:
                        dice_result = 0
                    elif banker_dice == 1 and user_dice == 2:
                        dice_result = 2
                    elif banker_dice == 2 and user_dice == 0:
                        dice_result = 2
                    elif banker_dice == 2 and user_dice == 1:
                        dice_result = 0
                dice_info.banker_dice = banker_dice
                dice_info.dice_result = dice_result
                # session.flush()
                if dice_result in [0, 1]:
                    change_type = change_type_32
                    dice_config = session.query(DiceConfigModel). \
                        filter(DiceConfigModel.support_token_id == dice_info.bet_token).first()
                    if dice_config is None:
                        return self.return_error(40022)
                    if dice_result == 0:
                        change_type = change_type_33
                        # 用户获胜 中奖金额为投注金额+奖励金额(投注金额=奖励金额) 扣除手续费
                        reward_quantity = (dice_info.reward_quantity + dice_info.bet_number) * (
                                100 - dice_config.handling_fee) / 100
                        dice_info.reward_quantity = reward_quantity
                    elif dice_result == 1:
                        change_type = change_type_32
                        # 平局 中奖金额为投注金额
                        reward_quantity = dice_info.bet_number
                    result = account_service.do_win(session,
                                                    dice_info.user_id,
                                                    dice_info.reward_token,
                                                    reward_quantity,
                                                    'dice_win' + str(dice_info._id),
                                                    dice_info.user_dice,
                                                    dice_info.dice_serial,
                                                    change_type)
                    if isinstance(result, int) is False:
                        raise_logger("dice分钱失败" + "user:" + str(dice_info.user_id), "game_publish_lottery",
                                     "info")
                        session.rollback()
                        return False
                    if result != 0:
                        raise_logger("dice分钱失败" + "user:" + str(dice_info.user_id), "game_publish_lottery",
                                     "info")
                        session.rollback()
                        return False
            # ret_info = dice_info
            # print(ret_info)
            session.commit()
            session.refresh(dice_info)
            # session.expunge(dice_info)
        response = {
            'dice_result': dice_info.dice_result,
            'banker_dice': dice_info.banker_dice,
            'user_dice': dice_info.user_dice,
            # 'dice_timestamp': timestamp_to_str(dice_info.dice_timestamp, format_style="%Y-%m-%d %H:%M:%S"),
            'dice_id': str(dice_info._id),
            'dice_serial': dice_info.dice_serial,
            'reward_token': self.get_coin_name(dice_info.reward_token),
            'reward_quantity': decimal_to_str(reward_quantity, 6)
            # 'reward_quantity': decimal_to_str(
            #     str((dice_info.bet_number + dice_info.bet_number) * decimal.Decimal(0.99)), 6)
        }

        if dice_info.reward_token == int(_COIN_ID_USDT):
            response['reward_quantity'] = decimal_to_str(reward_quantity, 4)
        return response


if __name__ == '__main__':
    pass
    # DiceService().dice_chip_in('097b28eacbdc49a68657ca4c567a5676', 0, 0, 1, 1)
    # DiceService().get_dice_award_rate()
