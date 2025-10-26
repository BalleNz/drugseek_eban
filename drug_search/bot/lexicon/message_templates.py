class MessageTemplates:
    """Шаблоны сообщений с форматированием"""
    # [ SECTIONS ]
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

    USER_PROFILE: str = (
        "<b>{profile_icon} Твой профиль</b>\n\n"
        "<b>Осталось запросов сегодня:</b>\n"
        "   — Поиск препаратов: <u>{allowed_search_requests}</u>\n"
        "   — Вопросы: <u>{allowed_question_requests}</u>\n\n"
        "{refresh_section}\n\n"
        "{subscription_section}"
    )

    USER_PROFILE_DESCRIPTION: str = (
        "<b>{profile_icon} Твоё описание</b>\n\n"
        "{description_section}"
    )

    DRUG_UPDATE_INFO: str = (
        "{drug_name}\n\n"
        "Последнее обновление препарата: {drug_last_update}\n"
    )

    DRUGS_INFO: str = (
        "<b>📫 Все ваши препараты расположены на этой странице!</b>\n\n"
        "Сейчас в вашей базе {len_allowed_drugs} препаратов."
    )

    # [ ACTIONS ]
    DRUG_BUY_REQUEST: str = (
        "<b>Препарата {drug_name_ru} нет в вашей базе.</b>\n\n"
        "<b>Стоимость:</b>\n"
        "   1 поисковый токен\n"
    )

    DRUG_BUY_ALLOWED: str = (
        "<b>Теперь препарат {drug_name} доступен в базе!</b>"
    )

    # [ antispam ]
    ANTISPAM_MESSAGE = (
        "⚠️ <b>Лимит сообщений превышен!</b>\n\n"
        "Следующее сообщение можно отправить через:\n"
        "— <b>{time_left}</b>\n\n"
        "⚡ Текущий тариф:\n"
        "— <u>{what_subscription}</u>, {message_rate}"
    )

    # [ Message Limits ]
    MESSAGE_LENGTH_EXCEED = (
        "⚠️ <b>Превышена длина сообщения!</b>\n\n"
        "Для людей <b>{subscription_info}</b> разрешено использовать {max_message_len} символов."
    )
