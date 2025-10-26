class ButtonText:
    # [ REPLY ]
    DRUG_DATABASE = "База препаратов"
    PROFILE = "Профиль"
    HELP = "Что умеет бот?"

    BUY_SUBSCRIPTION = "Купить подписку"  # TODO: при покупке высылать сообщение с новой REPLY клавиатурой
    UPGRADE_SUBSCRIPTION = "Улучшить подписку"

    # [ INLINE ]
    BUY_DRUG = "Купить"
    FULL_LIST = "Полный список"
    SHOW_DESCRIPTION = "Показать описание профиля"

    # [ DRUGS SECTION ]
    DOSAGES = "Дозировки"
    METABOLISM = "Метаболизм"
    COMBINATIONS = "Комбинации"
    ANALOGS = "Аналоги"
    MECHANISM = "Механизм действия | Пути активации"
    RESEARCHES = "Научные исследования"

    WRONG_DRUG_FOUNDED = "Найден не тот препарат"

    UPDATE_DRUG = "Обновить препарат (стоит 1 запрос)"
    UPDATE_DRUG_FOR_PREMIUM = "Обновить препарат"

    UPDATE_RESEARCHES = "Загрузить исследования"

    # [ ARROWS ]
    LEFT_ARROW: str = "<——"
    RIGHT_ARROW: str = "——>"

    # [ HELP ]
    HELP_QUERIES = "Запросы"
    HELP_TOKENS = "Токены"
    HELP_SUBSCRIPTION = "Подписка"

    HELP_QUERIES_QUESTIONS = "Вопросы по фарме"
    HELP_QUERIES_PHARMA = "Фарм рекомендации"
    HELP_QUERIES_DRUG_SEARCH = "Поиск препаратов"

    HELP_TOKENS_FREE = "Как получать токены?"
