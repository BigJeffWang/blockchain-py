from models.announcement_manage_model import AnnouncementManageModel
from models.banner_manage_model import BannerManageModel
from models.mine_comments_model import MineCommentsModel
from services.account_service import AccountService
from services.base_service import BaseService
from utils.util import get_offset_by_page, get_page_by_offset
from tools.mysql_tool import MysqlTools


class OperatingService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def comment_manage_list(self, limit, offset, user_name='', key_word='', release_time_start='',
                            release_time_end='', status='', picture=''):
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
                order_by(MineCommentsModel.created_at.desc())
            if user_name != '':
                q = q.filter(MineCommentsModel.user_name == user_name)
            if key_word != '':
                q = q.filter(MineCommentsModel.submit_content.like('%' + key_word + '%'))
            if status != '':
                q = q.filter(MineCommentsModel.status == status)
            if release_time_start != '':
                q = q.filter(MineCommentsModel.created_at >= release_time_start)
            if release_time_end != '':
                q = q.filter(MineCommentsModel.created_at <= release_time_end)
            if picture == '1':
                q = q.filter(MineCommentsModel.submit_image != '')
            if picture == '0':
                q = q.filter(MineCommentsModel.submit_image == '')
            record_count = q.count()
            result_dict['total'] = record_count
            result_dict['count'] = get_page_by_offset(record_count, limit)
            query_result = q.all()
            if query_result is not None:
                for i in query_result:
                    # user_info = account_service.get_inner_user_account_info(session, i.user_id)
                    result_dict['content'].append({
                        "user_name": i.user_name,
                        'submit_content': i.submit_content,
                        'submit_image': i.submit_image,
                        'submit_thumbnail': i.submit_thumbnail,
                        'praise_number': i.praise_number,
                        'status': i.status
                    })
            return result_dict

    def change_status(self, comment_id, new_status):
        with MysqlTools().session_scope() as session:
            if comment_id == '':
                self.return_error(40003)
            comment = session.query(MineCommentsModel). \
                filter(MineCommentsModel._id == comment_id).first()
            comment.status = new_status
            session.commit()
        return {
            "status": True
        }

    def create_announce(self, title, site, auto_online, auto_offline='', remark=''):
        if auto_offline <= auto_online:
            self.return_error(40011)
        with MysqlTools().session_scope() as session:
            announce = AnnouncementManageModel(
                title=title,
                site=site,
                auto_online=auto_online,
                auto_offline=auto_offline,
                remark=remark,
                status=0
            )
            session.add(announce)
            session.commit()
        return {
            "status": True
        }

    def get_announce_list(self, limit, offset, title='', site='', online_time_start='',
                          online_time_end='', status='', create_time_start='',
                          create_time_end=''):
        offset = get_offset_by_page(offset, limit)
        result_dict = {
            'limit': limit,
            'offset': offset,
            'count': 0,
            'content': [],
            'total': 0
        }
        with MysqlTools().session_scope() as session:
            q = session.query(AnnouncementManageModel). \
                order_by(AnnouncementManageModel.created_at.desc())
            if title != '':
                q = q.filter(AnnouncementManageModel.title == title)
            if site != '':
                q = q.filter(AnnouncementManageModel.site == site)
            if status != '':
                q = q.filter(AnnouncementManageModel.status == status)
            if create_time_start != '':
                q = q.filter(AnnouncementManageModel.created_at >= create_time_start)
            if create_time_end != '':
                q = q.filter(AnnouncementManageModel.created_at <= create_time_end)
            if online_time_start != '':
                q = q.filter(AnnouncementManageModel.auto_online >= online_time_start)
            if online_time_end != '':
                q = q.filter(AnnouncementManageModel.auto_online <= online_time_end)
            record_count = q.count()
            result_dict['total'] = record_count
            result_dict['count'] = get_page_by_offset(record_count, limit)
            query_result = q.all()
            if query_result is not None:
                for i in query_result:
                    result_dict['content'].append({
                        'id': i._id,
                        "title": i.title,
                        'site': i.site,
                        'status': i.status,
                        'created_at': str(i.created_at),
                        'auto_online': str(i.auto_online),
                        'remark': i.remark
                    })
            return result_dict

    def announce_details(self, announce_id):
        with MysqlTools().session_scope() as session:
            announce = session.query(AnnouncementManageModel). \
                filter(AnnouncementManageModel._id == announce_id).first()
            result = {
                'created_at': str(announce.created_at),
                'title': announce.title,
                'site': announce.site,
                'auto_online': str(announce.auto_online),
                'auto_offline': str(announce.auto_offline),
                'status': announce.status,
                'remark': announce.remark
            }
            return result

    def edit_announce(self, announce_id, title, site, auto_online, auto_offline='', remark=''):
        if auto_offline <= auto_online:
            self.return_error(40011)
        with MysqlTools().session_scope() as session:
            announce = session.query(AnnouncementManageModel). \
                filter(AnnouncementManageModel._id == announce_id).first()
            if announce.status != 0:
                self.return_error(40012)
            announce.title = title
            announce.site = site
            announce.auto_online = auto_online
            if auto_offline != '':
                announce.auto_offline = auto_offline
            if remark != '':
                announce.remark = remark
            session.commit()
        return {
            "status": True
        }

    def change_announce_status(self, announce_id, status):
        with MysqlTools().session_scope() as session:
            announce = session.query(AnnouncementManageModel). \
                filter(AnnouncementManageModel._id == announce_id).first()
            announce.status = status
            session.commit()
        return {
            "status": True
        }

    def create_banner(self, title, site, image, thumbnail, auto_online='', remark=''):
        with MysqlTools().session_scope() as session:
            banner = BannerManageModel(
                title=title,
                site=site,
                image=image,
                thumbnail=thumbnail,
                auto_online=auto_online,
                remark=remark,
                status=0
            )
            session.add(banner)
            session.commit()
        return {
            "status": True
        }

    def get_banner_list(self, limit, offset, title='', site='', online_time_start='',
                        online_time_end='', status='', create_time_start='',
                        create_time_end=''):
        offset = get_offset_by_page(offset, limit)
        result_dict = {
            'limit': limit,
            'offset': offset,
            'count': 0,
            'content': [],
            'total': 0
        }
        with MysqlTools().session_scope() as session:
            q = session.query(BannerManageModel). \
                order_by(BannerManageModel.created_at.desc())
            if title != '':
                q = q.filter(BannerManageModel.title == title)
            if site != '':
                q = q.filter(BannerManageModel.site == site)
            if status != '':
                q = q.filter(BannerManageModel.status == status)
            if create_time_start != '':
                q = q.filter(BannerManageModel.created_at >= create_time_start)
            if create_time_end != '':
                q = q.filter(BannerManageModel.created_at <= create_time_end)
            if online_time_start != '':
                q = q.filter(BannerManageModel.auto_online >= online_time_start)
            if online_time_end != '':
                q = q.filter(BannerManageModel.auto_online <= online_time_end)
            record_count = q.count()
            result_dict['total'] = record_count
            result_dict['count'] = get_page_by_offset(record_count, limit)
            query_result = q.all()
            if query_result is not None:
                for i in query_result:
                    result_dict['content'].append({
                        'id': i._id,
                        "title": i.title,
                        'site': i.site,
                        'status': i.status,
                        'image': i.image,
                        'thumbnail': i.thumbnail,
                        'created_at': str(i.created_at),
                        'auto_online': str(i.auto_online),
                        'remark': i.remark
                    })
            return result_dict

    def banner_details(self, banner_id):
        with MysqlTools().session_scope() as session:
            banner = session.query(BannerManageModel). \
                filter(BannerManageModel._id == banner_id).first()
            result = {
                'created_at': str(banner.created_at),
                'title': banner.title,
                'image': banner.image,
                'thumbnail': banner.thumbnail,
                'site': banner.site,
                'auto_online': str(banner.auto_online),
                'auto_offline': str(banner.auto_offline),
                'status': banner.status,
                'remark': banner.remark
            }
            return result

    def edit_banner(self, banner_id, title, site, auto_online, image, thumbnail, remark=''):
        with MysqlTools().session_scope() as session:
            banner = session.query(BannerManageModel). \
                filter(BannerManageModel._id == banner_id).first()
            if banner.status != 0:
                self.return_error(40013)
            banner.title = title
            banner.site = site
            banner.auto_online = auto_online
            banner.image = image
            banner.thumbnail = thumbnail
            if remark != '':
                banner.remark = remark
            session.commit()
        return {
            "status": True
        }

    def change_banner_status(self, banner_id, status):
        with MysqlTools().session_scope() as session:
            announce = session.query(BannerManageModel). \
                filter(BannerManageModel._id == banner_id).first()
            announce.status = status
            session.commit()
        return {
            "status": True
        }
