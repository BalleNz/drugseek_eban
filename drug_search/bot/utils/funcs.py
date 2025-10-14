from datetime import datetime, timedelta

from lexicon import SUBSCRIBE_TYPES


def make_google_sources(sources: list[str]) -> list[dict]:
    """Возвращает ссылки на поиск гугл различных источников"""
    return [
        {
            "source_name": source,
            "google_url": f'https://www.google.com/search?q={source.replace("'", "").replace('"', "")}'
        }
        for source in sources
    ]


def get_subscription_name(subscription_type: SUBSCRIBE_TYPES):
    match subscription_type:
        case SUBSCRIBE_TYPES.DEFAULT:
            return "нет"
        case SUBSCRIBE_TYPES.LITE:
            return "стандарт"
        case SUBSCRIBE_TYPES.PREMIUM:
            return "премиум"


def days_text(day: datetime):
    """Преобразование datetime.days в русскоязычные дни"""
    days = (day - datetime.now()).days
    return f"{days} день" if days % 10 == 1 and days % 100 != 11 \
        else f"{days} дня" if 2 <= days % 10 <= 4 and (days % 100 < 10 or days % 100 >= 20) \
        else f"{days} дней"


def get_time_when_refresh(last_update: datetime) -> str:
    def __get_time_name_format(count: int, time_type: str):
        """Преобразование datetime.hours | .minutes в русскоязычный формат"""
        if time_type == "minutes":
            if count % 10 == 1 and count % 100 != 11:
                return "минута"
            elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
                return "минуты"
            else:
                return "минут"
        elif time_type == "hours":
            if count % 10 == 1 and count % 100 != 11:
                return "час"
            elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
                return "часа"
            else:
                return "часов"

    text: str = "<i>({time_to_update} {time_format} до сброса)</i>"

    time_diff: timedelta = (last_update + timedelta(hours=24)) - datetime.now()
    if time_diff <= timedelta(hours=1):
        time_to_update: int = time_diff.seconds // 60
        return text.format(
            time_to_update=time_to_update,
            time_format=__get_time_name_format(time_to_update, "minutes")
        )
    else:
        time_to_update: int = time_diff.seconds // 60 // 60
        return text.format(
            time_to_update=time_to_update,
            time_format=__get_time_name_format(time_to_update, "hours")
        )
