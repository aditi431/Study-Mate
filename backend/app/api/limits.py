from collections import deque
from datetime import date, datetime, timezone
from threading import Lock
import time

from fastapi import HTTPException, Request

from app.config import Settings

DAILY_LIMIT_MESSAGE = "Daily AI limit reached, try again tomorrow"
RATE_LIMIT_MESSAGE = "Too many AI requests. Please wait a minute and try again."


class InMemoryAiLimitTracker:
    def __init__(self) -> None:
        self._lock = Lock()
        self._requests_by_ip: dict[str, deque[float]] = {}
        self._daily_usage: dict[tuple[str, date], int] = {}
        self._usage_date: date | None = None
        self._last_ip_cleanup = 0.0

    def check_and_record(
        self,
        *,
        ip_address: str,
        user_id: str,
        is_demo_user: bool,
        settings: Settings,
    ) -> None:
        now = time.monotonic()
        today = datetime.now(timezone.utc).date()
        daily_limit = (
            settings.demo_ai_daily_limit_per_user
            if is_demo_user
            else settings.ai_daily_limit_per_user
        )

        with self._lock:
            if now - self._last_ip_cleanup >= 60:
                for address, requests in list(self._requests_by_ip.items()):
                    while requests and requests[0] <= now - 60:
                        requests.popleft()
                    if not requests:
                        del self._requests_by_ip[address]
                self._last_ip_cleanup = now

            if self._usage_date != today:
                self._daily_usage.clear()
                self._usage_date = today

            recent_requests = self._requests_by_ip.get(ip_address)
            if recent_requests is None:
                recent_requests = deque()
                self._requests_by_ip[ip_address] = recent_requests
            while recent_requests and recent_requests[0] <= now - 60:
                recent_requests.popleft()
            if not recent_requests:
                recent_requests = deque()
                self._requests_by_ip[ip_address] = recent_requests

            if len(recent_requests) >= settings.ai_rate_limit_per_minute:
                raise HTTPException(status_code=429, detail=RATE_LIMIT_MESSAGE)

            daily_key = (user_id, today)
            if self._daily_usage.get(daily_key, 0) >= daily_limit:
                raise HTTPException(status_code=429, detail=DAILY_LIMIT_MESSAGE)

            recent_requests.append(now)
            self._daily_usage[daily_key] = self._daily_usage.get(daily_key, 0) + 1

    def reset(self) -> None:
        with self._lock:
            self._requests_by_ip.clear()
            self._daily_usage.clear()
            self._usage_date = None
            self._last_ip_cleanup = 0


ai_limit_tracker = InMemoryAiLimitTracker()


def enforce_ai_limits(
    request: Request,
    user_id: str,
    is_demo_user: bool,
    settings: Settings,
) -> None:
    ip_address = request.client.host if request.client is not None else "unknown"
    ai_limit_tracker.check_and_record(
        ip_address=ip_address,
        user_id=user_id,
        is_demo_user=is_demo_user,
        settings=settings,
    )
