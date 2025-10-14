from datetime import timedelta, datetime, timezone

from drug_search.config import config


def may_update_drug(last_update: datetime) -> bool:
    """Проверяет, прошло ли более MIN_DAYS_TO_UPDATE_DRUG дней с последнего обновления препарата"""
    # Приводим оба времени к одному типу timezone.utc
    now_utc = datetime.now(timezone.utc)
    threshold = now_utc - timedelta(days=config.constants.MIN_DAYS_TO_UPDATE_DRUG)

    # Приводим last_update к тому же типу tzinfo
    if last_update.tzinfo != timezone.utc:
        last_update_normalized = last_update.astimezone(timezone.utc)
    else:
        last_update_normalized = last_update

    return last_update_normalized < threshold


def layout_converter(text: str) -> str:
    """
    Автоматически определяет раскладку и конвертирует в противоположную
    """

    def convert_layout(text: str, from_layout: str = 'en', to_layout: str = 'ru') -> str:
        """
        Конвертирует текст между русской и английской раскладками

        Args:
            text: исходный текст
            from_layout: 'en' или 'ru' - исходная раскладка
            to_layout: 'en' или 'ru' - целевая раскладка
        """
        # Соответствия клавиш
        en_to_ru = {
            'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е', 'y': 'н', 'u': 'г',
            'i': 'ш', 'o': 'щ', 'p': 'з', '[': 'х', ']': 'ъ', 'a': 'ф', 's': 'ы',
            'd': 'в', 'f': 'а', 'g': 'п', 'h': 'р', 'j': 'о', 'k': 'л', 'l': 'д',
            ';': 'ж', "'": 'э', 'z': 'я', 'x': 'ч', 'c': 'с', 'v': 'м', 'b': 'и',
            'n': 'т', 'm': 'ь', ',': 'б', '.': 'ю', '/': '.',
            'Q': 'Й', 'W': 'Ц', 'E': 'У', 'R': 'К', 'T': 'Е', 'Y': 'Н', 'U': 'Г',
            'I': 'Ш', 'O': 'Щ', 'P': 'З', '{': 'Х', '}': 'Ъ', 'A': 'Ф', 'S': 'Ы',
            'D': 'В', 'F': 'А', 'G': 'П', 'H': 'Р', 'J': 'О', 'K': 'Л', 'L': 'Д',
            ':': 'Ж', '"': 'Э', 'Z': 'Я', 'X': 'Ч', 'C': 'С', 'V': 'М', 'B': 'И',
            'N': 'Т', 'M': 'Ь', '<': 'Б', '>': 'Ю', '?': ','
        }

        ru_to_en = {v: k for k, v in en_to_ru.items()}

        if from_layout == 'en' and to_layout == 'ru':
            mapping = en_to_ru
        elif from_layout == 'ru' and to_layout == 'en':
            mapping = ru_to_en
        else:
            return text  # или поднять исключение

        result = []
        for char in text:
            result.append(mapping.get(char, char))

        return ''.join(result)

    # Счетчики для определения раскладки
    en_chars = set("qwertyuiop[]asdfghjkl;'zxcvbnm,./")
    ru_chars = set("йцукенгшщзхъфывапролджэячсмитьбю.")

    en_count = sum(1 for char in text if char in en_chars)
    ru_count = sum(1 for char in text if char in ru_chars)

    if en_count > ru_count:
        return convert_layout(text, 'en', 'ru')
    elif ru_count > en_count:
        return convert_layout(text, 'ru', 'en')
    else:
        return text  # неопределенно, возвращаем как есть
