from dataclasses import dataclass


@dataclass
class PharmaLevel:
    title: str
    emoji: str
    min_best_streak: int


PHARMA_LEVELS: tuple[PharmaLevel, ...] = (
    PharmaLevel("Стажёр", "💉", 0),
    PharmaLevel("Фармацевт", "💊", 3),
    PharmaLevel("Биохимик", "🧬", 7),
    PharmaLevel("Pharma Legend", "🏆", 15),
)


def get_pharma_level(best_streak: int) -> PharmaLevel:
    current = PHARMA_LEVELS[0]
    for level in PHARMA_LEVELS:
        if best_streak >= level.min_best_streak:
            current = level
    return current


def format_level_badge(best_streak: int) -> str:
    level = get_pharma_level(best_streak)
    return f"{level.emoji} {level.title}"
