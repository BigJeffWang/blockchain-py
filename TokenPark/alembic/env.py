from __future__ import with_statement

import sys
from pathlib import Path
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

sys.path.append(str(Path(__file__).resolve().parent.parent))

from tools.mysql_tool import MysqlTools
from models import base_model
from models import __alembic__

__alembic__.call_dynamic()
config = context.config
fileConfig(config.config_file_name)

connect_string = MysqlTools().get_connect_string()
config.set_main_option('sqlalchemy.url', connect_string)
target_metadata = base_model.BaseModel.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
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
