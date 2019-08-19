from services.base_service import BaseService
from common_settings import *
from models.invest_user_model import InvestUserModel
from models.borrow_user_model import BorrowUserModel
from crypto_utils import *


class PasswordService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def base_check_method(self, argument_dict, user_type=_USER_TYPE_INVEST):
        with self.session_scope() as session:
            if user_type == _USER_TYPE_INVEST:
                q = session.query(InvestUserModel).filter_by(user_id=argument_dict['user_id'], deleted=False).first()
            elif user_type == _USER_TYPE_BORROW:
                q = session.query(BorrowUserModel).filter_by(user_id=argument_dict['user_id'], deleted=False).first()
            else:
                self.return_aes_error(10019)

            if q is None:
                self.return_aes_error(30213)

            result = slow_is_equal(q.password, sha512(str(argument_dict['old_password']), str(q.passwd_salt)))
            if not result:
                self.return_aes_error(30212)

            return {
                    "status": _PASSWORD_CHECK_TYPE_REDIRECT,
                    "rediret_url": "http://127.0.0.1:5001/show",
                }









