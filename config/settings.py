"""Framework configuration.

Values come from environment variables:
  - locally, loaded from the .env file
  - in CI, provided by GitHub Secrets
Nothing (URLs, credentials) is hard-coded anywhere else in the framework.
"""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()  # copies values from .env into environment variables (if the file exists)


def _required(name: str) -> str:
    """Return an env variable's value, or stop with a clear error if it's missing."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing environment variable '{name}'. "
            f"Copy .env.example to .env and fill it in."
        )
    return value


@dataclass(frozen=True)
class Settings:
    ui_base_url: str
    api_base_url: str
    email: str
    password: str


settings = Settings(
    ui_base_url=os.getenv("UI_BASE_URL", "https://eventhub.rahulshettyacademy.com"),
    api_base_url=os.getenv("API_BASE_URL", "https://api.eventhub.rahulshettyacademy.com/api"),
    email=_required("EVENTHUB_EMAIL"),
    password=_required("EVENTHUB_PASSWORD"),
)