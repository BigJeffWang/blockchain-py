""" Base Model

The base model which is abstract class.

Includes:

.. Class ..

BaseModel: implement the base model inherits from sqlalchemy declarativae_base.

.. Function ..

dump_to_dict: dump sql query results to dict.

"""

import datetime
import uuid
from decimal import Decimal

from sqlalchemy import Column, BigInteger, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# 所有删除必须走 delete方法


class BaseModel(Base):
    __abstract__ = True

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, server_default="0000-00-00 00:00:00")
    update_at = Column(DateTime, onupdate=datetime.datetime.now, nullable=False, server_default="0000-00-00 00:00:00")
    deleted_at = Column(DateTime, nullable=False, server_default="0000-00-00 00:00:00")
    deleted = Column(Boolean, nullable=False, server_default="0")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.created_at = datetime.datetime.now()
        self.update_at = self.created_at

    def delete(self, session):
        self.deleted = True
        self.deleted_at = datetime.datetime.now()

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

