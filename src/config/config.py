from __future__ import annotations

from dataclasses import dataclass

from dotenv import load_dotenv

from config.base import getenv


@dataclass
class TelegramBotConfig:
    token: str


@dataclass
class Config:
    tg_bot: TelegramBotConfig


def load_config() -> Config:
    """Parse a `.env` file and load the variables into environment valriables."""
    load_dotenv()

    return Config(tg_bot=TelegramBotConfig(token=getenv("BOT_TOKEN")))


DB_ADDRESS = "sqlite+aiosqlite:///db/db.sqlite"
