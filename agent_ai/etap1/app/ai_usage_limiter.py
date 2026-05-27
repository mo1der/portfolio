# app/ai_usage_limiter.py

from datetime import date


class AIUsageLimiter:
    def __init__(self):
        self.current_day = date.today()
        self.request_count = 0

    def can_use_ai(self, daily_limit: int) -> bool:
        self._reset_if_new_day()
        return self.request_count < daily_limit

    def register_ai_request(self) -> None:
        self._reset_if_new_day()
        self.request_count += 1

    def get_usage(self) -> dict:
        self._reset_if_new_day()
        return {
            "date": str(self.current_day),
            "request_count": self.request_count,
        }

    def _reset_if_new_day(self) -> None:
        today = date.today()

        if today != self.current_day:
            self.current_day = today
            self.request_count = 0


ai_usage_limiter = AIUsageLimiter()