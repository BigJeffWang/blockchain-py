import decimal
import json
import time

from sqlalchemy import func

from models.game_digital_instance_model import GameDigitalInstanceModel
from models.game_digital_template_model import GameDigitalTemplateModel
from models.game_get_lottery_block_info_model import GameGetLotteryBlockInfoModel
from models.participate_in_model import ParticipateInModel
from models.winning_record_model import WinningRecordModel
from services.account_service import AccountService
from services.base_service import BaseService
from services.block_chain_info_service import BlockChainInfoService
from services.block_hash_service import BlockHashService
from services.game_service import GameService
from services.participate_in_service import ParticipateInService
from tools.mysql_tool import MysqlTools
# 后台模版操作Servie
from tools.tool import is_number
from utils.log import raise_logger
from utils.time_util import get_utc_now
from utils.util import get_offset_by_page, get_page_by_offset


class GameModelServie(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

        if dic.get('handling_fee', "") == '':
            return self.return_error(50000)
        if is_number(dic.get('handling_fee')):
            if float(dic.get('handling_fee')) < 0:
                return self.return_error(50002)
        else:
            return self.return_error(50002)

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
            digital_template_model = GameDigitalTemplateModel
            q = session.query(digital_template_model).filter(
                GameDigitalTemplateModel.game_title == dic['game_title']).with_for_update().all()
            if len(q) > 0:
                return self.return_error(50003)

            digital_template_model = digital_template_model(
                game_title=dic['game_title'],
                reward_token=int(dic['reward_token']),
                bet_token=int(dic['bet_token']),
                bet_unit=int(dic['bet_unit']),
                reward_quantity=int(dic['reward_quantity']),
                need_ceiling=int(dic['need_ceiling']),
                need_floor=int(dic['need_floor']),
                exceeded_ratio=int(dic['exceeded_ratio']),
                experience=int(dic.get('experience', '0')),
                handling_fee=float(dic['handling_fee']),
                support_token=dic['support_token'],
                template_status=int(dic['template_status']),
                auto_release=int(dic['auto_release']),
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
            q = session.query(GameDigitalTemplateModel)
            if dic.get('id', '') != '':
                q = q.filter(GameDigitalTemplateModel._id == dic['id'])
            if dic.get('game_title', '') != '':
                q = q.filter(GameDigitalTemplateModel.game_title == dic['game_title'])
            if dic.get('reward_quantity', '') != '':
                q = q.filter(GameDigitalTemplateModel.reward_quantity == int(dic['reward_quantity']))

            if dic.get('release_time_start', '') != '':
                q = q.filter(GameDigitalTemplateModel.created_at >= dic['release_time_start'])
            if dic.get('release_time_end', '') != '':
                q = q.filter(GameDigitalTemplateModel.created_at <= dic['release_time_end'])

            if dic.get('template_status', '') != '':
                q = q.filter(GameDigitalTemplateModel.template_status == int(dic['template_status']))
            if dic.get('auto_release', '') != '':
                q = q.filter(GameDigitalTemplateModel.auto_release == int(dic['auto_release']))

            total = q.count()
            count = get_page_by_offset(total, limit)

            if start_id is not None:
                q = q.filter(GameDigitalTemplateModel._id < str(start_id))

            query_result = q.order_by(GameDigitalTemplateModel._id.desc()).limit(limit).offset(offset).all()

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
                        # 'phase_prefix': i.phase_prefix,
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

        if dic.get('handling_fee', '') == '':
            return self.return_error(50000)
        if is_number(dic.get('handling_fee')):
            if float(dic.get('handling_fee')) < 0:
                return self.return_error(50002)
        else:
            return self.return_error(50002)

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
            model = session.query(GameDigitalTemplateModel).filter(
                GameDigitalTemplateModel._id == id).with_for_update().first()
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
            model.handling_fee = dic['handling_fee'],
            model.support_token = dic['support_token'],
            model.template_status = int(dic['template_status']),
            model.auto_release = int(dic['auto_release']),
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
            model = session.query(GameDigitalTemplateModel).filter(
                GameDigitalTemplateModel._id == id).delete()
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
            model = session.query(GameDigitalTemplateModel).filter(
                GameDigitalTemplateModel._id == id).with_for_update().first()
            if model is None == 0:
                return self.return_error(50001)

            if model.template_status == 0:
                model.template_status = 1
            else:
                model.template_status = 0

            session.commit()
            return True


# 开奖模块=======================================================================================================================
# 创建 game开奖 区块信息
def addGameLotteryBlock(id: str):
    with MysqlTools().session_scope() as session:
        model = session.query(GameGetLotteryBlockInfoModel).filter(
            GameGetLotteryBlockInfoModel.game_instance_id == id).with_for_update().first()

        if model is None:
            time_stamp = int(time.time())
            block_info = GameGetLotteryBlockInfoModel(
                game_instance_id=int(id),
                time_stamp=time_stamp,
            )
            session.add(block_info)
            session.commit()
            return time_stamp

        if model.block_hash is None or model.block_hash == '':
            return model.time_stamp

        if model.block_hash:
            return model.block_hash


# 修改 game开奖 区块信息
def modifyGameLotteryBlock(id: str, hash: str):
    with MysqlTools().session_scope() as session:
        model = session.query(GameGetLotteryBlockInfoModel).filter(
            GameGetLotteryBlockInfoModel.game_instance_id == int(id)).with_for_update().first()

        if model is None:
            return False
        else:
            model.block_hash = hash
            session.commit()

            return True


class GamePublishLotteryServie(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def checkGameSoldOut(self, id: str):
        with MysqlTools().session_scope() as session:
            model = session.query(GameDigitalInstanceModel).filter(
                GameDigitalInstanceModel._id == id, GameDigitalInstanceModel.status == 1).with_for_update().first()
            if model is None:
                return False

            result_block = {
                "block_no": 0,
                "block_hash": "",
                "timestamp": "",
                "received_time": ""
            }

            # 测试数据
            # result_block = {'block_no': 1445650,
            #                 'block_hash': '00000000000000c53778c8dd69f419a571e6faf0775d7e7a50bb00cb7fa571ac',
            #                 'timestamp': '2018-11-28 15:17:27', 'received_time': '2018-11-28 14:30:39'}

            block_info = addGameLotteryBlock(id)
            raise_logger("开奖block_info:" + str(block_info), "game_publish_lottery", "info")
            # print("lottery_time_stamp:", block_info)

            service = BlockHashService()
            # 第一次返回时间戳 通过时间戳查询区块
            if isinstance(block_info, int):
                hash = service.get_match_block_no(block_info)
                raise_logger("第一次开奖时间戳换hash:" + str(hash), "game_publish_lottery", "info")
                # print("第一次开奖时间戳换hash:", str(hash))

                modifyGameLotteryBlock(id, hash)

                result_block = service.get_hash_by_no(hash)
                if result_block is False:
                    raise_logger("第一次开奖没有返回 区块号", "game_publish_lottery", "info")
                    # print("first no lottery")

                    return

            # 第二次
            if isinstance(block_info, str):
                result_block = service.get_hash_by_no(block_info)
                if result_block is False:
                    raise_logger("第二次开奖没有返回 区块号", "game_publish_lottery", "info")
                    # print("secound no lottery")

                    return

            hash_numbers = result_block["block_hash"]
            raise_logger("项目:" + str(id) + "   中奖区块号:" + str(hash_numbers), "game_publish_lottery", "info")

            if hash_numbers == "":
                raise_logger("开奖异常:80001", "game_publish_lottery", "info")
                return False

            prize_number = int(hash_numbers, 16) % model.need + 1
            raise_logger("项目:" + str(id) + "    中奖号码:" + str(prize_number), "game_publish_lottery", "info")
            # print("中奖号码", str(prize_number))

            participate_in = ParticipateInService()
            records = participate_in.search_model(session, id)
            # 无人参与
            if len(records) <= 0:
                raise_logger("无人参与80002", "game_publish_lottery", "info")
                return False

            user_id = ""
            user_pay_token = 0
            user_bet_number = 0
            user_type = 0
            merge_id = -1
            part_in_id = -1
            for item in records:
                numbers = json.loads(item.award_numbers)
                if prize_number in numbers:
                    part_in_id = item._id
                    user_id = item.user_id
                    user_pay_token = item.pay_token
                    user_bet_number = item.bet_number
                    user_type = item.user_type
                    merge_id = item.merge_id
                    break

            # 无人中奖
            if user_id == "":
                raise_logger("无人中奖80003", "game_publish_lottery", "info")
                return False

            raise_logger("中奖user_id:" + str(user_id), "game_publish_lottery", "info")

            win_record = session.query(GameDigitalInstanceModel).filter(
                WinningRecordModel.game_instance_id == id).first()
            # game_instance_id已经存在开奖纪录
            if win_record:
                raise_logger(str(id) + "开奖纪录", "game_publish_lottery", "info")
                return False

            # 修改game实体添加开奖时间 和币价信息
            game_service = GameService()
            lottery_time_str = str(get_utc_now())
            lottery_time = lottery_time_str[0:19]

            if game_service.modifyDigitalInstance(model,
                                                  {"game_id": id,
                                                   "lottery_time": lottery_time}) is False:
                raise_logger("开奖纪录modifyDigitalInstance   False", "game_publish_lottery", "info")
                return False

            raise_logger("开奖纪录modifyDigitalInstance 修改成功", "game_publish_lottery", "info")

            try:
                # 添加开奖纪录
                winning_record_model = WinningRecordModel(
                    created_at=lottery_time,
                    game_instance_id=id,
                    game_serial=model.game_serial,
                    bet_serial=str(prize_number),
                    bet_hash=hash_numbers,
                    reward_token=model.reward_token,
                    reward_quantity=model.reward_quantity,
                    user_id=user_id,
                    bet_token=user_pay_token,
                    bet_number=user_bet_number,
                    user_type=user_type,
                    block_no=result_block['block_no'],
                    timestamp=result_block['timestamp'],
                    received_time=result_block['received_time'],
                    participation=model.participation,
                    block_type="0",
                    merge_id=merge_id
                )
                session.add(winning_record_model)
                session.flush()

                raise_logger("添加开奖纪录", "game_publish_lottery", "info")

                # 真实用户 添加 中奖金额
                if user_type == 0:
                    account_service = AccountService()
                    # 合买逻辑
                    if merge_id != -1:
                        raise_logger("合买逻辑", "game_publish_lottery", "info")
                        total_bet = session.query(func.sum(ParticipateInModel.bet_number).label('total')). \
                            filter(ParticipateInModel.merge_id == merge_id).first()
                        win_users = session.query(ParticipateInModel). \
                            filter(ParticipateInModel.merge_id == merge_id).all()
                        for win_user in win_users:
                            reward_quantity = win_user.bet_number / int(float(total_bet.total)) * model.reward_quantity \
                                              * (1 - float(model.handling_fee) / 100)
                            result = account_service.do_win_new_session(win_user.user_id,
                                                                        model.reward_token,
                                                                        decimal.Decimal(reward_quantity),
                                                                        str(part_in_id),
                                                                        win_user.bet_number,
                                                                        win_user.game_serial)
                            if isinstance(result, int) is False:
                                raise_logger("分钱失败" + "user:" + str(win_user.user_id), "game_publish_lottery", "info")
                                session.rollback()
                                return False
                            if result != 0:
                                raise_logger("分钱失败" + "user:" + str(win_user.user_id), "game_publish_lottery", "info")
                                session.rollback()
                                return False
                    else:
                        raise_logger("非合买逻辑", "game_publish_lottery", "info")
                        # 实际奖励金额 = 奖励金额 * (1-手续费%)
                        reward_quantity = model.reward_quantity * (1 - model.handling_fee / 100)
                        result = account_service.do_win(session,
                                                        user_id,
                                                        model.reward_token,
                                                        reward_quantity,
                                                        str(part_in_id),
                                                        user_bet_number,
                                                        model.game_serial
                                                        )

                        if isinstance(result, int) is False:
                            raise_logger("分钱失败" + "user:" + str(user_id), "game_publish_lottery", "info")
                            session.rollback()
                            return False
                        if result != 0:
                            raise_logger("分钱失败" + "user:" + str(user_id), "game_publish_lottery", "info")
                            session.rollback()
                            return False

                raise_logger("分钱成功", "game_publish_lottery", "info")

                try:
                    # 添加上链数据
                    lottery_time_str = str(model.lottery_time)
                    release_time_str = str(model.release_time)
                    full_load_time_str = str(model.full_load_time)
                    nick_name = session.query(ParticipateInModel.nick_name).filter(
                        ParticipateInModel.user_id == user_id).first()
                    if BlockChainInfoService().insert_block_chain_info("", id, 0, {
                        "id": winning_record_model._id,
                        "game_instance_id": winning_record_model.game_instance_id,
                        "game_serial": winning_record_model.game_serial,
                        "bet_serial": winning_record_model.bet_serial,
                        "bet_hash": winning_record_model.bet_hash,
                        "reward_token": winning_record_model.reward_token,
                        "reward_quantity": winning_record_model.reward_quantity,
                        "user_id": winning_record_model.user_id,
                        "bet_token": winning_record_model.bet_token,
                        "bet_number": winning_record_model.bet_number,
                        "user_type": winning_record_model.user_type,
                        "block_no": winning_record_model.block_no,
                        "timestamp": winning_record_model.timestamp,
                        "received_time": winning_record_model.received_time,
                        "block_type": winning_record_model.block_type,
                        "participation": winning_record_model.participation,
                        "lottery_time": lottery_time_str[0:19],
                        "game_describe": model.game_describe,
                        "nick_name": nick_name,
                        "need": model.need,
                        "release_time": release_time_str[0:19],
                        "full_load_time": full_load_time_str[0:19],
                    }):
                        winning_record_model.chain_status = 1

                except Exception as e:
                    raise_logger("开奖insert_block_chain_info     Exception", "game_publish_lottery", "info")
                session.commit()
                return True

            except Exception as e:
                raise_logger(e.__str__(), "game_publish_lottery", "info")
                session.rollback()
                return False

    def check_game_sold_out_by_eos(self, id, block_no, block_hash, timestamp, received_time):
        with MysqlTools().session_scope() as session:
            model = session.query(GameDigitalInstanceModel).filter(
                GameDigitalInstanceModel._id == id, GameDigitalInstanceModel.status == 1).with_for_update().first()
            if model is None:
                return False
            result_block = {
                'block_no': block_no,
                'block_hash': block_hash,
                'timestamp': timestamp,
                'received_time': received_time
            }
            hash_numbers = result_block["block_hash"]
            raise_logger("项目:" + str(id) + "   中奖区块号:" + str(hash_numbers), "game_publish_lottery", "info")

            if hash_numbers == "":
                raise_logger("开奖异常:80001", "game_publish_lottery", "info")
                return False

            prize_number = int(hash_numbers, 16) % model.need + 1
            raise_logger("项目:" + str(id) + "    中奖号码:" + str(prize_number), "game_publish_lottery", "info")
            # print("中奖号码", str(prize_number))

            participate_in = ParticipateInService()
            records = participate_in.search_model(session, id)
            # 无人参与
            if len(records) <= 0:
                raise_logger("无人参与80002", "game_publish_lottery", "info")
                return False

            user_id = ""
            user_pay_token = 0
            user_bet_number = 0
            user_type = 0
            merge_id = -1
            part_in_id = -1
            for item in records:
                numbers = json.loads(item.award_numbers)
                if prize_number in numbers:
                    part_in_id = item._id
                    user_id = item.user_id
                    user_pay_token = item.pay_token
                    user_bet_number = item.bet_number
                    user_type = item.user_type
                    merge_id = item.merge_id
                    break

            # 无人中奖
            if user_id == "":
                raise_logger("无人中奖80003", "game_publish_lottery", "info")
                return False

            raise_logger("中奖user_id:" + str(user_id), "game_publish_lottery", "info")

            win_record = session.query(GameDigitalInstanceModel).filter(
                WinningRecordModel.game_instance_id == id).first()
            # game_instance_id已经存在开奖纪录
            if win_record:
                raise_logger(str(id) + "开奖纪录", "game_publish_lottery", "info")
                return False

            # 修改game实体添加开奖时间 和币价信息
            game_service = GameService()
            lottery_time_str = str(get_utc_now())
            lottery_time = lottery_time_str[0:19]

            if game_service.modifyDigitalInstance(model,
                                                  {"game_id": id,
                                                   "lottery_time": lottery_time}) is False:
                raise_logger("开奖纪录modifyDigitalInstance   False", "game_publish_lottery", "info")
                return False

            raise_logger("开奖纪录modifyDigitalInstance 修改成功", "game_publish_lottery", "info")

            try:
                # 添加开奖纪录
                winning_record_model = WinningRecordModel(
                    created_at=lottery_time,
                    game_instance_id=id,
                    game_serial=model.game_serial,
                    bet_serial=str(prize_number),
                    bet_hash=hash_numbers,
                    reward_token=model.reward_token,
                    reward_quantity=model.reward_quantity,
                    user_id=user_id,
                    bet_token=user_pay_token,
                    bet_number=user_bet_number,
                    user_type=user_type,
                    block_no=result_block['block_no'],
                    timestamp=result_block['timestamp'],
                    received_time=result_block['received_time'],
                    participation=model.participation,
                    block_type="0",
                    merge_id=merge_id
                )
                session.add(winning_record_model)
                session.flush()

                raise_logger("添加开奖纪录", "game_publish_lottery", "info")

                # 真实用户 添加 中奖金额
                if user_type == 0:
                    account_service = AccountService()
                    # 合买逻辑
                    if merge_id != -1:
                        raise_logger("合买逻辑", "game_publish_lottery", "info")
                        total_bet = session.query(func.sum(ParticipateInModel.bet_number).label('total')). \
                            filter(ParticipateInModel.merge_id == merge_id).first()
                        win_users = session.query(ParticipateInModel). \
                            filter(ParticipateInModel.merge_id == merge_id).all()
                        for win_user in win_users:
                            reward_quantity = win_user.bet_number / int(float(total_bet.total)) * model.reward_quantity \
                                              * (1 - float(model.handling_fee) / 100)
                            result = account_service.do_win_new_session(win_user.user_id,
                                                                        model.reward_token,
                                                                        decimal.Decimal(reward_quantity),
                                                                        str(part_in_id),
                                                                        win_user.bet_number,
                                                                        win_user.game_serial)
                            if isinstance(result, int) is False:
                                raise_logger("分钱失败" + "user:" + str(win_user.user_id), "game_publish_lottery", "info")
                                session.rollback()
                                return False
                            if result != 0:
                                raise_logger("分钱失败" + "user:" + str(win_user.user_id), "game_publish_lottery", "info")
                                session.rollback()
                                return False
                    else:
                        raise_logger("非合买逻辑", "game_publish_lottery", "info")
                        # 实际奖励金额 = 奖励金额 * (1-手续费%)
                        reward_quantity = model.reward_quantity * (1 - model.handling_fee / 100)
                        result = account_service.do_win(session,
                                                        user_id,
                                                        model.reward_token,
                                                        reward_quantity,
                                                        str(part_in_id),
                                                        user_bet_number,
                                                        model.game_serial
                                                        )

                        if isinstance(result, int) is False:
                            raise_logger("分钱失败" + "user:" + str(user_id), "game_publish_lottery", "info")
                            session.rollback()
                            return False
                        if result != 0:
                            raise_logger("分钱失败" + "user:" + str(user_id), "game_publish_lottery", "info")
                            session.rollback()
                            return False

                raise_logger("分钱成功", "game_publish_lottery", "info")

                try:
                    # 添加上链数据
                    lottery_time_str = str(model.lottery_time)
                    release_time_str = str(model.release_time)
                    full_load_time_str = str(model.full_load_time)
                    nick_name = session.query(ParticipateInModel.nick_name).filter(
                        ParticipateInModel.user_id == user_id).first()
                    if BlockChainInfoService().insert_block_chain_info("", id, 0, {
                        "id": winning_record_model._id,
                        "game_instance_id": winning_record_model.game_instance_id,
                        "game_serial": winning_record_model.game_serial,
                        "bet_serial": winning_record_model.bet_serial,
                        "bet_hash": winning_record_model.bet_hash,
                        "reward_token": winning_record_model.reward_token,
                        "reward_quantity": winning_record_model.reward_quantity,
                        "user_id": winning_record_model.user_id,
                        "bet_token": winning_record_model.bet_token,
                        "bet_number": winning_record_model.bet_number,
                        "user_type": winning_record_model.user_type,
                        "block_no": winning_record_model.block_no,
                        "timestamp": winning_record_model.timestamp,
                        "received_time": winning_record_model.received_time,
                        "block_type": winning_record_model.block_type,
                        "participation": winning_record_model.participation,
                        "lottery_time": lottery_time_str[0:19],
                        "game_describe": model.game_describe,
                        "nick_name": nick_name,
                        "need": model.need,
                        "release_time": release_time_str[0:19],
                        "full_load_time": full_load_time_str[0:19],
                    }):
                        winning_record_model.chain_status = 1

                except Exception as e:
                    raise_logger("开奖insert_block_chain_info     Exception", "game_publish_lottery", "info")
                session.commit()
                return True

            except Exception as e:
                raise_logger(e.__str__(), "game_publish_lottery", "info")
                session.rollback()
                return False


if __name__ == "__main__":
    pass
    # GamePublishLotteryServie().checkGameSoldOut("97")
