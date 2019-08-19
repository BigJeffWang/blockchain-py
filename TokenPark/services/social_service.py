import time

from models.mine_comments_model import MineCommentsModel
from services.account_service import AccountService
from services.base_service import BaseService
from tools.mysql_tool import MysqlTools
from utils.util import get_offset_by_page, get_page_by_offset


class SocialService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_comment(self, content, submit_thumbnail='', submit_image='', user_id='', user_name=''):
        with MysqlTools().session_scope() as session:
            if user_id == '':
                self.return_error(20011)
            if content == '':
                self.return_error(40002)
            comment = MineCommentsModel(
                user_id=user_id,
                user_name=user_name,
                submit_content=content,
                praise_number=0,
                praise_users='',
                submit_image=submit_image,
                submit_thumbnail=submit_thumbnail,
                status=1
            )
            session.add(comment)
            session.commit()
        return {
            "status": True
        }

    def remove_comment(self, user_id, comment_id):
        with MysqlTools().session_scope() as session:
            comment = session.query(MineCommentsModel). \
                filter(MineCommentsModel._id == comment_id,
                       MineCommentsModel.user_id == user_id).delete()
            session.commit()
        return {
            "status": True
        }


    def add_praise(self, user_id, comment_id):
        with MysqlTools().session_scope() as session:
            if user_id == '':
                self.return_error(20011)
            if comment_id == '':
                self.return_error(40003)
            comment = session.query(MineCommentsModel). \
                filter(MineCommentsModel._id == comment_id).first()
            is_praise = self.get_is_praise(user_id, comment.praise_users)
            if is_praise == 1:
                self.return_error(40007)
            else:
                comment.praise_number = int(comment.praise_number) + 1
                comment.praise_users = comment.praise_users + ',' + str(user_id)
                session.commit()
        return {
            "status": True
        }

    def remove_praise(self, user_id, comment_id):
        with MysqlTools().session_scope() as session:
            if user_id == '':
                self.return_error(20011)
            if comment_id == '':
                self.return_error(40003)
            comment = session.query(MineCommentsModel). \
                filter(MineCommentsModel._id == comment_id).first()
            if comment.praise_number > 0:
                comment.praise_number = int(comment.praise_number) - 1
            comment.praise_users = comment.praise_users.replace(',' + str(user_id), '')
            session.commit()
        return {
            "status": True
        }

    def get_comment_list(self, limit, offset, user_id):
        offset = get_offset_by_page(offset, limit)
        result_dict = {
            'limit': limit,
            'offset': offset,
            'count': 0,
            'content': [],
            'total': 0
        }
        with MysqlTools().session_scope() as session:
            # account_service = AccountService()
            q = session.query(MineCommentsModel). \
                filter(MineCommentsModel.status == 1). \
                order_by(MineCommentsModel.created_at.desc())
            record_count = q.count()
            result_dict['total'] = record_count
            result_dict['count'] = get_page_by_offset(record_count, limit)
            query_result = q.all()
            if query_result is not None:
                for i in query_result:
                    # user_info = account_service.get_inner_user_account_info(session, i.user_id)
                    is_praise = self.get_is_praise(user_id, i.praise_users)
                    result_dict['content'].append({
                        'user_name': i.user_name,
                        'submit_content': i.submit_content,
                        'submit_image': i.submit_image,
                        'submit_thumbnail': i.submit_thumbnail,
                        'praise_number': i.praise_number,
                        'is_praise': is_praise,
                        'status': i.status
                    })
            return result_dict

    def get_is_praise(self, user_id, praise_list):
        arr = praise_list.split(',')
        for i in arr:
            if i == user_id:
                return 1
        return 0

    def get_mine_comment_list(self, limit, offset, user_id):
        offset = get_offset_by_page(offset, limit)
        result_dict = {
            'limit': limit,
            'offset': offset,
            'count': 0,
            'content': [],
            'total': 0
        }
        with MysqlTools().session_scope() as session:
            # account_service = AccountService()
            q = session.query(MineCommentsModel). \
                filter(MineCommentsModel.user_id == user_id, MineCommentsModel.status == 1). \
                order_by(MineCommentsModel.created_at.desc())
            record_count = q.count()
            result_dict['total'] = record_count
            result_dict['count'] = get_page_by_offset(record_count, limit)
            query_result = q.all()
            if query_result is not None:
                for i in query_result:
                    # user_info = account_service.get_inner_user_account_info(session, i.user_id)
                    is_praise = self.get_is_praise(user_id, i.praise_users)
                    result_dict['content'].append({
                        'user_name': i.user_name,
                        'submit_content': i.submit_content,
                        'submit_image': i.submit_image,
                        'submit_thumbnail': i.submit_thumbnail,
                        'praise_number': i.praise_number,
                        'is_praise': is_praise,
                        'status': i.status
                    })
            return result_dict
