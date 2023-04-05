import os.path

from alembic.config import Config


def get_alembic_config() -> Config:
    config_file_location = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(config_file_location, "alembic.ini")
    alembic_config = Config(config_file)
    return alembic_config
