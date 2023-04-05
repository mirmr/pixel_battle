from yaml import safe_load

from pixel_battle.config.app import AppConfig

with open(f"config/config.yaml", "r") as fin:
    _app_config = safe_load(fin)


app_config = AppConfig(**_app_config)
