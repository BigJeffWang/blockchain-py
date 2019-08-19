from services.base_service import BaseService
import oss2
from file_util import *
import boto3
from boto3.session import Session
from config import get_aws_config


class FileService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def uploan_photo(self, files):
        # 阿里云OSS
        auth = oss2.Auth('LTAIfOBx5PwVRo7s', 'Okk2D3aqtY14aGjXFV3BB5xjeSIGZF')
        bucket = oss2.Bucket(auth, 'http://oss-cn-beijing.aliyuncs.com', 'mshc-finance')

        # 处理文件
        flag = 0  # 0=默认,1=文件太大,2=文件格式有误，3=未选择文件
        max_size = 20971520  # 20MB
        file_path_list = []
        if len(files) == 0:
            flag = 3
        else:
            for file in files:
                file_read = file.read()
                # 判断文件大小
                file_size = len(file_read)
                if file_size > max_size:
                    flag = 1
                    break
                # 判断文件格式
                file_name = file.filename
                index = file_name.rfind(".")
                if index != -1:
                    format = file_name[index + 1:].lower()
                    if format == "jpg" or format == "jpeg" or format == "png" or format == "bmp" or format == "gif":
                        ori = create_photo_path(format)
                        dict = {"ori": ori, "thumb": ""}
                        bucket.put_object(ori, file_read)
                        if file_size > 20480:
                            thumb = create_photo_path("png")
                            dict["thumb"] = thumb
                            # 生成缩略图
                            thumb_bytes = pied_piper(file_read)
                            bucket.put_object(thumb, thumb_bytes)
                        else:
                            dict["thumb"] = ori
                        file_path_list.append(dict)
                    elif format == "pdf":
                        pdf_path = create_photo_path(format)
                        bucket.put_object(pdf_path, file_read)
                        file_path_list.append(pdf_path)
                    else:
                        flag = 2
                        break
                else:
                    flag = 2
                    break
        return {"flag": flag, "file_path_list": file_path_list}

    def uploan_photo_s3(self, files):
        s3 = boto3.resource('s3')
        # 处理文件
        flag = 0  # 0=默认,1=文件太大,2=文件格式有误，3=未选择文件
        max_size = 20971520  # 20MB
        file_path_list = []
        if len(files) == 0:
            flag = 3
        else:
            for file in files:
                file_read = file.read()
                # 判断文件大小
                file_size = len(file_read)
                if file_size > max_size:
                    flag = 1
                    break
                # 判断文件格式
                file_name = file.filename
                index = file_name.rfind(".")
                if index != -1:
                    format = file_name[index + 1:].lower()
                    if format == "jpg" or format == "jpeg" or format == "png" or format == "bmp" or format == "gif":
                        ori = create_photo_path(format)
                        dict = {"ori": ori, "thumb": ""}
                        s3.Bucket('tokenpark-test').put_object(Key=ori, Body=file_read)
                        if file_size > 20480:
                            thumb = create_photo_path("png")
                            dict["thumb"] = thumb
                            # 生成缩略图
                            thumb_bytes = pied_piper(file_read)
                            s3.Bucket('tokenpark-test').put_object(Key=thumb, Body=thumb_bytes)
                        else:
                            dict["thumb"] = ori
                        file_path_list.append(dict)
                    elif format == "pdf":
                        pdf_path = create_photo_path(format)
                        s3.Bucket('tokenpark-test').put_object(Key=pdf_path, Body=file_read)
                        file_path_list.append(pdf_path)
                    else:
                        flag = 2
                        break
                else:
                    flag = 2
                    break
        return {"flag": flag, "file_path_list": file_path_list}

    def uploan_photo_s3_session(self, files):
        aws_config = get_aws_config()
        aws_key = aws_config['aws_access_key_id']
        aws_secret = aws_config['aws_secret_access_key']
        session = Session(aws_access_key_id=aws_key,
                          aws_secret_access_key=aws_secret,
                          region_name="ap-northeast-1")
        s3 = session.resource("s3")
        bucket = "tokenpark-test"

        # 处理文件
        flag = 0  # 0=默认,1=文件太大,2=文件格式有误，3=未选择文件
        max_size = 20971520  # 20MB
        file_path_list = []
        if len(files) == 0:
            flag = 3
        else:
            for file in files:
                file_read = file.read()
                # 判断文件大小
                file_size = len(file_read)
                if file_size > max_size:
                    flag = 1
                    break
                # 判断文件格式
                file_name = file.filename
                index = file_name.rfind(".")
                if index != -1:
                    format = file_name[index + 1:].lower()
                    if format == "jpg" or format == "jpeg" or format == "png" or format == "bmp" or format == "gif":
                        ori = create_photo_path(format)
                        dict = {"ori": ori, "thumb": ""}
                        s3.Bucket(bucket).put_object(Key=ori, Body=file_read)
                        if file_size > 20480:
                            thumb = create_photo_path("png")
                            dict["thumb"] = thumb
                            # 生成缩略图
                            thumb_bytes = pied_piper(file_read)
                            s3.Bucket(bucket).put_object(Key=ori, Body=file_read)
                        else:
                            dict["thumb"] = ori
                        file_path_list.append(dict)
                    elif format == "pdf":
                        pdf_path = create_photo_path(format)
                        s3.Bucket(bucket).put_object(Key=ori, Body=file_read)
                        file_path_list.append(pdf_path)
                    else:
                        flag = 2
                        break
                else:
                    flag = 2
                    break
        return {"flag": flag, "file_path_list": file_path_list}

