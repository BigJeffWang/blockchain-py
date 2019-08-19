import datetime
import json
import re

from models.instant_game_instance_model import InstantGameInstanceModel
from models.instant_game_template_model import InstantGameTemplateModel
from models.instant_participate_in_model import InstantParticipateInModel
from models.participate_in_model import ParticipateInModel
from services.account_service import AccountService
from services.base_service import BaseService
from common_settings import *
from services.instant_game_model_service import InstantGameModelService
from services.wallet_eos_service import WalletEosService
from tools.mysql_tool import MysqlTools
from utils.exchange_rate_util import get_exchange_rate
from utils.log import raise_logger
from utils.time_util import get_timestamp, get_utc_now, timestamp_to_str, str_to_timestamp
from utils.util import decimal_to_str, get_decimal, get_offset_by_page, get_page_by_offset
from sqlalchemy import func


class InstantGameService(BaseService):
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

    def bet_in(self, dic):
        change_type_41 = '41'  # 即时开中奖
        change_type_42 = '42'  # 即时开投注
        id = dic.get("game_instance_id", "")  # 项目id
        user_id = dic.get("user_id", "")  # 用户id
        user_channel_id = dic.get("user_channel_id", "")  # 用户下注渠道id
        conin_id = dic.get("coin_id", "")  # 投入币种id
        bet_amount = dic.get("bet_amount", "")  # 投注数量
        bet_start = dic.get("bet_start", 0)
        bet_end = dic.get("bet_end", 0)
        faker = True
        # merge_id = dic.get("merge_id", -1)  # 合并投注id
        # transaction_password = dic.get("transaction_password", "")  # 交易密码
        with MysqlTools().session_scope() as session:
            # 查询项目
            model = session.query(InstantGameInstanceModel).filter(
                InstantGameInstanceModel._id == id).first()
            template = session.query(InstantGameTemplateModel). \
                order_by(InstantGameTemplateModel._id.desc()).first()
            if model is None:
                return self.return_error(60001)
            if model.status == 1:
                return self.return_error(60002)
            if model.status == 2:
                return self.return_error(60003)
            if model.status == 0:
                can_bet = model.need - model.bet_number
                if can_bet <= 0:
                    return self.return_error(60002)
                if int(bet_amount) > can_bet:
                    return self.return_error(60004)

            if model.support_token >= 0 and int(conin_id) != model.support_token and int(conin_id) != int(_COIN_ID_EXP):
                return self.return_error(60008)

            if int(bet_amount) > model.need * (model.max_bet_ratio / 100):
                return self.return_error(40025)

            # 查询币价 币种实际需要金额
            exchange_rate = get_exchange_rate(int(conin_id))

            # (投注数量 * 投注单位) / 投注币种兑换usdt比例
            bet_money = (int(bet_amount) * model.bet_unit) / exchange_rate['price']

            # 体验金相关逻辑
            if int(conin_id) == int(_COIN_ID_EXP):
                # 检查本次投注体验金使用数量 (允许范围: 1~10)
                if int(bet_amount) < 1 or int(bet_amount) > 10:
                    self.return_error(60015)
                # 体验金使用额度
                exp = int(model.experience / 100 * model.need)
                # 检查项目体验金占比剩余额度以及个人当天最大体验金使用额度(每天最多用10个)
                limit = self.check_instance_exp_limit(session, user_id, model.game_serial)
                # instance_limit = limit['instance_limit']
                user_limit = limit['user_limit']
                total_pay_number = limit['total_pay_number']
                if user_limit > 10 - int(bet_amount):
                    self.return_error(60017)
                # if instance_limit >= exp:
                #     self.return_error(60016)
                if total_pay_number >= int(model.need) * model.reward_quantity * ((100 + template.exceeded_ratio) / 100):
                    model.full_load_time = datetime.datetime.utcnow()
                    faker = False
            else:
                limit = self.check_instance_exp_limit(session, user_id, model.game_serial)
                total_pay_number = limit['total_pay_number']
                raise_logger("总下注金额" + "USDT:" + str(total_pay_number), "game_publish_lottery", "info")
                if total_pay_number >= int(model.need) * model.reward_quantity * ((100 + template.exceeded_ratio) / 100):
                    model.full_load_time = datetime.datetime.utcnow()
                    faker = False

            # 查询用户资产
            account_service = AccountService()
            user_info = account_service.get_inner_user_account_by_token(session, user_id, conin_id)
            if isinstance(user_info, int):
                if user_info == 20001:
                    return self.return_error(20001)

            balance = get_decimal(user_info.get("balance"), digits=8, decimal_type="down")

            # 账户余额 < 需要下注金额
            if balance < bet_money:
                return self.return_error(60005)

            # 获取下注编号
            numbers = []
            user_lottery_num_list = []
            i = int(bet_amount)
            # start_num = random.randint(1, model.need 0- int(bet_amount))
            bet_start = int(bet_start)
            bet_end = int(bet_end)
            user_lottery_num_list.append(bet_start)
            user_lottery_num_list.append(bet_end)
            while i > 0:
                numbers.append(bet_start)
                bet_start += 1
                i -= 1
            if isinstance(numbers, list):
                nick_name = account_service.get_inner_user_account_info(session, user_id).get("nick_name")
                # 添加参与记录
                participate_in_model = ParticipateInModel(
                    game_instance_id=0,
                    template_id=model.template_id,
                    game_serial=model.game_serial,
                    game_title=model.game_title,
                    release_type=model.release_type,
                    bet_token=model.bet_token,
                    bet_unit=model.bet_unit,
                    user_id=user_id,
                    nick_name=nick_name,
                    channel=user_channel_id,
                    bet_number=int(bet_amount),
                    pay_token=int(conin_id),
                    pay_number=get_decimal(bet_money, digits=8, decimal_type="down"),
                    award_numbers=json.dumps(numbers),
                    user_type=0,
                    merge_id=-1
                )
                session.add(participate_in_model)
                session.flush()
                # raise_logger("add participate_in_model", "game_bet_in", "info")
                # 提交扣款申请
                result = account_service.do_bet(session,
                                                user_id,
                                                conin_id,
                                                get_decimal(bet_money, digits=8, decimal_type="down"),
                                                str(participate_in_model._id),
                                                int(bet_amount),
                                                model.game_serial,
                                                user_channel_id,
                                                change_type_42)
                # raise_logger("do_bet success", "game_bet_in", "info")
                if isinstance(result, int):
                    if result == 0:
                        instant_game_service = InstantGameModelService()
                        # print('user_lottery_num_list-=-=', user_lottery_num_list)
                        # print('model.need-=-=', model.need)
                        # print('faker-=-=', faker)
                        lottery_result = WalletEosService().\
                            lottery_instant_adduce(get_timestamp(), user_lottery_num_list, model.need, faker)
                        # print('lottery_result-=-=', lottery_result)
                        if not any(lottery_result):
                            raise_logger("lottery_result empty", "game_bet_in", "info")
                            session.rollback()
                            return self.return_error(40026)
                        # 开奖
                        hash_numbers = lottery_result['block_hash']
                        raise_logger("项目:" + str(id) + "   中奖区块号:" + str(hash_numbers), "game_publish_lottery",
                                     "info")
                        if hash_numbers == "":
                            raise_logger("开奖异常:80001", "game_publish_lottery", "info")
                            return False
                        # prize_number = int(hash_numbers, 16) % model.need + 1
                        prize_number = lottery_result['lottery_num']
                        raise_logger("项目:" + str(id) + "    中奖号码:" + str(prize_number), "game_publish_lottery",
                                     "info")
                        participate_in_model.win_number = prize_number
                        participate_in_model.block_no = lottery_result['block_num']
                        participate_in_model.bet_hash = hash_numbers
                        participate_in_model.received_time = lottery_result['timestamp']
                        # 中奖
                        is_win = False
                        if prize_number in numbers:
                            is_win = True
                            participate_in_model.result = 1
                            model.lottery_time = datetime.datetime.utcnow()
                            instant_game_service.automatic_release(session, model.template_id)
                            do_win = account_service.do_win(session,
                                                            user_id,
                                                            model.reward_token,
                                                            model.reward_quantity,
                                                            str(participate_in_model._id),
                                                            int(bet_amount),
                                                            model.game_serial,
                                                            change_type_41)
                            if isinstance(do_win, int) is False:
                                raise_logger("分钱失败" + "user:" + str(user_id), "game_publish_lottery", "info")
                                session.rollback()
                                return False
                            if do_win != 0:
                                raise_logger("分钱失败" + "user:" + str(user_id), "game_publish_lottery", "info")
                                session.rollback()
                                return False

                        session.commit()

                        return {
                            'is_win': is_win,
                            'prize_number': prize_number,
                            'part_in_id': participate_in_model._id
                        }
                    else:
                        session.rollback()
                        return self.return_error(60009)
                else:
                    session.rollback()
                    return self.return_error(60010)
            else:
                session.rollback()
                return self.return_error(60007)

    def get_game_instance_none_user(self):
        with MysqlTools().session_scope() as session:
            instance_info = session.query(InstantGameInstanceModel). \
                order_by(InstantGameInstanceModel.created_at.desc()).first()
            if instance_info is None:
                self.return_error(40005)
            result = {
                'ins_instance': {
                    'id': instance_info._id,
                    'game_serial': instance_info.game_serial,
                    'game_title': instance_info.game_title,
                    'game_describe': instance_info.game_describe,
                    'need': instance_info.need,
                    'max_bet_ratio': instance_info.max_bet_ratio,
                    'status': instance_info.status,
                    'bet_token': self.get_coin_name(instance_info.bet_token),
                }
            }
            return result

    def get_game_instance(self, user_id=''):
        with MysqlTools().session_scope() as session:
            account_service = AccountService()
            instance_info = session.query(InstantGameInstanceModel). \
                order_by(InstantGameInstanceModel.created_at.desc()).first()
            if instance_info is None:
                self.return_error(40005)
            balance_btc = ''
            balance_eth = ''
            balance_usdt = ''
            balance_eos = ''
            balance_exp = ''
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
            result = {
                'instance': {
                    'id': instance_info._id,
                    'game_serial': instance_info.game_serial,
                    'game_title': instance_info.game_title,
                    'game_describe': instance_info.game_describe,
                    'need': instance_info.need,
                    'status': instance_info.status,
                    'bet_token': self.get_coin_name(instance_info.bet_token),
                    'max_bet_ratio': instance_info.max_bet_ratio
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
                    'exp': decimal_to_str(balance_exp, 4),
                }
            }
            return result

    def get_instant_result(self, part_in_id):
        with MysqlTools().session_scope() as session:
            part_in_info = session.query(ParticipateInModel). \
                filter(ParticipateInModel._id == part_in_id).first()
            if part_in_info is None:
                self.return_error(40016)
            pattern = re.compile(r'[\[\]\s]')
            award_numbers_list = part_in_info.award_numbers
            indiana_numbers = pattern.sub('', award_numbers_list).split(',')
            number_list = []
            is_win = False
            for i in indiana_numbers:
                if i == part_in_info.win_number:
                    status = True
                else:
                    status = False
                number_list.append({
                    'number': i,
                    'is_win': status
                })
            if part_in_info.win_number in indiana_numbers:
                is_win = True
        return {
            'is_win': is_win,
            'indiana_numbers': number_list,
            'win_number': part_in_info.win_number,
            'created_at': str(part_in_info.created_at),
            'received_time': timestamp_to_str(str_to_timestamp(part_in_info.received_time), format_style="%Y-%m-%d %H:%M:%S"),
            'block_no': part_in_info.block_no,
            'bet_hash': part_in_info.bet_hash,
        }

    # 检查项目体验金占比剩余额度以及个人当天最大体验金使用额度(每天最多用10个)
    def check_instance_exp_limit(self, session, user_id, game_serial):
        exp_coin_id = int(_COIN_ID_EXP)
        result = {
            'instance_limit': 0,
            'user_limit': 0,
            'total_pay_number': 0
        }
        # with MysqlTools().session_scope() as session:
        total_pay_number = session.query(func.sum(ParticipateInModel.bet_number * ParticipateInModel.bet_unit)). \
            filter(ParticipateInModel.game_serial == game_serial,
                   ParticipateInModel.pay_token != int(_COIN_ID_EXP)).first()
        # instance_exp_limit = session.query(func.sum(ParticipateInModel.bet_number * ParticipateInModel.bet_unit)). \
        #     filter(ParticipateInModel.game_serial == game_serial,
        #            ParticipateInModel.pay_token == exp_coin_id).first()
        user_limit = session.query(func.sum(ParticipateInModel.bet_number * ParticipateInModel.bet_unit)). \
            filter(ParticipateInModel.user_id == user_id,
                   ParticipateInModel.game_instance_id == 0,
                   ParticipateInModel.pay_token == exp_coin_id,
                   func.date_format(ParticipateInModel.created_at, "%Y-%m-%d") ==
                   func.date_format(get_utc_now(), "%Y-%m-%d")).first()
        # if instance_exp_limit[0] is not None:
        #     result['instance_limit'] = int(instance_exp_limit[0])
        if user_limit[0] is not None:
            result['user_limit'] = int(user_limit[0])
        if total_pay_number[0] is not None:
            result['total_pay_number'] = int(total_pay_number[0])
        return result

    def get_instant_part_in_list(self, limit, offset, game_serial='', bet_time_start='',
                                 bet_time_end='', result='', user_name='', start_id=None):
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
            if user_name != '':
                q = q.filter(ParticipateInModel.nick_name == user_name)
            if game_serial != '':
                q = q.filter(ParticipateInModel.game_serial == game_serial)
            if bet_time_start != '':
                q = q.filter(ParticipateInModel.created_at >= bet_time_start)
            if bet_time_end != '':
                q = q.filter(ParticipateInModel.created_at <= bet_time_end)
            if result != '':
                q = q.filter(ParticipateInModel.result == result)
            game_instance_id = 0
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
                is_win = False
                if participate.win_number in participate.award_numbers:
                    is_win = True
                result_dict['content'].append({
                    "id": participate._id,
                    "user": user_name,
                    "bet_time": str(participate.created_at),
                    "channel": participate.channel,
                    "bet_token": self.get_coin_name(participate.bet_token),
                    "bet_unit": participate.bet_unit,
                    "bet_number": decimal_to_str(participate.bet_number, 8),
                    "pay_token": self.get_coin_name(participate.pay_token),
                    "pay_number": decimal_to_str(participate.pay_number, 8),
                    'game_serial': participate.game_serial,
                    "is_win": is_win
                })
        return result_dict
