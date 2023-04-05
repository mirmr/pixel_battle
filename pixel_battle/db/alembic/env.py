from alembic import context
from sqlalchemy import engine_from_config, pool

from pixel_battle.config import app_config
from pixel_battle.db.tables import meta

config = context.config
target_metadata = meta


def run_migrations_offline() -> None:
    context.configure(url=app_config.db.url, target_metadata=meta, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


config.set_main_option("sqlalchemy.url", app_config.db.url)

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
