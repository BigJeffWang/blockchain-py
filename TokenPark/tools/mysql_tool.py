import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from errors.error_handler import InvalidUsageException, FundamentalErrorException
from tools.decorator_tools import FormatOutput
from utils.log import MultiProcessTimingLog, TimingLog


class MysqlTools(object):
    def __init__(self, conf=None):
        super().__init__()
        self.engine = None
        self.Session = None
        self.init_session(conf)

    @staticmethod
    def get_connect_string(conf=None):
        if not conf:
            base_conf = config.get_config()
            conf = base_conf["mysql"][base_conf["env"]]
        connect_string = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8mb4' % (
            conf['user'], conf['psd'], conf['host'], str(conf['port']), conf['db'])
        return connect_string

    @FormatOutput("tools", 10022)
    def init_session(self, conf=None):
        connect_string = self.get_connect_string(conf)
        self.engine = create_engine(connect_string)
        self.Session = sessionmaker()
        self.Session.configure(bind=self.engine)

    @contextmanager
    def session_scope(self):
        mpt = MultiProcessTimingLog()
        mpt.start()
        # TimingLog.begin()
        session = self.Session()
        try:
            yield session
        except InvalidUsageException as error:
            session.rollback()
            raise error
        except FundamentalErrorException as error:
            session.rollback()
            raise error
        except Exception as error:
            session.rollback()
            raise error
        finally:
            session.close()
            mpt.stop()
            # TimingLog.end()
