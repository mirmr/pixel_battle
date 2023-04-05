import click

from pixel_battle.cli.db import db
from pixel_battle.cli.server import server


@click.group()
def cli_root() -> None:
    pass


cli_root.add_command(server)
cli_root.add_command(db)
