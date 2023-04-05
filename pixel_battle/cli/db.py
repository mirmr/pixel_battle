from click import group, option, echo


@group("db")
def db() -> None:
    """
    Group for managing db
    """
    pass


@db.command()
def shell() -> None:
    """
    Connect to db via shell
    """
    from os import environ
    from subprocess import run
    from pixel_battle.config import app_config

    psql_path = environ.get("PSQL_PATH")
    if not psql_path:
        psql_path = "/usr/bin/psql"

    environ["PGPASSWORD"] = app_config.db.password

    args = [
        psql_path,
        "-h",
        app_config.db.host,
        "-p",
        str(app_config.db.port),
        "-U",
        app_config.db.user,
        "-d",
        app_config.db.dbname,
    ]
    echo(f"Connecting to {args}")
    run(args)


@db.command()
@option("-m", "--message", "message", required=True, type=str)
def migrate(message: str) -> None:
    """
    Create new migration
    """
    from alembic import command
    from pixel_battle.db.alembic.utils import get_alembic_config

    alembic_config = get_alembic_config()
    command.revision(alembic_config, message=message, autogenerate=True)


@db.command()
@option("-r", "--revision", "revision", type=str, required=False, default="head", show_default=True)
def upgrade(revision: str) -> None:
    """
    Upgrade db revision
    """
    from alembic import command

    from pixel_battle.db.alembic.utils import get_alembic_config

    alembic_config = get_alembic_config()
    command.upgrade(alembic_config, revision)


@db.command()
@option("-r", "--revision", "revision", type=str, required=False, default="-1", show_default=True)
def downgrade(revision: str) -> None:
    """
    Downgrade db revision
    """
    from alembic import command

    from pixel_battle.db.alembic.utils import get_alembic_config

    alembic_config = get_alembic_config()
    command.downgrade(alembic_config, revision)
