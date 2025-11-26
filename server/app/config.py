import os
from functools import lru_cache


class Settings:
    """Lightweight settings loader."""

    database_url: str

    def __init__(self) -> None:
        # Prefer environment variable, fall back to local MySQL placeholder.
        self.database_url = os.getenv(
            "DATABASE_URL", "mysql+aiomysql://root:password@localhost:3306/ustc_db"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()

