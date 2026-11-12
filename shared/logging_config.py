import logging.config
from pathlib import Path

import yaml

def configure_logging():
    config_path = (
        Path(__file__).resolve().parents[1]
        / "config"
        / "logging.yaml"
    )

    with config_path.open("r") as file:
        config = yaml.safe_load(file)

    logging.config.dictConfig(config)

