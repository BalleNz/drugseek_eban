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
        "<b>🎯 {drug_name_ru} МЕХАНИЗМ ДЕЙСТВИЯ {sources_section}</b>\n\n"
        "<b>Основное действие: </b>\n{primary_action}\n\n"
        "{secondary_actions_section}"
        "<b>┫Пути активации:</b>"
        "{pathways_list}\n"
    )

    DRUG_INFO_COMBINATIONS: str = (
        "<b>🔄 {drug_name_ru} КОМБИНАЦИИ</b>\n\n"
        "💚 <b>СИНЕРГИЯ</b>\n"
        "{good_combinations}\n"
        "🚫<b> ПРОТИВОПОКАЗАННЫЕ </b>\n"
        "{bad_combinations}"
    )

    DRUG_INFO_DOSAGES: str = (
        "<b>📋 {drug_name_ru} ДОЗИРОВКИ {sources_section}</b>\n\n"
        "{dosages}"
        "{dosages_fun_fact}"
    )

    DRUG_INFO_METABOLISM: str = (
        "<b>💊 {drug_name_ru} ФАРМАКОКИНЕТИКА</b>\n\n"
        "💉 <b>ВСАСЫВАНИЕ</b>\n"
        "{absorption}\n"
        "<b>🌟 МЕТАБОЛИЗМ <a href='https://ru.wikipedia.org/wiki/%D0%9C%D0%B5%D1%82%D0%B0%D0%B1%D0%BE%D0%BB%D0%B8%D0%B7%D0%BC_%D0%BB%D0%B5%D0%BA%D0%B0%D1%80%D1%81%D1%82%D0%B2'>¹</a></b>\n"
        "{metabolism}\n"
        "<b>📤 ВЫВЕДЕНИЕ</b>\n"
        "{elimination}\n"
        "{metabolism_description}"
    )

    DRUG_INFO_RESEARCHES: str = (
        "<b>📊 {drug_name_ru} ИССЛЕДОВАНИЯ</b>\n\n"
        "{researches_list}"
    )

    DRUGS_ANALOGS: str = (
        "<b>⚙️ {drug_name_ru} АНАЛОГИ</b>\n\n"
        "{analogs_section}"
        "{analogs_description}"
    )

    USER_PROFILE: str = (
        "<b>{profile_name}</b>\n\n"
        "<b>Ваши токены:</b> {allowed_tokens}\n\n"
        "{refresh_section}\n\n"
        "<i>{subscription_end_at}</i>"
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

    # [ PAYMENTS ]
    TOKENS_BUY = (
        "💳 <b>Покупка токенов</b>\n\n"
        "Выбери пак: \n"
    )

    SUBSCRIPTION_BUY_CHOOSE_TYPE = (
        "💳 <b>Покупка подписки</b>\n\n"
        "Выбери тип подписки:\n"
    )

    SUBSCRIPTION_BUY_CHOOSE_DURATION = (
        "💳 <b>Покупка подписки</b>\n\n"
        "Выбери длительность подписки:\n"
    )

    SUBSCRIPTION_UPGRADE = (
        "💳 <b>Улучшение подписки</b>\n\n"
        "Текущая подписка: \n"
        "— {subscription_name} ({subscription_end})\n\n"
        "<b>Скидка на улучшение подписки:</b>\n"
        "— {subscription_discount}%"
    )

    TOKENS_BUY_CONFIRMATION = (
        "💳 <b>Покупка токенов</b>\n\n"
        "Выбранный пак: \n"
        "— {package_name} ({package_tokens} токенов)"
    )

    SUBSCRIPTION_BUY_CONFIRMATION = (
        "💳 <b>Покупка подписки</b>\n\n"
        "Выбранная подписка: \n"
        "— {subscription_name} ({subscription_period})\n\n"
        "<b>Цена:</b>\n"
        "— {subscription_price} рублей"
    )

    SUBSCRIPTION_UPGRADE_CONFIRMATION = (
        "💳 <b>Улучшение подписки</b>\n\n"
        "Выбранная подписка: \n"
        "— {subscription_name} ({subscription_period})\n\n"
        "<b>Цена:</b>\n"
        "— {subscription_price} рублей"
    )
