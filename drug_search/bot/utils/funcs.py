from datetime import datetime, timedelta

from aiogram.types import User

from drug_search.core.lexicon import SUBSCRIPTION_TYPES, TOKENS_LIMIT
from drug_search.core.schemas import UserTelegramDataSchema


def make_google_sources(sources: list[str]) -> list[dict]:
    """Возвращает ссылки на поиск гугл различных источников"""
    return [
        {
            "source_name": source,
            "google_url": f'https://www.google.com/search?q={source.replace("'", "").replace('"', "")}'
        }
        for source in sources
    ]


def get_subscription_name(subscription_type: SUBSCRIPTION_TYPES):
    match subscription_type:
        case SUBSCRIPTION_TYPES.DEFAULT:
            return "нет"
        case SUBSCRIPTION_TYPES.LITE:
            return "стандарт"
        case SUBSCRIPTION_TYPES.PREMIUM:
            return "премиум"


def days_text(day: datetime):
    """Преобразование datetime.days в русскоязычные дни"""
    days = (day - datetime.now()).days
    return f"{days} день" if days % 10 == 1 and days % 100 != 11 \
        else f"{days} дня" if 2 <= days % 10 <= 4 and (days % 100 < 10 or days % 100 >= 20) \
        else f"{days} дней"


def get_time_when_refresh_tokens_text(_datetime: datetime, subscription_type: SUBSCRIPTION_TYPES) -> str:
    """Время до сброса токенов"""
    def __get_time_name_format(count: int, time_type: str) -> str:
        """Преобразование числа в русскоязычный формат времени"""
        forms = {
            "minutes": ("минуту", "минуты", "минут"),
            "hours": ("час", "часа", "часов"),
            "days": ("день", "дня", "дней")
        }[time_type]

        if count % 10 == 1 and count % 100 != 11:
            return forms[0]
        elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
            return forms[1]
        else:
            return forms[2]

    text: str = "<b>⏳ Сброс токенов через:</b> {time_to_update} {time_format}"

    refresh_tokens_days_interval: int = TOKENS_LIMIT.get_days_interval_to_refresh_tokens(subscription_type=subscription_type)
    time_diff: timedelta = (_datetime + timedelta(days=refresh_tokens_days_interval)) - datetime.now()
    if time_diff <= timedelta(hours=1):
        time_to_update: int = time_diff.seconds // 60
        return text.format(
            time_to_update=time_to_update,
            time_format=__get_time_name_format(time_to_update, "minutes")
        )
    elif time_diff <= timedelta(hours=24):
        time_to_update: int = time_diff.seconds // 60 // 60
        return text.format(
            time_to_update=time_to_update,
            time_format=__get_time_name_format(time_to_update, "hours")
        )
    else:
        time_to_update: int = time_diff.days
        return text.format(
            time_to_update=time_to_update,
            time_format=__get_time_name_format(time_to_update, "days")
        )


async def get_telegram_schema_from_data(user: User) -> UserTelegramDataSchema:
    return UserTelegramDataSchema(
        telegram_id=str(user.id),
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        auth_date=None
    )


def format_time(seconds: int) -> str:
    """
    Форматирует время в строку с правильным склонением

    Args:
        seconds: количество секунд

    Returns:
        Строка с правильным склонением (например: "13 секунд", "1 секунду", "2 минуты")
    """

    def _format_seconds(seconds: int) -> str:
        """Форматирует секунды"""
        if seconds % 10 == 1 and seconds % 100 != 11:
            return f"{seconds} секунду"  # винительный падеж для "через"
        elif 2 <= seconds % 10 <= 4 and (seconds % 100 < 10 or seconds % 100 >= 20):
            return f"{seconds} секунды"  # винительный падеж для "через"
        else:
            return f"{seconds} секунд"  # родительный падеж для "через"

    def _format_minutes(minutes: int) -> str:
        """Форматирует минуты"""
        if minutes % 10 == 1 and minutes % 100 != 11:
            return f"{minutes} минуту"  # винительный падеж для "через"
        elif 2 <= minutes % 10 <= 4 and (minutes % 100 < 10 or minutes % 100 >= 20):
            return f"{minutes} минуты"  # винительный падеж для "через"
        else:
            return f"{minutes} минут"  # родительный падеж для "через"

    def _format_hours(hours: int) -> str:
        """Форматирует часы"""
        if hours % 10 == 1 and hours % 100 != 11:
            return f"{hours} час"  # винительный падеж для "через"
        elif 2 <= hours % 10 <= 4 and (hours % 100 < 10 or hours % 100 >= 20):
            return f"{hours} часа"  # винительный падеж для "через"
        else:
            return f"{hours} часов"  # родительный падеж для "через"

    def _format_days(days: int) -> str:
        """Форматирует дни"""
        if days % 10 == 1 and days % 100 != 11:
            return f"{days} день"  # винительный падеж для "через"
        elif 2 <= days % 10 <= 4 and (days % 100 < 10 or days % 100 >= 20):
            return f"{days} дня"  # винительный падеж для "через"
        else:
            return f"{days} дней"  # родительный падеж для "через"

    if seconds < 60:
        return _format_seconds(seconds)
    elif seconds < 3600:
        minutes = seconds // 60
        return _format_minutes(minutes)
    elif seconds < 86400:
        hours = seconds // 3600
        return _format_hours(hours)
    else:
        days = seconds // 86400
        return _format_days(days)


def format_rate_limit(message_count: int, interval_seconds: int) -> str:
    """
    Форматирует лимит сообщений в строку типа 'X сообщений/сутки' или 'X сообщений/час'

    Args:
        message_count: количество сообщений
        interval_seconds: интервал в секундах

    Returns:
        Строка с лимитом (например: "5 сообщений/сутки", "3 сообщения/час", "11 сообщений/минуту")
    """
    # Форматируем количество сообщений
    if message_count % 10 == 1 and message_count % 100 != 11:
        message_text = f"{message_count} сообщение"
    elif 2 <= message_count % 10 <= 4 and (message_count % 100 < 10 or message_count % 100 >= 20):
        message_text = f"{message_count} сообщения"
    else:
        message_text = f"{message_count} сообщений"

    # Форматируем интервал времени
    if interval_seconds < 60:
        # Секунды
        if interval_seconds == 1:
            interval_text = "секунду"
        elif interval_seconds % 10 == 1 and interval_seconds % 100 != 11:
            interval_text = f"{interval_seconds} секунду"
        elif 2 <= interval_seconds % 10 <= 4 and (interval_seconds % 100 < 10 or interval_seconds % 100 >= 20):
            interval_text = f"{interval_seconds} секунды"
        else:
            interval_text = f"{interval_seconds} секунд"

    elif interval_seconds < 3600:
        # Минуты
        minutes = interval_seconds // 60
        if minutes == 1:
            interval_text = "минуту"
        elif minutes % 10 == 1 and minutes % 100 != 11:
            interval_text = f"{minutes} минуту"
        elif 2 <= minutes % 10 <= 4 and (minutes % 100 < 10 or minutes % 100 >= 20):
            interval_text = f"{minutes} минуты"
        else:
            interval_text = f"{minutes} минут"

    elif interval_seconds < 86400:
        # Часы
        hours = interval_seconds // 3600
        if hours == 1:
            interval_text = "час"
        elif hours % 10 == 1 and hours % 100 != 11:
            interval_text = f"{hours} час"
        elif 2 <= hours % 10 <= 4 and (hours % 100 < 10 or hours % 100 >= 20):
            interval_text = f"{hours} часа"
        else:
            interval_text = f"{hours} часов"

    else:
        # Дни
        days = interval_seconds // 86400
        if days == 1:
            interval_text = "сутки"
        elif days % 10 == 1 and days % 100 != 11:
            interval_text = f"{days} сутки"
        elif 2 <= days % 10 <= 4 and (days % 100 < 10 or days % 100 >= 20):
            interval_text = f"{days} суток"
        else:
            interval_text = f"{days} суток"

    return f"{message_text}/{interval_text}"


def decline_tokens(count: int) -> str:
    """
    Склоняет слово 'токен' в зависимости от числа.

    Args:
        count (int): Количество токенов

    Returns:
        str: Склоненное слово 'токен'
    """
    if count % 10 == 1 and count % 100 != 11:
        return "токен"
    elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
        return "токена"
    else:
        return "токенов"


def what_subscription(subscription: SUBSCRIPTION_TYPES):
    match subscription:
        case SUBSCRIPTION_TYPES.DEFAULT:
            return "Без подписки"
        case SUBSCRIPTION_TYPES.LITE:
            return "Лайт"
        case SUBSCRIPTION_TYPES.DEFAULT:
            return "Премиум"
