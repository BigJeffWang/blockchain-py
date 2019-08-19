import datetime
import json
import random

from sqlalchemy import func

from common_settings import *
from models.game_digital_instance_model import GameDigitalInstanceModel
from models.game_numbers_set_model import GameNumbersSetModel
from models.participate_in_model import ParticipateInModel
from models.robot_account_model import RobotAccountModel
from models.robot_config_record_model import RobotConfigRecordModel
from models.robot_game_config_record_model import RobotGameConfigRecordModel
from services.account_service import AccountService
from services.base_service import BaseService
from services.block_chain_info_service import BlockChainInfoService
from services.game_model_service import GamePublishLotteryServie
from services.game_service import GameService
from services.wallet_eos_service import WalletEosService
from tools.mysql_tool import MysqlTools
from utils.exchange_rate_util import get_exchange_rate
from utils.log import raise_logger
from utils.time_util import get_utc_now, get_timestamp
from utils.util import get_decimal

"""
用户下注Servie
"""


class GameBetInServie(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # 用户正常下注==================================================================================================================================================================
    def bet_in(self, dic):
        id = dic.get("game_instance_id", "")  # 项目id
        user_id = dic.get("user_id", "")  # 用户id
        user_channel_id = dic.get("user_channel_id", "")  # 用户下注渠道id
        conin_id = dic.get("conin_id", "")  # 投入币种id
        bet_amount = dic.get("bet_amount", "")  # 投注数量
        merge_id = dic.get("merge_id", -1)  # 合并投注id
        # transaction_password = dic.get("transaction_password", "")  # 交易密码

        with MysqlTools().session_scope() as session:
            # 查询项目
            model = session.query(GameDigitalInstanceModel).filter(
                GameDigitalInstanceModel._id == id).with_for_update().first()
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
                limit = self.check_instance_exp_limit(session, user_id, id)
                instance_limit = limit['instance_limit']
                user_limit = limit['user_limit']
                if user_limit > 10 - int(bet_amount):
                    self.return_error(60017)
                if instance_limit >= exp:
                    self.return_error(60016)

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

            # 验证交易密码
            # if account_service.check_pay_password(user_id, transaction_password) is False:
            #     return self.return_error(35024)
            # raise_logger("begin", "game_bet_in", "info")
            # 获取下注编号
            game_numbers = session.query(GameNumbersSetModel).filter(
                GameNumbersSetModel.game_serial == model.game_serial).with_for_update().all()
            numbers = []
            for num in game_numbers:
                numbers.append(num.number)
            numbers = random.sample(numbers, int(bet_amount))
            # raise_logger("get game_numbers", "game_bet_in", "info")
            if isinstance(numbers, list):
                nick_name = account_service.get_inner_user_account_info(session, user_id).get("nick_name")
                try:
                    # 添加参与记录
                    participate_in_model = ParticipateInModel(
                        game_instance_id=model._id,
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
                        merge_id=merge_id
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
                                                    user_channel_id
                                                    )
                    # raise_logger("do_bet success", "game_bet_in", "info")
                    if isinstance(result, int):
                        if result == 0:
                            # 修改项目状态
                            game_service = GameService()
                            # raise_logger("modifyDigitalInstance begin", "game_bet_in", "info")
                            if game_service.modifyDigitalInstance(model,
                                                                  {"game_id": id,
                                                                   "add_bet_number": int(bet_amount),
                                                                   "full_load_time": participate_in_model.created_at,
                                                                   "add_people": 1}) is False:
                                session.rollback()
                                raise_logger("modifyDigitalInstance err", "game_bet_in", "info")
                                return self.return_error(80005)
                            # raise_logger("modifyDigitalInstance succ", "game_bet_in", "info")
                            try:
                                created_at_str = str(participate_in_model.created_at)
                                update_at_str = str(participate_in_model.update_at)
                                deleted_at_str = str(participate_in_model.deleted_at)
                                deleted_str = str(participate_in_model.deleted)
                                if BlockChainInfoService().insert_block_chain_info(user_id,
                                                                                   participate_in_model.game_instance_id,
                                                                                   1,
                                                                                   {
                                                                                       "id": participate_in_model._id,
                                                                                       "created_at": created_at_str[
                                                                                                     0:19],
                                                                                       "update_at": update_at_str[0:19],
                                                                                       "deleted_at": deleted_at_str[
                                                                                                     0:19],
                                                                                       "deleted": deleted_str[0:19],
                                                                                       "game_instance_id": str(
                                                                                           participate_in_model.game_instance_id),
                                                                                       "template_id": participate_in_model.template_id,
                                                                                       "game_serial": participate_in_model.game_serial,
                                                                                       "bet_token": participate_in_model.bet_token,
                                                                                       "user_id": participate_in_model.user_id,
                                                                                       "nick_name": participate_in_model.nick_name,
                                                                                       "channel": participate_in_model.channel,
                                                                                       "pay_token": participate_in_model.pay_token,
                                                                                       "bet_number": participate_in_model.bet_number,
                                                                                       "pay_number": str(
                                                                                           participate_in_model.pay_number),
                                                                                       "award_numbers": participate_in_model.award_numbers,
                                                                                       "user_type": participate_in_model.user_type,
                                                                                   }):
                                    participate_in_model.chain_status = 1
                                    # raise_logger("insert_block succ", "game_bet_in", "info")
                                else:
                                    raise_logger("insert_block err", "game_bet_in", "info")
                            except Exception as e:
                                session.rollback()
                                raise_logger(e, "game_bet_in", "info")
                            # raise_logger("pri del GameNumbersSetModel", "game_bet_in", "info")
                            for i in numbers:
                                # raise_logger("pri del GameNumbersSetModel", "game_bet_in", "info")
                                # game_number_filters = {"game_serial": model.game_serial, "number": i}
                                session.query(GameNumbersSetModel). \
                                    filter(GameNumbersSetModel.game_serial == model.game_serial,
                                           GameNumbersSetModel.number == i).delete()
                                # number_filter.time_stamp = 1
                                # session.delete(num_filters)
                            # raise_logger("GameNumbersSetModel delete succ", "game_bet_in", "info")

                            # # 检测游戏是否售罄需要申请开奖
                            # instance = session.query(GameDigitalInstanceModel).filter(
                            #     GameDigitalInstanceModel._id == id).first()
                            if int(model.status) == 1:
                                add_result = WalletEosService().lottery_adduce(id, get_timestamp(
                                    model.full_load_time))
                                if not add_result:
                                    raise_logger("lottery_adduce fail", "game_bet_in", "info")

                            session.commit()
                            # raise_logger("commit succ", "game_bet_in", "info")
                            try:
                                # # 提交验证是否需要上线新项目
                                game_service.automatic_release(session, model.template_id)
                            except Exception as e:
                                raise_logger(e, "game_bet_in", "info")

                            can_merge = False
                            if int(bet_amount) >= model.merge_threshold and merge_id == -1:
                                can_merge = True
                            # raise_logger("pri return", "game_bet_in", "info")
                            return {
                                'numbers': numbers,
                                'can_merge': can_merge,
                                'part_in_id': participate_in_model._id
                            }

                        else:
                            session.rollback()
                            return self.return_error(60009)
                    else:
                        session.rollback()
                        return self.return_error(60010)

                except Exception as e:
                    raise_logger(e, "game_bet_in", "info")
                    session.rollback()
                    return self.return_error(60011)

                if isinstance(numbers, int):
                    session.rollback()
                    return self.return_error(60012)

            else:
                session.rollback()
                return self.return_error(60007)

    # 机器人下注 ==================================================================================================================================================================
    def robot_bet_in(self, dic):
        id = dic.get("game_instance_id", "")  # 项目id
        user_id = dic.get("user_id", "")  # 用户id
        conin_id = dic.get("conin_id", 0)  # 投入币种id
        bet_amount = dic.get("bet_amount", 0)  # 投注数量
        time_stamp = dic.get("time_stamp", 0)  # 纪录时间戳

        with MysqlTools().session_scope() as session:
            # 查询项目
            model = session.query(GameDigitalInstanceModel).filter(
                GameDigitalInstanceModel._id == id).with_for_update().first()
            if model is None:
                raise_logger("机器人下注失败60001", "game_bet_in", "info")
                return 60001
            if model.status == 1:
                raise_logger("机器人下注失败60002", "game_bet_in", "info")
                return 60002
            if model.status == 2:
                raise_logger("机器人下注失败60003", "game_bet_in", "info")
                return 60003
            if model.status == 0:
                can_bet = model.need - model.bet_number
                if can_bet <= 0:
                    raise_logger("机器人下注失败60002", "game_bet_in", "info")
                    return 60005
                if int(bet_amount) > can_bet:
                    raise_logger("机器人下注失败60004", "game_bet_in", "info")
                    return 60004

            # 查询币价 币种实际需要金额
            exchange_rate = get_exchange_rate(int(conin_id))
            # (投注数量 * 投注单位) / 投注币种兑换usdt比例
            bet_money = (int(bet_amount) * model.bet_unit) / exchange_rate['price']

            game_numbers = session.query(GameNumbersSetModel).filter(
                GameNumbersSetModel.game_serial == model.game_serial).with_for_update().all()
            numbers = []
            for num in game_numbers:
                numbers.append(num.number)

            try:
                numbers = random.sample(numbers, int(bet_amount))
            except Exception as e:
                raise_logger("机器人下注失败 没有numbers", "game_bet_in", "info")
                return False
            if isinstance(numbers, list) and len(numbers) > 0:
                # try:
                    # 修改机器人账户状态
                    user = session.query(RobotAccountModel).filter(
                        RobotAccountModel.user_id == user_id).with_for_update().first()
                    if user is None:
                        raise_logger("机器人下注失败70002", "game_bet_in", "info")
                        return 70002
                    user.status = 0

                    # 添加投注纪录
                    participate_in_model = ParticipateInModel(
                        game_instance_id=model._id,
                        template_id=model.template_id,
                        game_serial=model.game_serial,
                        game_title=model.game_title,
                        release_type=model.release_type,
                        bet_unit=model.bet_unit,
                        bet_token=model.bet_token,
                        user_id=user_id,
                        nick_name=user.nick_name,
                        channel="0",
                        bet_number=int(bet_amount),
                        pay_token=int(conin_id),
                        pay_number=get_decimal(bet_money),
                        award_numbers=json.dumps(numbers),
                        user_type=1
                    )
                    session.add(participate_in_model)

                    # 修改项目信息
                    game_service = GameService()
                    if game_service.modifyDigitalInstance(model,
                                                          {"game_id": id,
                                                           "add_bet_number": int(bet_amount),
                                                           "full_load_time": participate_in_model.created_at,
                                                           "add_people": 1}) is False:
                        session.rollback()
                        raise_logger("机器人下注失败80005", "game_bet_in", "info")
                        return 80005

                    # 修改机器人配置纪录 下注状态
                    record = session.query(RobotConfigRecordModel).filter(
                        RobotConfigRecordModel.game_instance_id == id,
                        RobotConfigRecordModel.user_id == user_id,
                        RobotConfigRecordModel.time_stamp == time_stamp
                    ).with_for_update().first()
                    if record is None:
                        raise_logger("机器人下注失败70002", "game_bet_in", "info")
                        return 70002
                    record.bet_status = 1

                    # 查看本期 机器人是否都已下注完成
                    is_finish = True
                    robots = session.query(RobotConfigRecordModel).filter(
                        RobotConfigRecordModel.game_instance_id == id,
                        RobotConfigRecordModel.time_stamp == time_stamp
                    ).all()
                    for r in robots:
                        if r.bet_status == 0 or r.bet_status == 2:
                            is_finish = False
                            break

                    if is_finish:
                        # 修改 游戏机器人配置纪录
                        q = session.query(RobotGameConfigRecordModel).filter(
                            RobotGameConfigRecordModel.game_instance_id == id,
                            RobotGameConfigRecordModel.time_stamp == time_stamp
                        ).with_for_update().first()

                        if q is None:
                            raise_logger("机器人下注失败70003", "game_bet_in", "info")
                            return 70003

                        q.status = 2
                        q.end_of_real_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

                    session.flush()

                    try:
                        created_at_str = str(participate_in_model.created_at)
                        update_at_str = str(participate_in_model.update_at)
                        deleted_at_str = str(participate_in_model.deleted_at)
                        deleted_str = str(participate_in_model.deleted)
                        dic = {
                            "id": participate_in_model._id,
                            "created_at": created_at_str[0:19],
                            "update_at": update_at_str[0:19],
                            "deleted_at": deleted_at_str[0:19],
                            "deleted": deleted_str[0:19],
                            "game_instance_id": participate_in_model.game_instance_id,
                            "template_id": participate_in_model.template_id,
                            "game_serial": participate_in_model.game_serial,
                            "bet_token": participate_in_model.bet_token,
                            "user_id": participate_in_model.user_id,
                            "nick_name": participate_in_model.nick_name,
                            "channel": participate_in_model.channel,
                            "pay_token": participate_in_model.pay_token,
                            "bet_number": participate_in_model.bet_number,
                            "pay_number": str(participate_in_model.pay_number),
                            "award_numbers": participate_in_model.award_numbers,
                            "user_type": participate_in_model.user_type,
                        }

                        if BlockChainInfoService().insert_block_chain_info(user_id,
                                                                           participate_in_model.game_instance_id,
                                                                           1, dic):
                            participate_in_model.chain_status = 1

                    except Exception as e:
                        session.rollback()
                        raise_logger("insert_block_chain_info", "game_bet_in", "info")

                    g_service = model.game_serial
                    for i in numbers:
                        session.query(GameNumbersSetModel).filter(
                            GameNumbersSetModel.game_serial == g_service,
                            GameNumbersSetModel.number == i).delete()
                    # # 检测游戏是否售罄需要申请开奖
                    if int(model.status) == 1:
                        add_result = WalletEosService().lottery_adduce(id, get_timestamp(
                            model.full_load_time))
                        if not add_result:
                            raise_logger("lottery_adduce fail", "game_bet_in", "info")

                    session.commit()

                    try:
                        # # 提交验证是否需要上线新项目
                        game_service.automatic_release(session, model.template_id)
                    except Exception as e:
                        raise_logger("automatic_release", "game_bet_in", "info")

                    return True

                # except Exception as e:
                #     session.rollback()
                #     raise_logger("机器人下注失败60006", "game_bet_in", "info")
                #     return 60006

            return False

    # 检查项目体验金占比剩余额度以及个人当天最大体验金使用额度(每天最多用10个)
    def check_instance_exp_limit(self, session, user_id, game_instance_id):
        exp_coin_id = int(_COIN_ID_EXP)
        result = {
            'instance_limit': 0,
            'user_limit': 0
        }
        # with MysqlTools().session_scope() as session:
        instance_exp_limit = session.query(func.sum(ParticipateInModel.bet_number * ParticipateInModel.bet_unit)). \
            filter(ParticipateInModel.game_instance_id == game_instance_id,
                   ParticipateInModel.pay_token == exp_coin_id).first()
        user_limit = session.query(func.sum(ParticipateInModel.bet_number * ParticipateInModel.bet_unit)). \
            filter(ParticipateInModel.user_id == user_id,
                   ParticipateInModel.game_instance_id != 0,
                   ParticipateInModel.pay_token == exp_coin_id,
                   func.date_format(ParticipateInModel.created_at, "%Y-%m-%d") ==
                   func.date_format(get_utc_now(), "%Y-%m-%d")).first()
        if instance_exp_limit[0] is not None:
            result['instance_limit'] = int(instance_exp_limit[0])
        if user_limit[0] is not None:
            result['user_limit'] = int(user_limit[0])
        return result

# if __name__ == "__main__":
#     re = GameBetInServie().check_instance_exp_limit('3e77d2faa4d844ae8a1ac3c8443d3f2a', 34)
#     print('re====', re)
