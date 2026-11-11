"""Application configuration loading, without enabling destructive test tools."""

import os
from pathlib import Path

from dotenv import dotenv_values

ROOT_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"


def load_application_env(path: Path = ROOT_ENV_PATH) -> None:
    for name, value in dotenv_values(path).items():
        # Live test authorization must be explicit in the invoking shell,
        # never inherited from a production application configuration file.
        if name != "TEST_DATABASE_URL" and value is not None:
            os.environ.setdefault(name, value)
