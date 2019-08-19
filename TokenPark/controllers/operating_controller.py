from controllers.base_controller import BaseController
from services.operating_service import OperatingService
from tools.decorator_tools import FormatOutput


class CommentManageListController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict()
        limit = request_data.get('limit', 10)
        offset = request_data.get('offset', 1)
        user_name = request_data.get('user_name', '')
        key_word = request_data.get('key_word', '')
        release_time_start = request_data.get('release_time_start', '')
        release_time_end = request_data.get('release_time_end', '')
        status = request_data.get('status', '')
        picture = request_data.get('picture', '')
        operating_service = OperatingService()
        result = operating_service.comment_manage_list(limit, offset, user_name, key_word,
                                                       release_time_start, release_time_end, status, picture)

        return result


class ChangeCommentStatusController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['comment_id', 'status'])
        comment_id = request_data['comment_id']
        status = request_data['status']
        operating_service = OperatingService()
        result = operating_service.change_status(comment_id, status)

        return result


class CreateAnnounceController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['title', 'site', 'auto_online'])
        title = request_data['title']
        site = request_data['site']
        auto_online = request_data['auto_online']
        auto_offline = request_data.get('auto_offline', '')
        remark = request_data.get('remark', '')
        operating_service = OperatingService()
        result = operating_service.create_announce(title, site, auto_online, auto_offline, remark)

        return result


class AnnounceListController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict()
        limit = request_data.get('limit', 10)
        offset = request_data.get('offset', 1)
        title = request_data.get('title', '')
        site = request_data.get('site', '')
        online_time_start = request_data.get('online_time_start', '')
        online_time_end = request_data.get('online_time_end', '')
        status = request_data.get('status', '')
        create_time_start = request_data.get('create_time_start', '')
        create_time_end = request_data.get('create_time_end', '')
        operating_service = OperatingService()
        result = operating_service.get_announce_list(limit, offset, title, site, online_time_start,
                                                     online_time_end, status, create_time_start,
                                                     create_time_end)

        return result


class AnnounceDetailsController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['announce_id'])
        announce_id = request_data['announce_id']
        operating_service = OperatingService()
        result = operating_service.announce_details(announce_id)

        return result


class EditAnnounceController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['announce_id', 'title', 'site', 'auto_online'])
        announce_id = request_data['announce_id']
        title = request_data['title']
        site = request_data['site']
        auto_online = request_data['auto_online']
        auto_offline = request_data.get('auto_offline', '')
        remark = request_data.get('remark', '')
        operating_service = OperatingService()
        result = operating_service.edit_announce(announce_id, title, site, auto_online, auto_offline, remark)

        return result


class ChangeAnnounceStatusController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['announce_id', 'status'])
        announce_id = request_data['announce_id']
        status = request_data['status']
        operating_service = OperatingService()
        result = operating_service.change_announce_status(announce_id, status)

        return result


class CreateBannerController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['title', 'site', 'image', 'thumbnail'])
        title = request_data['title']
        site = request_data['site']
        image = request_data['image']
        thumbnail = request_data['thumbnail']
        auto_online = request_data.get('auto_online', '')
        remark = request_data.get('remark', '')
        operating_service = OperatingService()
        result = operating_service.create_banner(title, site, image, thumbnail, auto_online, remark)

        return result


class BannerListController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict()
        limit = request_data.get('limit', 10)
        offset = request_data.get('offset', 1)
        title = request_data.get('title', '')
        site = request_data.get('site', '')
        online_time_start = request_data.get('online_time_start', '')
        online_time_end = request_data.get('online_time_end', '')
        status = request_data.get('status', '')
        create_time_start = request_data.get('create_time_start', '')
        create_time_end = request_data.get('create_time_end', '')
        operating_service = OperatingService()
        result = operating_service.get_banner_list(limit, offset, title, site, online_time_start,
                                                   online_time_end, status, create_time_start,
                                                   create_time_end)
        return result


class EditBannerController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(
            must_keys=['banner_id', 'title', 'site', 'auto_online', 'image', 'thumbnail'])
        banner_id = request_data['banner_id']
        title = request_data['title']
        site = request_data['site']
        auto_online = request_data['auto_online']
        image = request_data['image']
        thumbnail = request_data['thumbnail']
        remark = request_data.get('remark', '')
        operating_service = OperatingService()
        result = operating_service.edit_banner(banner_id, title, site, auto_online, image,
                                               thumbnail, remark)

        return result


class BannerDetailsController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['banner_id'])
        banner_id = request_data['banner_id']
        operating_service = OperatingService()
        result = operating_service.banner_details(banner_id)

        return result


class ChangeBannerStatusController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['banner_id', 'status'])
        banner_id = request_data['banner_id']
        status = request_data['status']
        operating_service = OperatingService()
        result = operating_service.change_banner_status(banner_id, status)

        return result
