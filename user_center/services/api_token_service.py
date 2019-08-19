import datetime
import time
import uuid
from services.base_service import BaseService
from utils import n_day_ago
from tools.redis_tools import RedisTools
from common_settings import *
from models.api_token_model import ApiTokenModel
from models.invest_user_model import InvestUserModel
from models.admin_user_model import AdminUserModel


class ApiTokenService(BaseService):
    def __init__(self, *args, **kwargs):
        super(ApiTokenService, self).__init__(*args, **kwargs)
        self.access_token_ex_web = 3600  # 一小时
        self.refresh_token_ex_web = 86400  # 一天
        self.access_token_ex_mobile = 604800  # 一周
        self.refresh_token_ex_mobile = 2592000  # 30天
        self.redis_access_token_key = 'access_token:'
        self.mysql_access_token_key = 'AccessToken'
        self.mysql_refresh_token_key = 'RefreshToken'

    def get_access_token_ex(self, source):
        if source in [_SOURCE_TYPE_3, _SOURCE_TYPE_4]:
            return self.access_token_ex_mobile
        else:
            return self.access_token_ex_web

    def get_refresh_token_ex(self, source):
        if source in [_SOURCE_TYPE_3, _SOURCE_TYPE_4]:
            return self.refresh_token_ex_mobile
        else:
            return self.refresh_token_ex_web

    def generator_user_tokens(self, user_id, user_type=_USER_TYPE_INVEST, source=ApiTokenModel.source_type_1):
        """
        生成用的access_token和refresh_token
        :param user_id:
        :return:
        """
        self.check_api_token_source(source)
        with self.session_scope() as session:
            # 将之前的token删除
            self.delete_all_token(user_id, user_type, source)

            redis_tool = RedisTools()
            access_token_key = self.make_access_token_redis_key(user_id, user_type, source)
            redis_tool.delete(access_token_key)

            access_token_ex = self.get_access_token_ex(source)
            refresh_token_ex = self.get_refresh_token_ex(source)

            # 生成token
            access_token_expire_time = datetime.datetime.fromtimestamp(int(time.time()) + access_token_ex)
            refresh_token_expire_time = datetime.datetime.fromtimestamp(int(time.time()) + refresh_token_ex)
            access_token = self.generate_token(user_id, uuid.uuid4().hex)
            refresh_token = self.generate_token(user_id, uuid.uuid4().hex)

            access_token_model = ApiTokenModel(user_id=user_id, token_type=self.mysql_access_token_key,
                                               token=access_token, user_type=user_type, source=source,
                                               expire_at=access_token_expire_time)
            refresh_token_model = ApiTokenModel(user_id=user_id, token_type=self.mysql_refresh_token_key,
                                                token=refresh_token, user_type=user_type, source=source,
                                                expire_at=refresh_token_expire_time)
            session.add(access_token_model)
            session.add(refresh_token_model)
            session.commit()
            redis_tool.set(access_token_key, access_token, ex=access_token_ex)

            result = {
                "access_token": access_token,
                "access_token_expire_time": str(access_token_expire_time),
                "refresh_token": refresh_token,
                "refresh_token_expire_time": str(refresh_token_expire_time),
                "user_id": user_id,
            }

            return result

    def refresh_user_access_token(self, user_id, user_type=_USER_TYPE_INVEST, source=ApiTokenModel.source_type_1):
        """
        刷新用户access_token
        :param user_id: 用户ID
        :return:
        """
        self.check_api_token_source(source)
        with self.session_scope() as session:
            # 1.0 获取用户可用时间大约2天的token
            access_token = session.query(ApiTokenModel).filter(
                ApiTokenModel.deleted == False,
                ApiTokenModel.expire_at > n_day_ago(datetime.datetime.now(), -2),
                ApiTokenModel.token_type == self.mysql_access_token_key,
                ApiTokenModel.user_id == user_id,
                ApiTokenModel.user_type == user_type,
                ApiTokenModel.source == source,
            ).first()
            # 2.0 验证用户名下有没有可用的access_token,如果有,则返回
            if access_token:
                return {
                    "access_token": access_token.token,
                    "access_token_expire_time": str(access_token.expire_at)
                }
            # 3.0将之前的token删除
            self.delete_all_token(user_id, user_type, source, reserve_refresh_token=True)

            access_token_ex = self.get_access_token_ex(source)

            # 4.0生成token
            access_token_expire_time = datetime.datetime.fromtimestamp(int(time.time()) + access_token_ex)
            access_token = self.generate_token(user_id, uuid.uuid4().hex)

            access_token_model = ApiTokenModel(user_id=user_id, token_type=self.mysql_access_token_key,
                                               token=access_token, user_type=user_type, source=source,
                                               expire_at=access_token_expire_time)
            session.add(access_token_model)
            session.commit()

            # 5.0更新redis
            redis_tool = RedisTools()
            access_token_key = self.make_access_token_redis_key(user_id, user_type, source)
            redis_tool.set(access_token_key, access_token, ex=access_token_ex)

            return {
                "access_token": access_token,
                "access_token_expire_time": str(access_token_expire_time)
            }

    def delete_all_token(self, user_id, user_type=_USER_TYPE_INVEST, source=ApiTokenModel.source_type_1, reserve_refresh_token=False):
        """
        将用户所有的token都删除
        :param user_id:
        :return:
        """
        self.check_api_token_source(source)
        with self.session_scope() as session:
            # 将之前的token删除
            if reserve_refresh_token:
                session.query(ApiTokenModel).filter_by(
                    user_id=user_id,
                    user_type=user_type,
                    deleted=False,
                    token_type=self.mysql_refresh_token_key,
                ).update({
                    ApiTokenModel.deleted: True,
                    ApiTokenModel.deleted_at: datetime.datetime.now()
                })
            else:
                session.query(ApiTokenModel).filter_by(
                    user_id=user_id,
                    user_type=user_type,
                    deleted=False
                ).update({
                    ApiTokenModel.deleted: True,
                    ApiTokenModel.deleted_at: datetime.datetime.now()
                })
            session.commit()

    def generate_token(self, user_id, uuid4):
        """
        token 生成规则 = user_id + timestamp (交错穿插) + uuid(随机数)
        :param user_id:
        :param uuid4:
        :return:
        """
        user_id = str(user_id)
        timestamp = str(int(time.time()))
        token = ""
        for index in range(len(user_id) + len(timestamp)):
            if index < len(user_id):
                token += user_id[index]

            if index < len(timestamp):
                token += timestamp[index]

        return token + uuid4

    def get_access_token_by_user_id(self, user_id, user_type=_USER_TYPE_INVEST, source=ApiTokenModel.source_type_1):
        """
        内部方法,只能用于验证用户,不能返回
        通过手机号获取用户token,先查看redis中是否有.如果没有在进行数据库查询
        :param user_id: 用户user_id
        :param user_type: 用户类型
        :return:
        """
        self.check_api_token_source(source)
        access_token_key = self.make_access_token_redis_key(user_id, user_type, source)
        redis_tool = RedisTools()
        # 1.0 从redis中查取
        access_token = redis_tool.get(access_token_key)
        if access_token:
            return str(access_token, encoding='utf-8')

        # 2.0 从数据库中查取
        with self.session_scope() as session:

            if user_type == _USER_TYPE_INVEST:
                UserModel = InvestUserModel
            if user_type == _USER_TYPE_ADMIN:
                UserModel = AdminUserModel
            else:
                self.return_aes_error(10030)

            user = session.query(UserModel, ApiTokenModel.token, ApiTokenModel.expire_at, UserModel.user_id).\
                outerjoin(ApiTokenModel, UserModel.user_id == ApiTokenModel.user_id)\
                .filter(
                UserModel.user_id == user_id,
                ApiTokenModel.token_type == self.mysql_access_token_key,
                ApiTokenModel.user_type == user_type, ApiTokenModel.deleted == False,
                ApiTokenModel.source == source,
                ApiTokenModel.expire_at > datetime.datetime.now()
            ).first()

            if not user:
                self.return_aes_error(10031)

            if not user.token:
                # 用户token过期
                self.return_aes_error(10032)

            end_time = int(time.mktime(time.strptime(str(user.expire_at), '%Y-%m-%d %H:%M:%S')))
            now_time = int(time.time())
            last_time = end_time - now_time
            if last_time <= 0:
                # 将之前的token删除
                session.query(ApiTokenModel).filter_by(
                    user_id=user.user_id,
                    token_type=self.mysql_access_token_key,
                    user_type=user_type,
                    source=source,
                    deleted=False
                ).update({
                    ApiTokenModel.deleted: True,
                    ApiTokenModel.deleted_at: datetime.datetime.now()
                })
                session.commit()
                self.return_aes_error(10033)

            # 3.0将token插入到redis中, 应该是mysql的时间减去当前时间
            redis_tool.set(access_token_key, user.token, ex=last_time)
            return user.token

    def check_access_token(self, user_id, token, user_type=_USER_TYPE_INVEST, source=ApiTokenModel.source_type_1):
        """
        对比用户token是否一致
        :param user_id: 用户user_id
        :param token: token
        :return:
        """
        self.check_api_token_source(source)
        access_token = self.get_access_token_by_user_id(user_id, user_type, source)
        return access_token == token

    def refresh_token(self, user_id, refresh_token, user_type=_USER_TYPE_INVEST, source=ApiTokenModel.source_type_1):
        """
        刷新Token
        :param user_id: 用户ID
        :param refresh_token: refresh_token
        :return:
        """
        self.check_api_token_source(source)
        with self.session_scope() as session:
            refresh_token_model = session.query(ApiTokenModel).filter(
                ApiTokenModel.token == refresh_token,
                ApiTokenModel.deleted == False,
                ApiTokenModel.expire_at > datetime.datetime.now(),
                ApiTokenModel.token_type == self.mysql_refresh_token_key,
                ApiTokenModel.user_id == user_id,
                ApiTokenModel.source == source,
            ).first()
            #  如果refresh_token通过校验
            if refresh_token_model is not None:
                return self.refresh_user_access_token(user_id, user_type, source)
            else:
                self.return_aes_error(10034)

    def make_access_token_redis_key(self, user_id, user_type=_USER_TYPE_INVEST, source=ApiTokenModel.source_type_1):
        if user_type == _USER_TYPE_INVEST:
            user_type_key = 'invest'
        elif user_type == _USER_TYPE_ADMIN:
            user_type_key = 'admin'
        else:
            user_type_key = 'otherkey'
        return self.redis_access_token_key + str(user_id) + ':' + str(user_type_key) + ':' + str(source)

    def check_access_token_by_user_id(self, user_info, user_type):
        user_id = user_info.get('user_id', "")
        token = user_info.get('access_token', "")
        source = user_info.get('source', ApiTokenModel.source_type_1)
        if user_id == '' or token == '' :
            return False
        self.check_api_token_source(source)
        return self.check_access_token(user_id, token, user_type, source)

    def check_api_token_source(self, source):
        if source not in ApiTokenModel.get_all_source_type():
            self.return_aes_error(10041)


