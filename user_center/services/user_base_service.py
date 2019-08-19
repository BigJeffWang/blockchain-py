from crypto_utils import get_ecc_shared_key, generate_ecc_private_key, get_ecc_public_key_pem_from_private, \
    urandom, get_bcrypt_salt, get_ecc_private_key_pem_from_private, slow_is_equal, sha512, get_bcrypt_pwd
import time
from common_settings import *
from models.invest_user_model import InvestUserModel
from services.base_service import BaseService
from services.api_token_service import ApiTokenService
from models.admin_user_model import AdminUserModel
from models.key_salt_model import KeySaltModel
from models.borrow_user_model import BorrowUserModel
import datetime
from config import get_conf
from flask import request
from tools.redis_tools import RedisTools
from models.admin_user_module_rights_model import AdminUserModuleRightsModel
from models.admin_module_model import AdminModuleModel
import json
from config import get_transfer_to_platform_path
from tools.transfer_tools import transfer_to_platform
from services.vcode_service import VcodeService


class UserBaseService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def delete_user_key_salt(self, session, user_name, user_type, request_type=_REQUEST_TYPE_REGISTER, admin_level=0, user_source=KeySaltModel.source_type_1):
        session.query(KeySaltModel)\
            .filter(
                KeySaltModel.user_id == user_name,
                KeySaltModel.user_type == user_type,
                KeySaltModel.request_type == request_type,
                KeySaltModel.user_level == admin_level,
                KeySaltModel.source == user_source,
                KeySaltModel.deleted == False,)\
            .update({
                KeySaltModel.deleted: True,
                KeySaltModel.deleted_at: datetime.datetime.now(),
            })
        session.commit()
        return True

    def get_register_key_salt(self, user_name, client_public_key, user_type=_USER_TYPE_INVEST, admin_level=0):
        '''
        获取注册时输入的密码salt，和aes加密的服务端公钥和nonce
        :param user_name: 用户名
        :param client_public_key: 客户端公钥
        :param user_type: 用户类别
        :param admin_level: 后台用户级别
        :param user_source: 客户端类别
        :return:
        '''
        request_type = _REQUEST_TYPE_REGISTER
        # 注册时时没有uid的，所以注释掉
        # if len(user_name) == _USER_ID_LEN:
        #     # 确保，不是以正常数据的userid存入数据库的，否则可能误删无误的数据库信息
        #     self.return_aes_error(10020)

        with self.session_scope() as session:
            if user_type == _USER_TYPE_ADMIN:
                user_model = AdminUserModel
                user = session.query(user_model).filter(
                    user_model.name == user_name, user_model.level == admin_level, user_model.deleted == False
                ).first()
            elif user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                user = session.query(user_model).filter(
                    user_model.user_mobile == user_name, user_model.deleted == False).first()
            elif user_type == _USER_TYPE_BORROW:
                user_model = BorrowUserModel
                user = session.query(user_model).filter(
                    user_model.user_mobile == user_name, user_model.deleted == False).first()
            else:
                self.return_aes_error(10019)

            if user is not None:
                self.return_aes_error(30203)

            self.delete_user_key_salt(session, user_name, user_type, request_type, admin_level=admin_level)

            bcrypt_salt = get_bcrypt_salt().decode("utf-8")
            server_private_key = generate_ecc_private_key()  # 获取ECC私钥
            server_private_key_pem = get_ecc_private_key_pem_from_private(server_private_key)  # 格式化ecc私钥
            server_public_key_pem = get_ecc_public_key_pem_from_private(server_private_key)  # 获取ecc公钥
            share_key = get_ecc_shared_key(client_public_key.encode('utf-8'), server_private_key)  # 获取share-key
            nonce = urandom(12)  # 获取随机数

            # 2.0 创建salt表
            key_salt = KeySaltModel(
                user_id=user_name,
                user_type=user_type,
                user_level=admin_level,
                request_type=request_type,
                server_public_key=server_public_key_pem,
                server_private_key=server_private_key_pem,
                client_public_key=client_public_key,
                share_key=share_key,
                bcrypt_salt=bcrypt_salt,
                nonce=nonce,
            )
            session.add(key_salt)
            session.commit()

            return {
                "server_public_key": server_public_key_pem,
                "user_name": user_name,
                "bcrypt_salt": bcrypt_salt,
                "nonce": nonce,
                "time_stamp": str(int(time.time())),
            }

    def register(self, user_name, bcypt_password, level, user_type=_USER_TYPE_INVEST):
        """
        注册用户
        :param user_mobile: 注册手机号
        :param bcypt_password: 注册密码
        :param source: 终端来源 0=pc,1=wap, 2=iphone, 3=android
        :param user_type: 用户类型，投资用户或后台用户
        """

        with self.session_scope() as session:

            if user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                user = session.query(user_model).filter(user_model.user_mobile == user_name,
                                                        user_model.deleted == False, ).first()
            elif user_type == _USER_TYPE_ADMIN:
                user_model = AdminUserModel
                user = session.query(user_model).filter(user_model.name == user_name,
                                                        user_model.level == level,
                                                        user_model.deleted == False, ).first()
            elif user_type == _USER_TYPE_BORROW:
                user_model = BorrowUserModel
                user = session.query(user_model).filter(user_model.user_mobile == user_name,
                                                        user_model.deleted == False, ).first()
            else:
                self.return_aes_error(10019)

            # 1.0 判断用户是否存在,如果已经存在则用户已经注册
            if user:
                self.return_aes_error(30203)

            key_salt = session.query(KeySaltModel).filter(KeySaltModel.user_id == user_name,
                                                          KeySaltModel.user_type == user_type,
                                                          KeySaltModel.deleted == False,
                                                          KeySaltModel.request_type == _REQUEST_TYPE_REGISTER,
                                                          ).first()

            if key_salt is None:
                self.return_aes_error(10021)
            else:
                bcrypt_salt = key_salt.bcrypt_salt
            passwd_salt = urandom(12)
            password = sha512(str(bcypt_password), str(passwd_salt))

            if user_type == _USER_TYPE_INVEST:
                user = user_model(
                    user_mobile=user_name,
                    bcrypt_salt=bcrypt_salt,
                    passwd_salt=passwd_salt,
                    password=password,
                )
                session.add(user)
            elif user_type == _USER_TYPE_BORROW:
                user = user_model(
                    user_mobile=user_name,
                    bcrypt_salt=bcrypt_salt,
                    passwd_salt=passwd_salt,
                    password=password,
                )
                session.add(user)
            elif user_type == _USER_TYPE_ADMIN:
                user = user_model(
                    name=user_name,
                    bcrypt_salt=bcrypt_salt,
                    passwd_salt=passwd_salt,
                    password=password,
                    level=level,
                )
                session.add(user)

            key_salt.user_id = user.user_id
            key_salt.deleted = True
            key_salt.deleted_at = datetime.datetime.now()
            session.commit()

            return {
                "status": "true",
                "user_id": user.user_id
            }

    def get_login_key_salt(self, user_name, client_public_key, user_type=_USER_TYPE_INVEST, admin_level=0):
        """
        登录时,验证用户注册状态,并且创建key-salt
        :param user_mobile:
        :param client_public_key:
        :return:
        """
        request_type = _REQUEST_TYPE_LOGIN

        with self.session_scope() as session:
            if user_type == _USER_TYPE_ADMIN:
                user_model = AdminUserModel
                user = session.query(user_model).filter(
                    user_model.name == user_name, user_model.deleted == False, user_model.level == admin_level
                ).first()
            elif user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                user = session.query(user_model).filter(
                    user_model.user_mobile == user_name, user_model.deleted == False).first()
            elif user_type == _USER_TYPE_BORROW:
                user_model = BorrowUserModel
                user = session.query(user_model).filter(
                    user_model.user_mobile == user_name, user_model.deleted == False).first()
            else:
                self.return_aes_error(10019)

            #  1.0 判断用户是否存在
            if user is None:
                # 用户未注册
                self.return_aes_error(10045)

            #  删除之前的用户key
            self.delete_user_key_salt(session, user.user_id, user_type, request_type, admin_level=admin_level)

            bcrypt_salt = user.bcrypt_salt  # 获取密码加密密钥
            server_private_key = generate_ecc_private_key()  # 获取ECC私钥
            server_private_key_pem = get_ecc_private_key_pem_from_private(server_private_key)  # 格式化ecc私钥
            server_public_key_pem = get_ecc_public_key_pem_from_private(server_private_key)  # 获取ecc公钥
            share_key = get_ecc_shared_key(client_public_key.encode('utf-8'), server_private_key)  # 获取share-key
            nonce = urandom(12)  # 获取随机数

            # 2.0 创建salt表
            key_salt = KeySaltModel(
                user_id=user.user_id,
                user_type=user_type,
                user_level=admin_level,
                request_type=request_type,
                server_public_key=server_public_key_pem,
                server_private_key=server_private_key_pem,
                client_public_key=client_public_key,
                share_key=share_key,
                bcrypt_salt=bcrypt_salt,
                nonce=nonce,
            )
            session.add(key_salt)
            session.commit()

            return {
                "server_public_key": server_public_key_pem,
                "user_name": user_name,
                "bcrypt_salt": bcrypt_salt,
                "nonce": nonce,
                "time_stamp": str(int(time.time()))
            }

    def login(self, user_name, bcypt_password, user_type=_USER_TYPE_INVEST, admin_level=0):
        """
        用户登录
        :param user_mobile: 手机号
        :param bcypt_password: 密码
        :return:
        """
        with self.session_scope() as session:

            if user_type == _USER_TYPE_ADMIN:
                user_model = AdminUserModel
                user = session.query(user_model).filter(user_model.name == user_name,
                                                        user_model.level == admin_level,
                                                        user_model.deleted == False, ).first()
            elif user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                user = session.query(user_model).filter(user_model.user_mobile == user_name,
                                                        user_model.deleted == False, ).first()
            elif user_type == _USER_TYPE_BORROW:
                user_model = BorrowUserModel
                user = session.query(user_model).filter(user_model.user_mobile == user_name,
                                                        user_model.deleted == False, ).first()
            else:
                self.return_aes_error(10019)

            #  1.0 获取用户
            if not user:
                self.return_aes_error(30209)

            #  2.0 对比用户密码
            result = slow_is_equal(user.password, sha512(str(bcypt_password), str(user.passwd_salt)))
            if not result:
                self.return_aes_error(30210)

            #  3.0 生成Token
            r = ApiTokenService().generator_user_tokens(user.user_id, user_type=user_type)
            return r

    def get_user_info_by_id(self, user_id, user_type=_USER_TYPE_INVEST, without_delete=True, admin_level=0):
        with self.session_scope() as session:
            if user_type == _USER_TYPE_ADMIN:
                user_model = AdminUserModel
                if without_delete:
                    user = session.query(user_model).filter(user_model.user_id == user_id,
                                                            user_model.level == admin_level,
                                                            user_model.deleted == False, ).first()
                else:
                    user = session.query(user_model).filter(user_model.user_id == user_id).first()
                if user is None:
                    self.return_aes_error(10038)
                return {
                    'user_id': user.user_id,
                    'user_name': user.name,
                    'level': user.level,
                }
            elif user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                if without_delete:
                    user = session.query(user_model).filter(user_model.user_id == user_id,
                                                            user_model.deleted == False, ).first()
                else:
                    user = session.query(user_model).filter(user_model.user_id == user_id).first()
                if user is None:
                    self.return_aes_error(10038)
                return {
                    'user_id': user.user_id,
                    'user_mobile': user.user_mobile,
                    'option1': user.option1,
                    # 'status': user.status,
                    # 'id_card': user.id_card,
                    # 'real_name': user.real_name,
                    'email': user.email,
                    'password': '******' if user.password else '',
                    # 'transaction_password': '******' if user.transaction_password else '',
                    'nick_name': user.nick_name if user.nick_name else '',
                }
            elif user_type == _USER_TYPE_BORROW:
                user_model = BorrowUserModel
                if without_delete:
                    user = session.query(user_model).filter(user_model.user_id == user_id,
                                                            user_model.deleted == False, ).first()
                else:
                    user = session.query(user_model).filter(user_model.user_id == user_id).first()
                if user is None:
                    self.return_aes_error(10038)
                return {
                    'user_id': user.user_id,
                    'user_mobile': user.user_mobile,
                    'option1': user.option1,
                    'status': user.status,
                    'id_card': user.id_card,
                    'real_name': user.real_name,
                }
            else:
                self.return_aes_error(10019)

    def reset_login_password(self, user_id, password, user_type=_USER_TYPE_ADMIN, admin_level=0):
        """
        重置登录密码
        :param user_mobile: user_mobile
        :param password: 新密码
        :param user_type: 用户类型
        :return:
        """
        with self.session_scope() as session:
            if user_type == _USER_TYPE_INVEST:
                q = session.query(InvestUserModel).filter_by(user_mobile=user_id, deleted=False).first()
            elif user_type == _USER_TYPE_ADMIN:
                q = session.query(AdminUserModel).filter_by(
                    user_id=user_id, deleted=False, level=admin_level,
                ).first()
            else:
                self.return_aes_error(10019)

            if q is None:
                self.return_aes_error(30213)

            q.password = sha512(str(password), str(q.passwd_salt))
            session.commit()
            return {
                "status": "true"
            }

    def change_login_password(self, user_id, old_password, new_password, user_type=_USER_TYPE_INVEST):
        """
        修改登录密码
        :param user_id: user_id
        :param old_password: 旧密码
        :param new_password: 新密码
        :param user_type: 用户类型
        :return:
        """
        with self.session_scope() as session:
            if user_type == _USER_TYPE_INVEST:
                q = session.query(InvestUserModel).filter_by(user_id=user_id, deleted=False).first()
            elif user_type == _USER_TYPE_BORROW:
                q = session.query(BorrowUserModel).filter_by(user_id=user_id, deleted=False).first()
            else:
                self.return_aes_error(10019)

            if q is None:
                self.return_aes_error(30213)

            result = slow_is_equal(q.password, sha512(str(old_password), str(q.passwd_salt)))
            if not result:
                self.return_aes_error(30212)
            q.password = sha512(new_password, q.passwd_salt)
            session.commit()
            return {
                "status": "true"
            }

    def update_user_info_by_id(self, argument_dict, user_type=_USER_TYPE_INVEST):
        user_id = argument_dict['user_id']
        with self.session_scope() as session:
            if user_type == _USER_TYPE_ADMIN:
                user_model = AdminUserModel
                user = session.query(user_model).filter(user_model.user_id == user_id).first()
                if user is None:
                    self.return_aes_error(10038)
                return {
                    'user_id': user.user_id,
                    'user_name': user.name,
                    'level': user.level,
                }
            elif user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                user = session.query(user_model).filter(user_model.user_id == user_id).first()
                if user is None:
                    self.return_aes_error(10038)
                if 'id_card' in argument_dict:
                    user.id_card = argument_dict['id_card']
                if 'real_name' in argument_dict:
                    user.real_name = argument_dict['real_name']
                session.commit()
                return {
                    'user_id': user.user_id,
                    'user_mobile': user.user_mobile,
                    'option1': user.option1,
                    'status': user.status,
                    'id_card': user.id_card,
                    'real_name': user.real_name,
                }
            elif user_type == _USER_TYPE_BORROW:
                user_model = BorrowUserModel
                user = session.query(user_model).filter(user_model.user_id == user_id).first()
                if user is None:
                    self.return_aes_error(10038)
                if 'id_card' in argument_dict:
                    user.id_card = argument_dict['id_card']
                if 'real_name' in argument_dict:
                    user.real_name = argument_dict['real_name']
                session.commit()
                return {
                    'user_id': user.user_id,
                    'user_mobile': user.user_mobile,
                    'option1': user.option1,
                    'status': user.status,
                    'id_card': user.id_card,
                    'real_name': user.real_name,
                }
            else:
                self.return_aes_error(10019)

    def register_on(self, user_mobile):
        """
        将注册用户的状态改为已创建账户
        :param user_mobile:
        :return:
        """
        with self.session_scope() as session:
            user_model = InvestUserModel
            user = session.query(user_model).filter(user_model.user_mobile == user_mobile,
                                                    user_model.deleted == False, ).first()

            if not user:
                self.return_aes_error(30202)
            user.status = InvestUserModel.status_on
            session.commit()
            return {
                "status": "true",
            }

    def get_register_key_salt_by_type(self, user_name, client_public_key, register_by, user_type=_USER_TYPE_INVEST,
                                      user_source=None, mobile_country_code=None):
        '''
        获取注册时输入的密码salt，和aes加密的服务端公钥和nonce
        :param user_name: 用户名
        :param client_public_key: 客户端公钥
        :param register_by: 注册所用字段
        :param user_type: 用户类别
        :param user_source: 客户端类别
        :param mobile_country_code: 客户端注册使用的用户名类型
        :return:
        '''

        request_type = _REQUEST_TYPE_REGISTER
        self.check_source(register_by, user_source)

        with self.session_scope() as session:
            if user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                if register_by == _REGISTER_BY_MOBILE:
                    if mobile_country_code is None or mobile_country_code == '':
                        self.return_aes_error(30217)
                    user = session.query(user_model).filter(
                        user_model.user_mobile == user_name,
                        user_model.mobile_country_code == mobile_country_code,
                        user_model.deleted == False,
                    ).first()
                elif register_by == _REGISTER_BY_EMAIL:
                    user = session.query(user_model).filter(
                        user_model.email == user_name,
                        user_model.deleted == False,
                    ).first()
                else:
                    self.return_aes_error(30215)
            else:
                self.return_aes_error(10019)

            if user is not None:
                self.return_aes_error(30203)

            self.delete_user_key_salt(session, user_name, user_type, request_type, user_source=user_source)
            bcrypt_salt = get_bcrypt_salt().decode("utf-8")
            server_private_key = generate_ecc_private_key()  # 获取ECC私钥
            server_private_key_pem = get_ecc_private_key_pem_from_private(server_private_key)  # 格式化ecc私钥
            server_public_key_pem = get_ecc_public_key_pem_from_private(server_private_key)  # 获取ecc公钥
            share_key = get_ecc_shared_key(client_public_key.encode('utf-8'), server_private_key)  # 获取share-key
            nonce = urandom(12)  # 获取随机数

            # 2.0 创建salt表
            key_salt = KeySaltModel(
                user_id=user_name,
                user_type=user_type,
                request_type=request_type,
                server_public_key=server_public_key_pem,
                server_private_key=server_private_key_pem,
                client_public_key=client_public_key,
                share_key=share_key,
                bcrypt_salt=bcrypt_salt,
                nonce=nonce,
                source=user_source,
            )
            session.add(key_salt)
            session.commit()

            return {
                "server_public_key": server_public_key_pem,
                "user_name": user_name,
                "bcrypt_salt": bcrypt_salt,
                "nonce": nonce,
                "time_stamp": str(int(time.time())),
            }

    def register_by_type(self, user_name, bcypt_password, user_type=_USER_TYPE_INVEST, source=None, register_by=None,
                         mobile_country_code=None, db_user_name=None, change_key_nonce=False):
        """
        根据注册字段注册用户
        :param user_name: 注册字段
        :param bcypt_password: 注册密码
        :param source: 终端来源 0=pc,1=wap, 2=iphone, 3=android
        :param user_type: 用户类型，投资用户或后台用户
        :param register_by: 注册字段含义
        :param mobile_country_code: 手机号所属国区号
        :param db_user_name: 数据库存储的username字段
        :param change_key_nonce: 是否吧注册时的key和nonce改为登陆后使用的key和nonce
        """
        self.check_source(register_by, source)

        with self.session_scope() as session:

            if user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                if register_by == _REGISTER_BY_MOBILE:
                    if mobile_country_code is None or mobile_country_code == '':
                        self.return_aes_error(30217)
                    user = session.query(user_model).filter(
                        user_model.user_mobile == user_name,
                        user_model.mobile_country_code == mobile_country_code,
                        user_model.deleted == False,
                    ).first()
                    db_user_name = user_name
                elif register_by == _REGISTER_BY_EMAIL:
                    user = session.query(user_model).filter(
                        user_model.email == user_name,
                        user_model.deleted == False,
                    ).first()
                    db_user_name = user_name
                else:
                    self.return_aes_error(30215)
            else:
                self.return_aes_error(10019)

            # 1.0 判断用户是否存在,如果已经存在则用户已经注册
            if user:
                self.return_aes_error(30203)

            key_salt = session.query(KeySaltModel).filter(
                KeySaltModel.user_id == user_name,
                KeySaltModel.user_type == user_type,
                KeySaltModel.deleted == False,
                KeySaltModel.request_type == _REQUEST_TYPE_REGISTER,
                KeySaltModel.source == source,
            ).first()

            if key_salt is None:
                self.return_aes_error(10021)
            else:
                bcrypt_salt = key_salt.bcrypt_salt
            passwd_salt = urandom(12)
            password = sha512(str(bcypt_password), str(passwd_salt))

            if user_type == _USER_TYPE_INVEST:
                nick_name = self.get_nick_name(user_model, session)
                ip = request.remote_addr
                if register_by == _REGISTER_BY_MOBILE:
                    user = user_model(
                        user_mobile=user_name,
                        bcrypt_salt=bcrypt_salt,
                        passwd_salt=passwd_salt,
                        password=password,
                        mobile_country_code=mobile_country_code,
                        register_ip=ip,
                        status=user_model.status_on,
                        nick_name=nick_name,
                        user_name=db_user_name,
                    )
                    user.email = user.user_id
                    session.add(user)
                elif register_by == _REGISTER_BY_EMAIL:
                    user = user_model(
                        email=user_name,
                        bcrypt_salt=bcrypt_salt,
                        passwd_salt=passwd_salt,
                        password=password,
                        register_ip=ip,
                        status=user_model.status_on,
                        nick_name=nick_name,
                        user_name=db_user_name,
                    )
                    user.user_mobile = user.user_id
                    session.add(user)

            key_salt.user_id = user.user_id
            if change_key_nonce:
                key_salt.request_type = _REQUEST_TYPE_LOGIN
            else:
                key_salt.deleted = True
                key_salt.deleted_at = datetime.datetime.now()

            # 获取对于平台的注册支持
            transfer_url = get_transfer_to_platform_path("invest", "register")
            if transfer_url != '' and user_type == _USER_TYPE_INVEST:
                account_response_dict = transfer_to_platform(transfer_url, data={
                    "user_id": user.user_id,
                    "nick_name": user.nick_name,
                    "user_mobile": user.user_mobile if user.user_mobile != user.user_id else '',
                    "mobile_country_code": user.user_mobile if user.user_mobile != user.user_id else '',
                    "email": user.email if user.email != user.user_id else '',
                    "user_name": user.user_name,
                    "register_source": source,
                    "register_ip": ip,
                })
                if ("code" not in account_response_dict) or ("data" not in account_response_dict) or ("msg" not in account_response_dict):
                    self.return_aes_error(30202)
                if account_response_dict['code'] != '00000':
                    self.return_aes_error(account_response_dict['code'], account_response_dict['msg'])
            session.commit()

            return {
                "status": "true",
                "user_id": user.user_id
            }

    def register_on_by_type(self, user_mobile, source=None, register_by=None, mobile_country_code=None):
        """
        将注册用户的状态改为已创建账户
        :param user_mobile:
        :return:
        """
        self.check_source(register_by, source)

        with self.session_scope() as session:
            user_model = InvestUserModel

            if register_by == _REGISTER_BY_MOBILE:
                if mobile_country_code is None or mobile_country_code == '':
                    self.return_aes_error(30217)
                user = session.query(user_model).filter(
                    user_model.user_mobile == user_mobile,
                    user_model.mobile_country_code == mobile_country_code,
                    user_model.deleted == False,
                ).first()
            elif register_by == _REGISTER_BY_EMAIL:
                user = session.query(user_model).filter(
                    user_model.email == user_mobile,
                    user_model.deleted == False,
                ).first()
            else:
                self.return_aes_error(30215)

            if not user:
                self.return_aes_error(30202)
            user.status = InvestUserModel.status_on
            session.commit()
            return {
                "status": "true",
            }

    def login_by_type(self, user_name, bcypt_password, user_type=_USER_TYPE_INVEST, source=None,
                      register_by=None, mobile_country_code=None, check_fail_times=True):
        """
        用户登录
        :param user_mobile: 手机号
        :param bcypt_password: 密码
        :return:
        """
        self.check_source(register_by, source)

        with self.session_scope() as session:
            if user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel

                if register_by == _REGISTER_BY_MOBILE:
                    if mobile_country_code is None or mobile_country_code == '':
                        self.return_aes_error(30217)
                    user = session.query(user_model).filter(
                        user_model.user_mobile == user_name,
                        user_model.mobile_country_code == mobile_country_code,
                        user_model.deleted == False,
                        user_model.status_on == user_model.status_on,
                    ).first()
                elif register_by == _REGISTER_BY_EMAIL:
                    user = session.query(user_model).filter(
                        user_model.email == user_name,
                        user_model.deleted == False,
                        user_model.status_on == user_model.status_on,
                    ).first()
                elif register_by == _LOGININ_BY_USER_NAME:
                    user = session.query(user_model).filter(
                        user_model.user_name == user_name,
                        user_model.deleted == False,
                        user_model.status_on == user_model.status_on,
                    ).first()
                else:
                    self.return_aes_error(30215)
            else:
                self.return_aes_error(10019)

            #  1.0 获取用户
            if not user:
                self.return_aes_error(30209)

            if check_fail_times:
                redis_tool = RedisTools()
                redis_key = self.make_login_fail_times_key(user.user_id, user_type)
                fail_times = redis_tool.get(redis_key)
                if fail_times:
                    fail_times = int(fail_times)
                    if fail_times > _LOGIN_FAIL_TIMES_LIMIT:
                        self.return_aes_error(30226)

            #  2.0 对比用户密码
            result = slow_is_equal(user.password, sha512(str(bcypt_password), str(user.passwd_salt)))
            if not result:
                if check_fail_times:
                    if not fail_times:
                        redis_tool.set(redis_key, 1, ex=_LOGIN_FAIL_TIME_LIMIT)
                    else:
                        redis_tool.incr(redis_key)
                self.return_aes_error(30210)

            #  3.0 生成Token
            r = ApiTokenService().\
                generator_user_tokens(user.user_id, user_type=user_type, source=source)

            # 获取对于平台的注册支持
            transfer_url = get_transfer_to_platform_path("invest", "login")
            if transfer_url != '' and user_type == _USER_TYPE_INVEST:
                ip = request.remote_addr
                account_response_dict = transfer_to_platform(transfer_url, data={
                    "user_id": user.user_id,
                    "source": source,
                    "login_ip": ip,
                })
                if ("code" not in account_response_dict) or ("data" not in account_response_dict) or ("msg" not in account_response_dict):
                    self.return_aes_error(30202)
                if account_response_dict['code'] != '00000':
                    self.return_aes_error(account_response_dict['code'], account_response_dict['msg'])

            return r

    def get_login_key_salt_by_type(self, user_name, client_public_key, user_type=_USER_TYPE_INVEST, source=None,
                                   register_by=None, mobile_country_code=None, admin_level=0):
        """
        登录时,验证用户注册状态,并且创建key-salt
        :param user_mobile:
        :param client_public_key:
        :return:
        """
        request_type = _REQUEST_TYPE_LOGIN

        self.check_source(register_by, source)

        with self.session_scope() as session:
            if user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel

                if register_by == _REGISTER_BY_MOBILE:
                    if mobile_country_code is None or mobile_country_code == '':
                        self.return_aes_error(30217)
                    user = session.query(user_model).filter(
                        user_model.user_mobile == user_name,
                        user_model.mobile_country_code == mobile_country_code,
                        user_model.deleted == False,
                    ).first()
                elif register_by == _REGISTER_BY_EMAIL:
                    user = session.query(user_model).filter(
                        user_model.email == user_name,
                        user_model.deleted == False,
                    ).first()
                elif register_by == _LOGININ_BY_USER_NAME:
                    user = session.query(user_model).filter(
                        user_model.user_name == user_name,
                        user_model.deleted == False,
                    ).first()
                else:
                    self.return_aes_error(30215)
            else:
                self.return_aes_error(10019)

            #  1.0 判断用户是否存在
            if user is None:
                # 用户未注册
                self.return_aes_error(10045)

            #  删除之前的用户key
            self.delete_user_key_salt(session, user.user_id, user_type, request_type, user_source=source,
                                      admin_level=admin_level)

            bcrypt_salt = user.bcrypt_salt  # 获取密码加密密钥
            server_private_key = generate_ecc_private_key()  # 获取ECC私钥
            server_private_key_pem = get_ecc_private_key_pem_from_private(server_private_key)  # 格式化ecc私钥
            server_public_key_pem = get_ecc_public_key_pem_from_private(server_private_key)  # 获取ecc公钥
            share_key = get_ecc_shared_key(client_public_key.encode('utf-8'), server_private_key)  # 获取share-key
            nonce = urandom(12)  # 获取随机数

            # 2.0 创建salt表
            key_salt = KeySaltModel(
                user_id=user.user_id,
                user_type=user_type,
                user_level=admin_level,
                request_type=request_type,
                server_public_key=server_public_key_pem,
                server_private_key=server_private_key_pem,
                client_public_key=client_public_key,
                share_key=share_key,
                bcrypt_salt=bcrypt_salt,
                nonce=nonce,
                source=source,
            )
            session.add(key_salt)
            session.commit()

            return {
                "server_public_key": server_public_key_pem,
                "user_name": user_name,
                "bcrypt_salt": bcrypt_salt,
                "nonce": nonce,
                "time_stamp": str(int(time.time()))
            }

    def get_pay_salt(self, user_id, user_type=_USER_TYPE_INVEST):
        with self.session_scope() as session:
            if user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                user = session.query(user_model).filter(
                    user_model.user_id == user_id,
                    user_model.deleted == False,
                ).first()
            else:
                self.return_aes_error(10019)

            #  1.0 判断用户是否存在
            if user is None:
                # 用户未注册
                self.return_aes_error(10045)

            transfer_url = get_transfer_to_platform_path("invest", "get_pay_salt")
            if transfer_url != '':
                account_response_dict = transfer_to_platform(transfer_url, data={
                    "user_id": user.user_id,
                })
                if ("code" not in account_response_dict) or ("data" not in account_response_dict) or ("msg" not in account_response_dict):
                    self.return_aes_error(30202)
                if account_response_dict['code'] != '00000':
                    self.return_aes_error(account_response_dict['code'], account_response_dict['msg'])
                transaction_bcrypt_salt = account_response_dict['data']['bcrypt_salt']
            else:
                if not user.transaction_bcrypt_salt:
                    user.transaction_bcrypt_salt = get_bcrypt_salt().decode("utf-8")
                    session.commit()
                transaction_bcrypt_salt = user.transaction_bcrypt_salt
            return {
                'bcrypt_salt': transaction_bcrypt_salt,
            }

    def real_name_authentication(self, user_id, mobile_country_code, email, user_mobile, login_password, pay_password,
                                 user_type=_USER_TYPE_INVEST):
        """
        实名认证
        :param user_mobile: user_mobile
        :param real_name: 用户姓名
        :param id_card: 身份证号
        :param bank_card_id: 银行卡号
        :return:
        """
        with self.session_scope() as session:

            if user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                user = session.query(user_model).filter(
                    user_model.user_id == user_id,
                    user_model.deleted == False,
                    user_model.authentication_status == user_model.authentication_status_off,
                ).first()
            else:
                self.return_aes_error(10019)

            if user is None:
                # 用户未注册
                self.return_aes_error(10045)

            if slow_is_equal(user.password, sha512(str(login_password), str(user.passwd_salt))):
                self.return_aes_error(30224)

            # 更新数据
            if user.mobile_country_code is None or user.mobile_country_code == '':
                user.mobile_country_code = mobile_country_code

            if user.email == user_id or user.email is None or user.email == '':
                self.check_email(email)
                user.email = email

            if user.user_mobile == user_id or user.user_mobile is None or user.user_mobile == '':
                self.check_mobile_all(user_mobile)
                user.user_mobile = user_mobile

            if not user.transaction_passwd_salt:
                user.transaction_passwd_salt = urandom(12)

            if user.transaction_password is None or user.transaction_password == '':
                user.transaction_password = sha512(str(pay_password), str(user.transaction_passwd_salt))

            # 校验缺失数据
            if not user.mobile_country_code or not user.email or not user.user_mobile or not user.transaction_passwd_salt \
                    or not user.transaction_password:
                self.return_aes_error(30220)
            user.authentication_status = user_model.authentication_status_on

            session.commit()
            return {
                "status": "true"
            }

    def reset_pay_password(self, user_id, user_mobile, pay_password, user_type=_USER_TYPE_INVEST):
        """
        修改支付密码
        :param user_mobile: user_mobile
        :param real_name: 用户姓名
        :param id_card: 身份证号
        :param bank_card_id: 银行卡号
        :return:
        """
        with self.session_scope() as session:

            if user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                user = session.query(user_model).filter(
                    user_model.user_id == user_id,
                    user_model.deleted == False,
                ).first()
            else:
                self.return_aes_error(10019)

            if user is None:
                # 用户未注册
                self.return_aes_error(10045)

            transfer_url = get_transfer_to_platform_path("invest", "reset_pay_password")
            if transfer_url != '':
                account_response_dict = transfer_to_platform(transfer_url, data={
                    "user_id": user.user_id,
                    'password': pay_password,
                })
                if ("code" not in account_response_dict) or ("data" not in account_response_dict) or ("msg" not in account_response_dict):
                    self.return_aes_error(30202)
                if account_response_dict['code'] != '00000':
                    self.return_aes_error(account_response_dict['code'], account_response_dict['msg'])
            else:
                self.return_aes_error(30234)

            session.commit()
            return {
                "status": "true"
            }

    def set_mobile(self, user_id, mobile_country_code, user_mobile, user_type=_USER_TYPE_INVEST):
        """
        设置手机号
        :param user_id:
        :param mobile_country_code: 手机号国家区号
        :param user_mobile:
        :param user_type:
        :return:
        """
        with self.session_scope() as session:

            if user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                user = session.query(user_model).filter(
                    user_model.user_id == user_id,
                    user_model.deleted == False,
                ).first()
            else:
                self.return_aes_error(10019)

            if user is None:
                # 用户未注册
                self.return_aes_error(10045)

            # 更新数据
            user.user_mobile = user_mobile
            user.mobile_country_code = mobile_country_code

            # 获取对于平台的注册支持
            transfer_url = get_transfer_to_platform_path("invest", "set_user_mobile")
            if transfer_url != '':
                account_response_dict = transfer_to_platform(transfer_url, data={
                    "user_id": user.user_id,
                    "user_mobile": user.user_mobile ,
                    "mobile_country_code": user.mobile_country_code,
                })
                if ("code" not in account_response_dict) or ("data" not in account_response_dict) or ("msg" not in account_response_dict):
                    self.return_aes_error(30235)
                if account_response_dict['code'] != '00000':
                    self.return_aes_error(account_response_dict['code'], account_response_dict['msg'])


            # 校验缺失数据
            if user.mobile_country_code and user.email and user.user_mobile and user.transaction_passwd_salt \
                    and user.transaction_password:
                user.authentication_status = user_model.authentication_status_on

            session.commit()
            return {
                "status": "true"
            }

    def set_email(self, user_id, email, user_type=_USER_TYPE_INVEST):
        """
        设置email
        :param user_id:
        :param email:
        :param user_type:
        :return:
        """
        with self.session_scope() as session:

            if user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                user = session.query(user_model).filter(
                    user_model.user_id == user_id,
                    user_model.deleted == False,
                ).first()
            else:
                self.return_aes_error(10019)

            if user is None:
                # 用户未注册
                self.return_aes_error(10045)

            # 更新数据
            user.email = email

            # 获取对于平台的注册支持
            transfer_url = get_transfer_to_platform_path("invest", "set_email")
            if transfer_url != '':
                account_response_dict = transfer_to_platform(transfer_url, data={
                    "user_id": user.user_id,
                    "email": user.email,
                })
                if ("code" not in account_response_dict) or ("data" not in account_response_dict) or ("msg" not in account_response_dict):
                    self.return_aes_error(30236)
                if account_response_dict['code'] != '00000':
                    self.return_aes_error(account_response_dict['code'], account_response_dict['msg'])

            # 校验缺失数据
            if user.mobile_country_code and user.email and user.user_mobile and user.transaction_passwd_salt \
                    and user.transaction_password:
                user.authentication_status = user_model.authentication_status_on

            session.commit()
            return {
                "status": "true"
            }

    def set_nick_name(self, user_id, nick_name, user_type=_USER_TYPE_INVEST):
        """
        设置昵称
        :param user_id:
        :param nick_name:
        :param user_type:
        :return:
        """
        with self.session_scope() as session:

            if user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                user = session.query(user_model).filter(
                    user_model.user_id == user_id,
                    user_model.deleted == False,
                ).first()
            else:
                self.return_aes_error(10019)

            if user is None:
                # 用户未注册
                self.return_aes_error(10045)

            if self.check_nick_name(user_model, nick_name, session):
                self.return_aes_error(10047)

            # 更新数据
            user.nick_name = nick_name

            # 校验缺失数据
            if user.mobile_country_code and user.email and user.user_mobile and user.transaction_passwd_salt \
                    and user.transaction_password:
                user.authentication_status = user_model.authentication_status_on

            transfer_url = get_transfer_to_platform_path("invest", "set_nick_name")
            if transfer_url != '':
                account_response_dict = transfer_to_platform(transfer_url, data={
                    "user_id": user.user_id,
                    'nick_name': nick_name,
                })
                if ("code" not in account_response_dict) or ("data" not in account_response_dict) or ("msg" not in account_response_dict):
                    self.return_aes_error(30202)
                if account_response_dict['code'] != '00000':
                    self.return_aes_error(account_response_dict['code'], account_response_dict['msg'])

            session.commit()
            return {
                "status": "true"
            }

    def set_avatar(self, user_id, avatar, user_type=_USER_TYPE_INVEST):
        """
        设置头像
        :param user_id:
        :param avatar: 头像地址
        :param user_type:
        :return:
        """
        with self.session_scope() as session:

            if user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                user = session.query(user_model).filter(
                    user_model.user_id == user_id,
                    user_model.deleted == False,
                    user_model.status == user_model.status_on,
                ).first()
            else:
                self.return_aes_error(10019)

            if user is None:
                # 用户未注册
                self.return_aes_error(10045)

            # 更新数据
            user.avatar = avatar

            # 校验缺失数据
            if user.mobile_country_code and user.email and user.user_mobile and user.transaction_passwd_salt \
                    and user.transaction_password:
                user.authentication_status = user_model.authentication_status_on

            transfer_url = get_transfer_to_platform_path("invest", "set_avatar")
            if transfer_url != '':
                account_response_dict = transfer_to_platform(transfer_url, data={
                    "user_id": user.user_id,
                    'avatar': avatar,
                })
                if ("code" not in account_response_dict) or ("data" not in account_response_dict) or ("msg" not in account_response_dict):
                    self.return_aes_error(30202)
                if account_response_dict['code'] != '00000':
                    self.return_aes_error(account_response_dict['code'], account_response_dict['msg'])

            session.commit()
            return {
                "status": "true"
            }

    def set_pay_password(self, user_id, login_password, pay_password, user_type=_USER_TYPE_INVEST):
        """
        设置支付密码
        :param user_id:
        :param login_password: 按照登陆salt加密规则加密的支付密码，用于校验支付密码与交易密码是否相同
        :param pay_password: 支付密码
        :param user_type:
        :return:
        """
        with self.session_scope() as session:

            if user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                user = session.query(user_model).filter(
                    user_model.user_id == user_id,
                    user_model.deleted == False,
                ).first()
            else:
                self.return_aes_error(10019)

            if user is None:
                # 用户未注册
                self.return_aes_error(30209)

            if slow_is_equal(user.password, sha512(str(login_password), str(user.passwd_salt))):
                self.return_aes_error(30224)

            # 更新数据

            transfer_url = get_transfer_to_platform_path("invest", "set_pay_password")
            if transfer_url != '':
                account_response_dict = transfer_to_platform(transfer_url, data={
                    "user_id": user.user_id,
                    'password': pay_password,
                })
                if ("code" not in account_response_dict) or ("data" not in account_response_dict) or ("msg" not in account_response_dict):
                    self.return_aes_error(30202)
                if account_response_dict['code'] != '00000':
                    self.return_aes_error(account_response_dict['code'], account_response_dict['msg'])
            else:
                self.return_aes_error(30234)

            # 校验缺失数据
            if user.mobile_country_code and user.email and user.user_mobile and user.transaction_passwd_salt \
                    and user.transaction_password:
                user.authentication_status = user_model.authentication_status_on

            session.commit()
            return {
                "status": "true"
            }

    def make_login_fail_times_key(self, user_id, user_type):
        return str('countloginfailtimes') + ':' + str(user_id) + ':' + str(user_type)

    def make_paypwd_fail_times_key(self, user_id, user_type):
        return str('countpaypwdfailtimes') + ':' + str(user_id) + ':' + str(user_type)

    def add_user_msg_to_platform(self, argument_dict, check_pay_pwd=False, user_type=_USER_TYPE_INVEST, add_msg=[]):
        """
        # 本项目与其他平台交互时，增加到数据
        :param argument_dict: 客户端所传参数
        :param check_pay_pwd: 是否校验支付密码
        :param user_type: 用户类型
        :param add_msg: 需要增加到数据
        :return:
        """
        if 'user_id' not in argument_dict:
            self.return_aes_error(30213)
        with self.session_scope() as session:
            if user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                user = session.query(user_model).filter(
                    user_model.user_id == argument_dict['user_id'],
                    user_model.deleted == False,
                    user_model.status == user_model.status_on,
                ).first()
            else:
                self.return_aes_error(10019)

            if user is None:
                # 用户未注册
                self.return_aes_error(30209)

            if check_pay_pwd:
                if 'pay_password' not in argument_dict:
                    self.return_aes_error(30227)
                redis_tool = RedisTools()
                redis_key = self.make_paypwd_fail_times_key(user.user_id, user_type)
                fail_times = redis_tool.get(redis_key)
                if fail_times:
                    fail_times = int(fail_times)
                    if fail_times > _PAYPWD_FAIL_TIMES_LIMIT:
                        self.return_aes_error(30228)

                if not user.transaction_passwd_salt or not user.transaction_password:
                    self.return_aes_error(30229)

                #  2.0 对比用户密码
                result = slow_is_equal(user.transaction_password, sha512(str(argument_dict['pay_password']), str(user.transaction_passwd_salt)))
                if not result:
                    if not fail_times:
                        redis_tool.set(redis_key, 1, ex=_PAYPWD_FAIL_TIME_LIMIT)
                    else:
                        redis_tool.set(redis_key, int(fail_times) + 1, ex=_PAYPWD_FAIL_TIME_LIMIT)
                    self.return_aes_error(30227)

            if add_msg != []:
                for i in add_msg:
                    argument_dict[i] = getattr(user, i, "")
            return True

    def reset_login_password_by_type(self, user_mobile, password, user_type=_USER_TYPE_INVEST, register_by=_REGISTER_BY_MOBILE,
                                     mobile_country_code=None, admin_level=0):
        """
        重置登录密码
        :param user_mobile: user_mobile
        :param password: 新密码
        :param user_type: 用户类型
        :return:
        """
        with self.session_scope() as session:
            if user_type == _USER_TYPE_INVEST:
                if register_by in [_REGISTER_BY_MOBILE, _RESET_PWD_MOBILE]:
                    q = session.query(InvestUserModel).filter_by(
                        user_mobile=user_mobile,
                        deleted=False,
                        mobile_country_code=mobile_country_code,
                        status=InvestUserModel.status_on,
                    ).first()
                elif register_by in [_REGISTER_BY_EMAIL, _RESET_PWD_EMAIL]:
                    q = session.query(InvestUserModel).filter_by(
                        email=user_mobile,
                        deleted=False,
                        status=InvestUserModel.status_on,
                    ).first()
                else:
                    self.return_aes_error(10020)
            else:
                self.return_aes_error(10020)

            if q is None:
                self.return_aes_error(30213)

            if user_type == _USER_TYPE_INVEST:
                if register_by in [_REGISTER_BY_MOBILE, _RESET_PWD_MOBILE] and q.user_mobile == q.user_id:
                    self.return_aes_error(10020)
                elif register_by in [_REGISTER_BY_EMAIL, _RESET_PWD_EMAIL] and q.email == q.user_id:
                    self.return_aes_error(10020)

            q.password = sha512(str(password), str(q.passwd_salt))
            session.commit()
            return {
                "status": "true"
            }

    def register_by_admin(self, user_id, user_name, password, rights_list):
        """
        后台root用户添加用户
        :param user_id:
        :param user_name: 用户名
        :param password: 密码
        :param rights_list: 权限列表，形如：[{'module_id': 1}, {'module_id': 2}]
        :return:
        """
        if not password:
            self.return_aes_error(30233)
        with self.session_scope() as session:

            user_model = AdminUserModel
            self.check_admin_level(session, user_id, user_model)

            one_user = session.query(user_model).filter(
                user_model.name == user_name,
                user_model.deleted == False,
            ).first()

            # 2.0 判断用户是否存在,如果已经存在则用户已经注册
            if one_user:
                self.return_aes_error(30203)

            bcrypt_salt = get_bcrypt_salt().decode("utf-8")
            bcypt_password = get_bcrypt_pwd(password, bcrypt_salt)
            passwd_salt = urandom(12)
            db_password = sha512(str(bcypt_password), str(passwd_salt))

            new_user = user_model(
                name=user_name,
                bcrypt_salt=bcrypt_salt,
                passwd_salt=passwd_salt,
                password=db_password,
                level=_BASE_ADMIN_LEVEL,
            )
            session.add(new_user)

            self.delete_all_user_rights(session, new_user.user_id)
            self.add_user_rights(session, new_user.user_id, rights_list)

            session.commit()

            return {
                "user_name": new_user.name
            }

    def delete_all_user_rights(self, session, user_id):
        session.query(AdminUserModuleRightsModel).filter(
            AdminUserModuleRightsModel.user_id == user_id,
            AdminUserModuleRightsModel.deleted == False,
        ).with_for_update().update({
            AdminUserModuleRightsModel.deleted: True,
            AdminUserModuleRightsModel.deleted_at: datetime.datetime.now(),
        })

    def add_user_rights(self, session, user_id, rights_list):
        for one_rights in rights_list:
            one_db_rights = AdminUserModuleRightsModel(
                user_id=user_id,
                module_id=one_rights['module_id'],
                rights_id_list=json.dumps([1]),
            )
            session.add(one_db_rights)

    def check_admin_level(self, session, user_id, user_model):
        user = session.query(user_model).filter(
            user_model.user_id == user_id,
            user_model.deleted == False,
            user_model.level == _ROOT_ADMIN_LEVEL,
        ).first()

        # 1.0 判断是否是最高权限admin做的操作
        if not user:
            self.return_aes_error(30230)
        return user

    def delete_by_admin(self, user_id, user_name):
        """
        后台root用户添加用户
        :param user_id:
        :param user_name: 用户名
        :param password: 密码
        :param rights_list: 权限列表，形如：[{'module_id': 1}, {'module_id': 2}]
        :return:
        """
        with self.session_scope() as session:

            user_model = AdminUserModel
            self.check_admin_level(session, user_id, user_model)

            one_user = session.query(user_model).filter(
                user_model.name == user_name,
                user_model.deleted == False,
            ).first()

            # 2.0 判断用户是否存在,如果已经存在则用户已经注册
            if not one_user:
                return {
                    "status": "true",
                    "user_name": user_name
                }

            one_user.delete(session)
            self.delete_all_user_rights(session, one_user.user_id)

            session.commit()

            return {
                "user_name": user_name
            }

    def change_rights_by_admin(self, user_id, user_name, rights_list, password, change_type):
        """
        后台root用户调整用户权限
        :param user_id:
        :param user_name:
        :param rights_list:
        :param password:
        :param change_type: 修改类型，0所有，1权限，2密码
        :return:
        """
        if not password:
            self.return_aes_error(30233)
        if change_type not in ['0', '1', '2']:
            self.return_aes_error(30231)

        with self.session_scope() as session:

            user_model = AdminUserModel
            self.check_admin_level(session, user_id, user_model)

            one_user = session.query(user_model).filter(
                user_model.name == user_name,
                user_model.deleted == False,
            ).first()

            # 2.0 判断用户是否存在,如果已经存在则用户已经注册
            if not one_user:
                self.return_aes_error(30213)

            if change_type in ['0', '1']:
                self.delete_all_user_rights(session, one_user.user_id)
                self.add_user_rights(session, one_user.user_id, rights_list)
            if change_type in ['0', '2']:
                bcrypt_salt = get_bcrypt_salt().decode("utf-8")
                bcypt_password = get_bcrypt_pwd(password, bcrypt_salt)
                passwd_salt = urandom(12)
                db_password = sha512(str(bcypt_password), str(passwd_salt))

                one_user.bcrypt_salt = bcrypt_salt
                one_user.passwd_salt = passwd_salt
                one_user.password = db_password

            session.commit()

            return {
                "user_name": one_user.name
            }

    def list_rights_by_admin(self, user_id, user_name):
        """
        后台root用户获取用户权限, 只查询一级模块，并且认为有一级模块的权限，就是拥有一级模块下所有模块的所有权限
        :param user_id:
        :param user_name:
        :return:
        """
        with self.session_scope() as session:
            user_model = AdminUserModel
            self.check_admin_level(session, user_id, user_model)

            one_user = session.query(user_model).filter(
                user_model.name == user_name,
                user_model.deleted == False,
            ).first()

            # 2.0 判断用户是否存在,如果已经存在则用户已经注册
            if not one_user:
                self.return_aes_error(30213)

            rights_list = self.list_rights(session, one_user.user_id)

            session.commit()

            return {
                "user_name": user_name,
                "rights_list": rights_list
            }

    def get_admin_user_info_by_id(self, user_id, admin_level):
        with self.session_scope() as session:
            user_model = AdminUserModel
            one_user = session.query(user_model).filter(
                user_model.user_id == user_id,
                user_model.deleted == False,
                user_model.level == admin_level,
            ).first()
            if one_user is None:
                self.return_aes_error(10038)
            rights_list = self.list_rights(session, one_user.user_id)

            return {
                'user_id': one_user.user_id,
                'user_name': one_user.name,
                'level': one_user.level,
                "rights_list": rights_list,
            }

    def list_rights(self, session, user_id):
        db_rights_list = session.query(
            AdminUserModuleRightsModel.module_id,
            AdminUserModuleRightsModel.rights_id_list,
            AdminModuleModel.module_id,
            AdminModuleModel.name,
        ).join(
            AdminModuleModel,
            AdminModuleModel.module_id == AdminUserModuleRightsModel.module_id,
        ).filter(
            AdminUserModuleRightsModel.user_id == user_id,
            AdminUserModuleRightsModel.deleted == False,
            AdminModuleModel.deleted == False,
            AdminModuleModel.level == AdminModuleModel.origin_module_level,
        ).order_by(
            AdminUserModuleRightsModel.module_id,
        ).all()

        rights_list = []

        for one_db_right in db_rights_list:
            rights_list.append({
                'module_name': one_db_right.name,
                'module_id': one_db_right.module_id,
                'rights_id_list': one_db_right.rights_id_list,
            })
        return rights_list

    def get_transfer_url_by_user_id(self, user_id, module_id):
        with self.session_scope() as session:
            one_db_rights = session.query(
                AdminUserModuleRightsModel.module_id,
                AdminUserModuleRightsModel.rights_id_list,
                AdminModuleModel.module_id,
                AdminModuleModel.module_url,
                AdminModuleModel.name,
            ).join(
                AdminModuleModel,
                AdminModuleModel.module_id == AdminUserModuleRightsModel.module_id,
            ).filter(
                AdminUserModuleRightsModel.user_id == user_id,
                AdminUserModuleRightsModel.module_id == module_id,
                AdminUserModuleRightsModel.deleted == False,
                AdminModuleModel.deleted == False,
            ).first()

            if not one_db_rights:
                self.return_aes_error(30232)

            return one_db_rights.module_url

    def list_rights_to_admin(self, user_id):
        """
        后台root用户获取用户权限, 只查询一级模块，并且认为有一级模块的权限，就是拥有一级模块下所有模块的所有权限
        :param user_id:
        :param user_name:
        :return:
        """
        with self.session_scope() as session:
            user_model = AdminUserModel
            self.check_admin_level(session, user_id, user_model)

            rights_list = self.list_all_rights(session)

            return {
                "rights_list": rights_list
            }

    def list_all_rights(self, session):
        db_rights_list = session.query(
            AdminModuleModel
        ).filter(
            AdminModuleModel.deleted == False,
        ).all()

        rights_list = {}

        """
        for one_db_right in db_rights_list:
            if one_db_right.level == AdminModuleModel.origin_module_level:
                if one_db_right.module_id not in rights_list:
                    rights_list[one_db_right.module_id] = {
                        'module_id': one_db_right.module_id,
                        'module_name': one_db_right.name,
                        'sub_module_list': {},
                    }
                else:
                    rights_list[one_db_right.module_id]['module_name'] = one_db_right.name
            else:
                if one_db_right.level not in rights_list:
                    rights_list[one_db_right.level] = {
                        'module_id': one_db_right.level,
                        'module_name': '',
                        'sub_module_list': {},
                    }
                rights_list[one_db_right.level]['sub_module_list'][one_db_right.module_id] = {
                    'module_id': one_db_right.module_id,
                    'module_name': one_db_right.name,
                }
        """
        for one_db_right in db_rights_list:
            if one_db_right.level == AdminModuleModel.origin_module_level:
                if one_db_right.module_id in rights_list:
                    rights_list[one_db_right.module_id]['name'] = one_db_right.name
                else:
                    rights_list[one_db_right.module_id] = {
                        'module_id': one_db_right.module_id,
                        'module_name': one_db_right.name,
                        'sub_module_list': {},
                    }
            else:
                level_list = one_db_right.level.split("_")
                tmp_right_list = rights_list
                i = 1
                all_levels = len(level_list)
                for one_level in level_list:
                    if one_level not in tmp_right_list:
                        tmp_right_list['sub_module_list'][one_level] = {
                            'module_id': one_level,
                            'module_name': '',
                            'sub_module_list': {},
                        }
                    tmp_right_list = tmp_right_list[one_level]['sub_module_list']
                    if i == all_levels:
                        tmp_right_list[one_db_right.module_id] = {
                            'module_id': one_db_right.module_id,
                            'module_name': one_db_right.name,
                            'sub_module_list': {},
                        }
                    i += 1

        return rights_list

    def check_admin_user_module_rights_by_user_id(self, user_id, module_url):
        return True
        with self.session_scope() as session:
            one_db_rights = session.query(
                AdminUserModuleRightsModel.module_id,
                AdminUserModuleRightsModel.rights_id_list,
                AdminModuleModel.module_id,
                AdminModuleModel.module_url,
                AdminModuleModel.name,
            ).join(
                AdminModuleModel,
                AdminModuleModel.module_id == AdminUserModuleRightsModel.module_id,
            ).filter(
                AdminUserModuleRightsModel.user_id == user_id,
                AdminModuleModel.module_url == module_url,
                AdminUserModuleRightsModel.deleted == False,
                AdminModuleModel.deleted == False,
            ).first()

            if not one_db_rights:
                self.return_aes_error(30232)

            return True

    def login_by_mobile(self, user_mobile, vcode, user_type=_USER_TYPE_INVEST, source=None, mobile_country_code=None,
                        check_fail_times=True):
        """
        用户登录
        :param user_mobile: 手机号
        :param bcypt_password: 密码
        :return:
        """
        register_by = _REGISTER_BY_MOBILE
        with self.session_scope() as session:
            if user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                if mobile_country_code is None or mobile_country_code == '':
                    self.return_aes_error(30217)
                user = session.query(user_model).filter(
                    user_model.user_mobile == user_mobile,
                    user_model.mobile_country_code == mobile_country_code,
                    user_model.deleted == False,
                    user_model.status_on == user_model.status_on,
                ).first()
            else:
                self.return_aes_error(10019)

            #  1.0 获取用户
            if not user:
                self.return_aes_error(30209)

            if check_fail_times:
                redis_tool = RedisTools()
                redis_key = self.make_login_fail_times_key(user.user_id, user_type)
                fail_times = redis_tool.get(redis_key)
                if fail_times:
                    fail_times = int(fail_times)
                    if fail_times > _LOGIN_FAIL_TIMES_LIMIT:
                        self.return_aes_error(30226)

            # 2.0 检查验证码有效性
            vcode_service = VcodeService(aes_share_key=self.aes_share_key, aes_nonce=self.aes_nonce)
            result = vcode_service.check_vcode(vcode, _VCODE_LOGIN, user_mobile, user_type=user_type,
                                               register_by=register_by, direct_return_error=False)

            if not result:
                if check_fail_times:
                    if not fail_times:
                        redis_tool.set(redis_key, 1, ex=_LOGIN_FAIL_TIME_LIMIT)
                    else:
                        redis_tool.set(redis_key, int(fail_times) + 1, ex=_LOGIN_FAIL_TIME_LIMIT)
                self.return_aes_error(30059)

            #  3.0 生成Token
            r = ApiTokenService().\
                generator_user_tokens(user.user_id, user_type=user_type, source=source)
            return r

    def dev_get_register_key_salt_by_type(self, user_name, register_by, user_type=_USER_TYPE_INVEST,
                                          user_source=None, mobile_country_code=None):
        '''
        仅开发环境，获取注册时输入的密码salt，和aes加密的服务端公钥和nonce
        :param user_name: 用户名
        :param register_by: 注册所用字段
        :param user_type: 用户类别
        :param user_source: 客户端类别
        :param mobile_country_code: 客户端注册使用的用户名类型
        :return:
        '''

        request_type = _REQUEST_TYPE_REGISTER
        self.check_source(register_by, user_source)

        with self.session_scope() as session:
            if user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                if register_by == _REGISTER_BY_MOBILE:
                    if mobile_country_code is None or mobile_country_code == '':
                        self.return_aes_error(30217)
                    user = session.query(user_model).filter(
                        user_model.user_mobile == user_name,
                        user_model.mobile_country_code == mobile_country_code,
                        user_model.deleted == False,
                    ).first()
                elif register_by == _REGISTER_BY_EMAIL:
                    user = session.query(user_model).filter(
                        user_model.email == user_name,
                        user_model.deleted == False,
                    ).first()
                else:
                    self.return_aes_error(30215)
            else:
                self.return_aes_error(10019)

            if user is not None:
                self.return_aes_error(30203)

            self.delete_user_key_salt(session, user_name, user_type, request_type, user_source=user_source)
            bcrypt_salt = get_bcrypt_salt().decode("utf-8")
            server_private_key = generate_ecc_private_key()  # 获取ECC私钥
            server_private_key_pem = get_ecc_private_key_pem_from_private(server_private_key)  # 格式化ecc私钥
            server_public_key_pem = get_ecc_public_key_pem_from_private(server_private_key)  # 获取ecc公钥

            # 伪造客户端公钥
            client_private_key = generate_ecc_private_key()
            client_private_key_pem = get_ecc_private_key_pem_from_private(client_private_key)
            client_public_key_pem = get_ecc_public_key_pem_from_private(client_private_key)

            share_key = get_ecc_shared_key(client_public_key_pem.encode('utf-8'), server_private_key)  # 获取share-key
            nonce = urandom(12)  # 获取随机数

            # 2.0 创建salt表
            key_salt = KeySaltModel(
                user_id=user_name,
                user_type=user_type,
                request_type=request_type,
                server_public_key=server_public_key_pem,
                server_private_key=server_private_key_pem,
                client_public_key=client_public_key_pem,
                share_key=share_key,
                bcrypt_salt=bcrypt_salt,
                nonce=nonce,
                source=user_source,
            )
            session.add(key_salt)
            session.commit()

            return {
                "server_public_key": server_public_key_pem,
                "user_name": user_name,
                "bcrypt_salt": bcrypt_salt,
                "nonce": nonce,
                "time_stamp": str(int(time.time())),
                "client_public_key": client_public_key_pem,
                "client_private_key": client_private_key_pem,
            }

    def dev_get_login_key_salt_by_type(self, user_name, user_type=_USER_TYPE_INVEST, source=None,
                                       register_by=None, mobile_country_code=None, admin_level=0):
        """
        仅开发环境，登录时,验证用户注册状态,并且创建key-salt
        :param user_mobile:
        :param client_public_key:
        :return:
        """
        request_type = _REQUEST_TYPE_LOGIN
        self.check_source(register_by, source)

        with self.session_scope() as session:
            if user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel

                if register_by == _REGISTER_BY_MOBILE:
                    if mobile_country_code is None or mobile_country_code == '':
                        self.return_aes_error(30217)
                    user = session.query(user_model).filter(
                        user_model.user_mobile == user_name,
                        user_model.mobile_country_code == mobile_country_code,
                        user_model.deleted == False,
                    ).first()
                elif register_by == _REGISTER_BY_EMAIL:
                    user = session.query(user_model).filter(
                        user_model.email == user_name,
                        user_model.deleted == False,
                    ).first()
                elif register_by == _LOGININ_BY_USER_NAME:
                    user = session.query(user_model).filter(
                        user_model.user_name == user_name,
                        user_model.deleted == False,
                    ).first()
                else:
                    self.return_aes_error(30215)
            else:
                self.return_aes_error(10019)

            #  1.0 判断用户是否存在
            if user is None:
                # 用户未注册
                self.return_aes_error(10045)

            #  删除之前的用户key
            self.delete_user_key_salt(session, user.user_id, user_type, request_type, user_source=source,
                                      admin_level=admin_level)

            bcrypt_salt = user.bcrypt_salt  # 获取密码加密密钥
            server_private_key = generate_ecc_private_key()  # 获取ECC私钥
            server_private_key_pem = get_ecc_private_key_pem_from_private(server_private_key)  # 格式化ecc私钥
            server_public_key_pem = get_ecc_public_key_pem_from_private(server_private_key)  # 获取ecc公钥

            # 伪造客户端公钥
            client_private_key = generate_ecc_private_key()
            client_private_key_pem = get_ecc_private_key_pem_from_private(client_private_key)
            client_public_key_pem = get_ecc_public_key_pem_from_private(client_private_key)

            share_key = get_ecc_shared_key(client_public_key_pem.encode('utf-8'), server_private_key)  # 获取share-key
            nonce = urandom(12)  # 获取随机数

            # 2.0 创建salt表
            key_salt = KeySaltModel(
                user_id=user.user_id,
                user_type=user_type,
                user_level=admin_level,
                request_type=request_type,
                server_public_key=server_public_key_pem,
                server_private_key=server_private_key_pem,
                client_public_key=client_public_key_pem,
                share_key=share_key,
                bcrypt_salt=bcrypt_salt,
                nonce=nonce,
                source=source,
            )
            session.add(key_salt)
            session.commit()

            return {
                "server_public_key": server_public_key_pem,
                "user_name": user_name,
                "bcrypt_salt": bcrypt_salt,
                "nonce": nonce,
                "time_stamp": str(int(time.time())),
                "client_public_key": client_public_key_pem,
                "client_private_key": client_private_key_pem,
            }

    def get_login_client_salt(self, user_id, user_type=_USER_TYPE_INVEST):
        """
        仅开发环境，登录时,验证用户注册状态,并且创建key-salt
        :param user_mobile:
        :param client_public_key:
        :return:
        """
        with self.session_scope() as session:
            if user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                user = session.query(user_model).filter(
                        user_model.user_id == user_id,
                        user_model.deleted == False,
                    ).first()
            else:
                self.return_aes_error(10019)

            #  1.0 判断用户是否存在
            if user is None:
                # 用户未注册
                self.return_aes_error(10045)

            return {
                "bcrypt_salt": user.bcrypt_salt,
            }

    def get_unlogin_client_salt(self, user_name, user_type=_USER_TYPE_INVEST, register_by=None, mobile_country_code=None):
        """
        登录时,验证用户注册状态,并且创建key-salt
        :param user_mobile:
        :param client_public_key:
        :return:
        """

        with self.session_scope() as session:
            if user_type == _USER_TYPE_INVEST:
                user_model = InvestUserModel
                if register_by == _REGISTER_BY_MOBILE:
                    if mobile_country_code is None or mobile_country_code == '':
                        self.return_aes_error(30217)
                    user = session.query(user_model).filter(
                        user_model.user_mobile == user_name,
                        user_model.mobile_country_code == mobile_country_code,
                        user_model.deleted == False,
                    ).first()
                elif register_by == _REGISTER_BY_EMAIL:
                    user = session.query(user_model).filter(
                        user_model.email == user_name,
                        user_model.deleted == False,
                    ).first()
                else:
                    self.return_aes_error(30215)
            else:
                self.return_aes_error(10019)

            #  1.0 判断用户是否存在
            if user is None:
                # 用户未注册
                self.return_aes_error(10045)

            return {
                "bcrypt_salt": user.bcrypt_salt,
            }



