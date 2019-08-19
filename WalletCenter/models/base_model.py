import datetime
import uuid
from decimal import Decimal

from sqlalchemy import Column, BigInteger, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    _id = Column(BigInteger, primary_key=True, autoincrement=True, comment="内置索引")
    created_at = Column(DateTime, nullable=False, server_default="0000-00-00 00:00:00", comment="创建时间")
    update_at = Column(DateTime, onupdate=datetime.datetime.now, nullable=False, server_default="0000-00-00 00:00:00", comment="修改时间")
    deleted_at = Column(DateTime, nullable=False, server_default="0000-00-00 00:00:00", comment="删除时间")
    deleted = Column(Boolean, nullable=False, default=0, server_default="0", comment="假删除 True为已删除")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.created_at = datetime.datetime.now()
        self.update_at = datetime.datetime.now()

    def save(self, session):
        session.add(self)
        session.commit()
        return True

    def delete(self, session):
        self.deleted = True
        self.deleted_at = datetime.datetime.now()
        session.commit()

    def dump_to_dict(self, args=None):
        ret = {}
        if args is None:
            args = self.__table__.columns.keys()
        for name in self.__table__.columns.keys():
            if name in args:
                if isinstance(getattr(self, name), datetime.datetime):
                    ret[name] = str(getattr(self, name))
                elif isinstance(getattr(self, name), Decimal):
                    ret[name] = float(getattr(self, name))
                else:
                    ret[name] = getattr(self, name)
        return ret

    def set_by_dict(self, args):
        keys = self.__table__.columns.keys()
        for k in args:
            if k not in keys:
                raise Exception("set a unknown key:%s" % k)
            setattr(self, k, args[k])

    @staticmethod
    def uuid():
        return uuid.uuid4().hex
