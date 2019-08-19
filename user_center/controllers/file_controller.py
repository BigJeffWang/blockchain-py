# 文件处理
from controllers.base_controller import BaseController
from flask import request
from tools.decorator_tools import FormateOutput
from services.file_service import FileService


class UploadPhotoController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # @FormateOutput(default_value=10001, return_type='return_error')
    def post(self):
        files = request.files.getlist('files')
        file_service = FileService()
        # dict = file_service.uploan_photo(files)
        # 线上用下面的方法，地址头改为https://s3-ap-northeast-1.amazonaws.com/tokenpark-test/
        dict = file_service.uploan_photo_s3_session(files)
        flag = dict["flag"]
        file_path_list = dict["file_path_list"]
        if flag == 0:
            pass
        elif flag == 1:
            self.return_error(20001)
        elif flag == 2:
            self.return_error(20002)
        elif flag == 3:
            self.return_error(20003)
        return file_path_list
