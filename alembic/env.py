from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from drug_search.config import config as app_config

database_url: str = app_config.DATABASE_URL.replace("db:", "localhost:") + "?async_fallback=True"  # for not docker location
config.set_main_option("sqlalchemy.url", database_url)

from drug_search.infrastructure.database.models.base import *  # noqa
from drug_search.infrastructure.database.models.drug import *  # noqa
from drug_search.infrastructure.database.models.user import *  # noqa
from drug_search.infrastructure.database import *  # noqa

target_metadata = IDMixin.metadata
print("Tables in metadata:", list(target_metadata.tables.keys()))


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    for _ in range(2):
        url = config.get_main_option("sqlalchemy.url")
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()

        config.set_main_option("sqlalchemy.url", app_config.DATABASE_TEST_URL + "?async_fallback=True")


def run_migrations_online():
    """Run migrations in 'online' mode."""
    print("making migration on DATABASE_URL: " + database_url)

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

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
