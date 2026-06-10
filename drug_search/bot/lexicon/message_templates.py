from drug_search.core.lexicon import QUESTION_COST, NEW_DRUG_COST, TOKENS_LIMIT


class MessageTemplates:
    """Шаблоны сообщений с форматированием"""
    # [ SECTIONS ]
    DRUG_INFO_BRIEFLY: str = (
        "<b>{drug_name_ru} ({drug_name}, {latin_name})</b>\n\n"
        "<i>({classification})</i>\n\n"
        "{description}\n\n"
        "<b>Клинические эффекты:</b>\n{clinical_effects}\n\n"
        "{fun_fact}\n\n"
        "{disclaimer}"
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
        "{disclaimer}"
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
        "<b>{profile_icon} {profile_name}</b>\n"
        "<i>{subscription_end_at}</i>"
        "<b>Токены:</b> {allowed_tokens}  {refresh_section}\n"
        "<i>{additional_tokens_text}</i>"
        "{additional_tokens_quote}"
        "{gamification_section}"
        "{simple_mode_text}"
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
        "<b>Зачем нужны токены:</b>\n"
        "— Токены нужны, чтобы делать запросы в бота.\n\n"
        "<b>Как тратятся токены:</b>\n"
        f"На каждый вопрос тратится: {QUESTION_COST} токен\n"
        f"На запись препарата в базу: {NEW_DRUG_COST} токена\n\n"
        "<b>Выбери пак:</b>"
    )

    SUBSCRIPTION_BUY_CHOOSE_TYPE = (
        "💳 <b>Покупка подписки</b>\n\n"
        "<b>Что дают подписки?</b>\n\n"
        "<b>🧢 Лайт:</b>\n"
        f"— каждую неделю ты получаешь {TOKENS_LIMIT.LITE_TOKENS_LIMIT.value} токенов\n"
        "— доступен раздел «Механизм действия»\n"
        "— уменьшено ограничение на запросы\n\n"
        "<b>💎 Премиум:</b>\n"
        f"— <b>каждый день</b> ты получаешь {TOKENS_LIMIT.PREMIUM_TOKENS_LIMIT.value} токенов\n"
        "— разблокирована возможность изучать запретные препараты\n"
        "— бесплатное обновление базы\n"
        "— убраны все ограничения\n\n"
        "<b>Выбери тип подписки:</b>"
    )

    SUBSCRIPTION_BUY_CHOOSE_DURATION = (
        "💳 <b>Покупка подписки {subscription_type}</b>\n\n"
        "<b>Выбери длительность подписки:</b>"
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
        "— {package_name} ({package_price} рублей)"
    )

    SUBSCRIPTION_BUY_CONFIRMATION = (
        "💳 <b>Покупка подписки</b>\n\n"
        "<b>Выбранная подписка:</b>\n"
        "— <u>{subscription_name}</u> ({subscription_period} дней)\n"
        "<i>(будет действовать до: {subscription_end})</i>\n\n"
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

    DRUG_PACKS_BUY = (
        "📦 <b>Паки препаратов</b>\n\n"
        "Разблокируют все препараты выбранной категории в базе бота.\n\n"
        "<b>Доступные паки:</b>"
    )

    DRUG_PACK_CONFIRMATION = (
        "📦 <b>Покупка пака</b>\n\n"
        "<b>{pack_name}</b>\n"
        "<i>{pack_description}</i>\n\n"
        "Цена: {pack_price} рублей"
    )

    QUIZ_INTRO = (
        "🧠 <b>Режим «Получение знаний»</b>\n\n"
        "Тебе показывают характеристику препарата — угадай вещество из 4 вариантов.\n"
        "Собери серию правильных ответов и хвастайся в Stories 🔥\n\n"
        f"Стоимость вопроса: {QUESTION_COST} токен."
    )

    QUIZ_MILESTONE = (
        "\n\n🎉 <b>Milestone x{streak}!</b> Ты на уровне {level_badge}"
    )

    QUIZ_CORRECT = "✅ Верно! Отличная работа."
    QUIZ_WRONG = "❌ Неверно.\n\n{explanation}"

    QUIZ_STREAK_BONUS = (
        "\n\n🔥 Серия: <b>{streak}</b> · Рекорд: <b>{best_streak}</b>\n"
        "{level_badge}"
    )

    GAMIFICATION_PROFILE = (
        "<blockquote>"
        "🧠 <b>Pharma IQ:</b> {level_badge}\n"
        "Серия викторины: {streak} · Рекорд: {best_streak}"
        "</blockquote>\n\n"
    )

    PDF_READY = (
        "📄 <b>Pharma Card готова!</b>\n\n"
        "Бело-синяя карточка с полным разбором «{drug_name}».\n"
        "Отправь другу — пусть тоже прокачает Pharma IQ 💉"
    )
    PDF_GENERATION_ERROR = "Не удалось создать PDF. Попробуйте позже."

    WEEKLY_DRUG_POST = (
        "💊 <b>Препарат недели: {drug_name}</b>\n\n"
        "<i>{classification}</i>\n\n"
        "{description}\n"
        "{footer}"
    )

    HELLO_WOW = (
        "💉 <b>DrugSearch</b> — твоя pharma-лаборатория в Telegram\n\n"
        "<blockquote>"
        "🔍 <b>Мгновенный разбор</b> любого препарата\n"
        "🧠 <b>Викторина</b> — угадай вещество по описанию\n"
        "📄 <b>Pharma Card PDF</b> — красивая карточка для шеринга\n"
        "🤖 <b>AI-ассистент</b> — ответит на любой pharma-вопрос"
        "</blockquote>\n\n"
        "Напиши название препарата или нажми кнопку ниже 👇"
    )

    # [ REFERRALS ]
    REFERRALS_MENU = (
        "🧚‍♀️ <b>Реферальная система</b>\n\n"
        "<blockquote>"
        "Твоя ссылка:\n"
        "— {url}"
        "</blockquote>\n\n"
        "До получения {ref_tokens_next_level_text} осталось пригласить {referrals_count_next_text}."
    )
