import urllib.parse

from drug_search.core.lexicon import BOT_USERNAME


def build_telegram_share_url(text: str, url: str | None = None) -> str:
    bot_url = url or f"https://t.me/{BOT_USERNAME}"
    return (
        "https://t.me/share/url?"
        f"url={urllib.parse.quote(bot_url, safe='')}"
        f"&text={urllib.parse.quote(text, safe='')}"
    )


def build_drug_share_text(drug_name_ru: str, drug_name: str) -> str:
    return (
        f"💊 Разобрал препарат «{drug_name_ru}» ({drug_name}) в DrugSearch!\n"
        f"Полная карточка: механизм, дозировки, комбинации — всё в одном боте."
    )


def build_quiz_share_text(streak: int, level_title: str, best_streak: int) -> str:
    return (
        f"🧠 Я угадываю препараты по описанию в DrugSearch!\n"
        f"Серия: {streak} · Рекорд: {best_streak} · Статус: {level_title}\n"
        f"Сможешь побить? Заходи в викторину 👇"
    )
