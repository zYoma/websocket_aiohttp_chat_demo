import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
# IMPORTANT: Gino() objects for target_metadata should only be imported from models!

from config.models.chat_models import db

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

config.set_section_option('test_db', "sqlalchemy.url", os.getenv("TEST_DB_URL", ""))
config.set_section_option('gafuk_chat_db', "sqlalchemy.url",os.getenv("CHAT_DB_URL"))

fileConfig(config.config_file_name)

target_metadata = db

# USAGE: alembic -x db=db_name ...
cmd_kwargs = context.get_x_argument(as_dictionary=True)
db_name = cmd_kwargs.get('db')


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
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    alembic_cfg = config.get_section(config.config_ini_section)
    db_config = config.get_section(db_name)

    for key in db_config:
        alembic_cfg[key] = db_config[key]

    connectable = engine_from_config(
        alembic_cfg,
        prefix='sqlalchemy.',
        poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
