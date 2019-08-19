from PIL import Image
from io import BytesIO
import io
import datetime
import uuid
from config import get_config


# 压缩图片
def pied_piper(file_read):
    im = Image.open(BytesIO(file_read))
    # print('格式', im.format, '，分辨率', im.size, '，色彩', im.mode)
    w = im.size[0]  # 宽
    h = im.size[1]  # 高
    new_w = 130
    new_h = new_w / (w / h)
    im.thumbnail((new_w, new_h))
    imgByteArr = io.BytesIO()
    im.save(imgByteArr, format='png')
    # im.save('thumb\\' + ImgName, 'JPEG', quality=90)
    return imgByteArr.getvalue()


# 生成新的路径
def create_photo_path(format):
    date = now_date()
    year = date["year"]
    month = date["month"]
    day = date["day"]
    uid = str(uuid.uuid4())
    suid = ''.join(uid.split('-'))
    conf = get_config()
    env = conf["env"]
    if env == "dev" or env == "test":
        prefix = "test/"
    elif env == "pd":
        prefix = "image/"
    path = prefix + year + "-" + month + "/" + year + "-" + month + "-" + day + "/" + suid + "." + format
    return path


# 获取当前年月日
def now_date():
    year = datetime.datetime.utcnow().year
    month = datetime.datetime.utcnow().month
    day = datetime.datetime.utcnow().day
    date = {"year": str(year), "month": str(month), "day": str(day)}
    return date
