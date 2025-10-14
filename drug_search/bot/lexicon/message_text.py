class MessageTemplates:
    HELLO: str = "💊 Привет! Напиши любой препарат, а я тебе пришлю его характеристику."

    QUERY_IN_PROCESS: str = "<b>Идёт обработка запроса...</b>"

    # [drug sections]
    DRUG_INFO_BRIEFLY: str = (
        "<b>{drug_name_ru} ({drug_name}, {latin_name})</b>\n\n"
        "<i>({classification})</i>\n\n"
        "{description}\n\n"
        "<b>Клинические эффекты:</b>\n{clinical_effects}\n\n"
        "{fun_fact}"
    )

    DRUG_INFO_PATHWAYS: str = (
        "<b>{drug_name_ru} механизм действия {sources_section}</b>\n\n"
        "<b>Основное действие: </b>\n{primary_action}\n\n"
        "{secondary_actions_section}"
        "<b>┫Пути активации:</b>"
        "{pathways_list}\n"
    )

    DRUG_INFO_COMBINATIONS: str = (
        "<b>{drug_name_ru} комбинации.</b>\n\n"
        "<b>Полезные комбинации:</b>\n{good_combinations}\n"
        "<b>Опасные комбинации:</b>\n{bad_combinations}"
    )

    DRUG_INFO_DOSAGES: str = (
        "<b>{drug_name_ru} дозировки {sources_section}</b>\n\n"
        "{dosages_list}"
        "{dosage_fun_fact_section}"
    )

    DRUG_INFO_METABOLISM: str = (
        "<b>{drug_name_ru} метаболизм.</b>\n\n"
        "{metabolism_description}"
        "{pharmacokinetics}"
    )

    DRUG_INFO_RESEARCHES: str = (
        "<b>{drug_name_ru} исследования.</b>\n\n"
        "{researches_list}"
    )

    DRUGS_ANALOGS: str = (
        "<b>{drug_name_ru} аналоги.</b>\n\n"
        "{analogs_description}"
        "{analogs_section}"
    )

    # [menu]
    USER_PROFILE: str = (
        "<b>{profile_icon} Твой профиль</b>\n\n"
        "<b>Осталось запросов сегодня:</b>\n"
        "    Поиск препаратов: <u>{allowed_search_requests}</u>\n"
        "    Вопросы: <u>{allowed_question_requests}</u>\n\n"
        "{refresh_section}\n\n"
        "{subscription_section}"
        "{description_section}"
    )

    DRUG_UPDATE_INFO: str = (
        "{drug_name}\n\n"
        "Последнее обновление препарата: {drug_last_update}\n"
    )

    DRUGS_INFO: str = (
        "<b>Все ваши препараты расположены на этой странице!</b>\n\n"
        "Всего препаратов в вашей <b>базе:</b> {len_allowed_drugs}"
    )

    # [drug actions]
    DRUG_BUY_REQUEST: str = (
        "<b>Препарата {drug_name_ru} нет в вашей базе.</b>\n\n"
        "<b>Стоимость:</b>\n"
        "   1 поисковый токен\n"
    )

    NOT_EXIST_DRUG: str = (
        "<b>Такого препарата не существует.</b>"
    )

    DRUG_BUY_ALLOWED: str = (
        "<b>Теперь препарат {drug_name} доступен в базе!</b>"
    )

    DRUG_BUY_CREATED: str = (
        "Вы приобрели препарат.\n\n"
        "Скоро вы получите уведомление о его готовности!"
    )

    NOT_ENOUGH_SEARCH_TOKENS: str = (
        "У вас недостаточно токенов для покупки.\n\n"
        "Пополнить: /tokens"
    )

    NOT_ENOUGH_QUESTION_TOKENS: str = (
        "У вас недостаточно токенов для вопросов.\n\n"
        "Пополнить: /tokens"
    )

    NEED_SUBSCRIPTION: str = (
        "Для просмотра запрещенных препаратов необходима подписка.\n\n"
        "Оформить подписку: /subscription"
    )

    DRUG_IS_BANNED: str = (
        "К сожалению, распространять информацию про нелегальные препараты запрещено законами РФ. "
        "Запрос отклонён."
    )
