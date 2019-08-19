# game相关
from controllers.base_controller import BaseController
from services.social_service import SocialService
from tools.decorator_tools import FormatOutput


# 发表评论
class AddCommentController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id', 'user_name', 'content'])
        user_id = request_data['user_id']
        user_name = request_data['user_name']
        content = request_data['content']
        submit_image = request_data.get('submit_image', '')
        submit_thumbnail = request_data.get('submit_thumbnail', '')
        social_service = SocialService()
        result = social_service.add_comment(content, submit_thumbnail, submit_image, user_id, user_name)
        return result


# 删除晒单
class RemoveCommentController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id', 'comment_id'])
        user_id = request_data['user_id']
        comment_id = request_data['comment_id']
        social_service = SocialService()
        result = social_service.remove_comment(user_id, comment_id)
        return result


# 点赞
class AddPraiseController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id', 'comment_id'])
        user_id = request_data['user_id']
        comment_id = request_data['comment_id']
        social_service = SocialService()
        result = social_service.add_praise(user_id, comment_id)
        return result


# 取消点赞
class RemovePraiseController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id', 'comment_id'])
        user_id = request_data['user_id']
        comment_id = request_data['comment_id']
        social_service = SocialService()
        result = social_service.remove_praise(user_id, comment_id)
        return result


# 评论列表
class CommentListController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id'])
        limit = request_data.get('limit', 10)
        offset = request_data.get('offset', 1)
        user_id = request_data['user_id']
        social_service = SocialService()
        result = social_service.get_comment_list(limit, offset, user_id)
        return result


# 我的评论列表
class MineCommentController(BaseController):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id'])
        limit = request_data.get('limit', 10)
        offset = request_data.get('offset', 1)
        user_id = request_data['user_id']
        social_service = SocialService()
        result = social_service.get_mine_comment_list(limit, offset, user_id)
        return result
