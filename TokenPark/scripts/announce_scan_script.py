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


class AnnounceScanScript(object):

    def announce_scan(self):
        now = int(time.time())
        time_struct = time.localtime(now)
        str_time = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)
        with MysqlTools().session_scope() as session:
            announce_list = session.query(AnnouncementManageModel). \
                filter(or_(AnnouncementManageModel.status == 0,
                           AnnouncementManageModel.status == 1)).all()
            # print("len(announce_list)===", len(announce_list))
            # print("str_time===", str_time)
            if len(announce_list) > 0:
                for announce in announce_list:
                    # print("announce.auto_online===", announce.auto_online)
                    # print("announce.auto_offline===", announce.auto_offline)
                    if announce.status == 0:
                        if str(announce.auto_online) <= str_time:
                            announce.status = 1
                    else:
                        if str(announce.auto_offline) <= str_time:
                            announce.status = 2
                session.commit()


if __name__ == "__main__":
    AnnounceScanScript().announce_scan()

