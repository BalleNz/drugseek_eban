from dataclasses import dataclass

from drug_search.core.services.cache_logic.redis_service import RedisService


@dataclass
class QuizStats:
    streak: int
    best_streak: int


class GamificationService:
    STREAK_TTL = 60 * 60 * 48

    def __init__(self, redis_service: RedisService):
        self.redis = redis_service.redis

    @staticmethod
    def _streak_key(telegram_id: str) -> str:
        return f"gamification:{telegram_id}:quiz_streak"

    @staticmethod
    def _best_key(telegram_id: str) -> str:
        return f"gamification:{telegram_id}:quiz_best"

    async def get_quiz_stats(self, telegram_id: str) -> QuizStats:
        streak_raw = await self.redis.get(self._streak_key(telegram_id))
        best_raw = await self.redis.get(self._best_key(telegram_id))
        streak = int(streak_raw or 0)
        best = int(best_raw or 0)
        return QuizStats(streak=streak, best_streak=max(best, streak))

    async def record_quiz_answer(self, telegram_id: str, is_correct: bool) -> QuizStats:
        streak_key = self._streak_key(telegram_id)
        best_key = self._best_key(telegram_id)

        if is_correct:
            streak = int(await self.redis.incr(streak_key))
            await self.redis.expire(streak_key, self.STREAK_TTL)
            best = int(await self.redis.get(best_key) or 0)
            if streak > best:
                await self.redis.set(best_key, streak)
                best = streak
        else:
            await self.redis.set(streak_key, 0, ex=self.STREAK_TTL)
            streak = 0
            best = int(await self.redis.get(best_key) or 0)

        return QuizStats(streak=streak, best_streak=best)
