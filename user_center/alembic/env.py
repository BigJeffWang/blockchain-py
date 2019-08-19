from __future__ import with_statement

import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

sys.path.append(str(Path(__file__).resolve().parent.parent))

import config as cf

from models import base_model
from models import __alembic__

__alembic__.call_dynamic()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None
# 读取平台所属配置文件的关键字段！！！！！！！


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """

    mysql_conf = cf.get_mysql_config()
    config.set_main_option('sqlalchemy.url',
                           'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8mb4' % (
                               mysql_conf['user'], mysql_conf['password'], mysql_conf['host'], mysql_conf['port'],
                               mysql_conf['db']))
    target_metadata = base_model.BaseModel.metadata

    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    mysql_conf = cf.get_mysql_config()
    config.set_main_option('sqlalchemy.url',
                           'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8mb4' % (
                               mysql_conf['user'], mysql_conf['password'], mysql_conf['host'], mysql_conf['port'],
                               mysql_conf['db']))
    target_metadata = base_model.BaseModel.metadata

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()