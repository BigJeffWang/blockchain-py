import sys
import time
from pathlib import Path
from sqlalchemy import or_

pro_name = "TokenPark"
current_path = str(Path(__file__).resolve())
import_index = current_path.rfind(pro_name)
import_path = current_path[:import_index + len(pro_name)]
path_flag = True if not import_path in sys.path else False
if path_flag:
    sys.path.append(import_path)


from tools.mysql_tool import MysqlTools
from models.announcement_manage_model import AnnouncementManageModel


class BannerScanScript(object):

    def banner_scan(self):
        now = int(time.time())
        time_struct = time.localtime(now)
        str_time = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)
        with MysqlTools().session_scope() as session:
            banner_list = session.query(AnnouncementManageModel). \
                filter(AnnouncementManageModel.status == 0).all()
            if len(banner_list) > 0:
                for banner in banner_list:
                    if str(banner.auto_online) <= str_time:
                        banner.status = 1
                session.commit()


if __name__ == "__main__":
    BannerScanScript().banner_scan()

