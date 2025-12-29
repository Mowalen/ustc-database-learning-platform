from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import secrets
from app.core.time_utils import get_now, APP_TIMEZONE


@dataclass
class ResetEntry:
    code: str
    expires_at: datetime


class PasswordResetStore:
    def __init__(self, ttl_minutes: int = 10) -> None:
        self._ttl = timedelta(minutes=ttl_minutes)
        self._entries: dict[str, ResetEntry] = {}


    def issue(self, email: str) -> str:
        code = f"{secrets.randbelow(1_000_000):06d}"
        expires_at = get_now() + self._ttl
        self._entries[email.lower()] = ResetEntry(code=code, expires_at=expires_at)
        return code

    def verify(self, email: str, code: str, consume: bool = True) -> bool:
        key = email.lower()
        entry = self._entries.get(key)
        if not entry:
            return False
        if get_now() > entry.expires_at:
            self._entries.pop(key, None)
            return False
        if entry.code != code:
            return False
        if consume:
            self._entries.pop(key, None)
        return True


password_reset_store = PasswordResetStore()
