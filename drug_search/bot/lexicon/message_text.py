from drug_search.bot.lexicon import MessageTemplates
from drug_search.bot.lexicon.enums import HelpSectionMode
from drug_search.bot.lexicon.keyboard_words import ButtonText
from drug_search.bot.utils.format_message_text import DrugMessageFormatter, UserProfileMessageFormatter
from drug_search.bot.utils.funcs import format_time
from drug_search.core.lexicon import ANTISPAM_DEFAULT, TOKENS_LIMIT, QUESTION_COST, NEW_DRUG_COST


class MessageText:
    """Шаблоны сообщений"""

    class formatters:
        """Шаблоны с форматированием"""
        # [ drugs section ]
        DRUG_BRIEFLY: str = DrugMessageFormatter.format_drug_briefly
        DRUG_BY_TYPE: str = DrugMessageFormatter.format_by_type
        DRUGS_INFO: str = DrugMessageFormatter.format_drugs_info

        # [ user profile ]
        USER_PROFILE: str = UserProfileMessageFormatter.format_user_profile
        USER_PROFILE_DESCRIPTION: str = UserProfileMessageFormatter.format_user_description_profile

    class help:
        """Секция с помощью юзеру"""
        MAIN = (
            "🔎 <b>Что умеет бот?</b>\n\n"
            "Здесь ты найдешь полную инструкцию к боту\n\n"
            "Если остались вопросы, <a href='https://t.me/uaquoa'><b>напиши мне.</b></a>\n"
        )
        QUERIES = (
            f"🔎 <b>{ButtonText.HELP_QUERIES}</b>\n\n"
            "В боте есть <b>3 режима</b> запросов (выбираются автоматически):\n\n"
            "<blockquote>"
            "— База препаратов: поиск препарата по названию со всеми разделами\n\n"
            "— Эффективные препараты: рекомендации препаратов по симптомам или желаниям\n\n"
            "— Вопросы по фарме: ответы на любые вопросы фармакологического ассистента\n\n"
            "</blockquote>"
        )
        TOKENS = (
            f"🔎 <b>{ButtonText.HELP_TOKENS}</b>\n\n"
            "<b>Как расходуются токены?</b>\n"
            "<blockquote>"
            f"На каждый вопрос / список препаратов тратится: {QUESTION_COST} токен\n"
            f"Для записи препарата в базу тратится: {NEW_DRUG_COST} токена"
            "</blockquote>\n\n"
            "<b>Вам даются токены в зависимости от вашей подписки:</b>\n"
            "<blockquote>"
            f"<b>💎️ Премиум:</b>\n"
            f"       — {TOKENS_LIMIT.PREMIUM_TOKENS_LIMIT.value} токенов в день\n"
            f"<b>⚡ Лайт:</b>\n"
            f"       — {TOKENS_LIMIT.LITE_TOKENS_LIMIT.value} токенов в неделю\n"
            f"<b>❌ Без подписки:</b>\n"
            f"       — {TOKENS_LIMIT.DEFAULT_TOKENS_LIMIT.value} токенов в неделю"
            "</blockquote>\n\n"
        )
        SUBSCRIPTION = (
            f"🔎 <b>{ButtonText.HELP_SUBSCRIPTION}</b>\n\n"
            f"Для повседневного использования бота необходимы подписки.\n\n"
            f"<u>Без подписки</u> в боте действуют ограничения:\n"
            f"       ❌ нельзя просматривать разделы «Исследования» и «Механизм действия»\n"
            f"       ❌ 5 токенов при регистрации и больше токены не начисляются\n"
            f"       ❌ ограничение на частоту запросов: {ANTISPAM_DEFAULT["max_requests"]} сообщения раз в {format_time(ANTISPAM_DEFAULT["time_limit"])}"
            f"\n\n"
            f"<blockquote>"
            f"<b>🧢 <u>Лайт:</u></b>\n"
            f"      ✅ каждую неделю вы получаете {TOKENS_LIMIT.LITE_TOKENS_LIMIT.value} токенов\n"
            f"      ✅ можно просматривать раздел «🎯 Механизм действия»\n"
            f"      ✅ уменьшено ограничение на частоту запросов\n"
            f"      ❌️ нет доступа к изучению запретных препаратов\n"
            f"      ❌️ нет доступа к исследованиям\n\n"
            f"<b>💎 <u>Премиум:</u></b>\n"
            f"      ✅ вы получаете 100 токенов каждый день\n"
            f"      ✅ разблокирована возможность изучать запретные препараты\n"
            f"      ✅ убраны ограничения сообщений\n"
            f"      ✅ полный доступ ко всему функционалу\n"
            f"      ✅ бесплатное обновление препаратов\n"
            f"</blockquote>\n\n"
        )

        QUERIES_QUESTIONS = (
            f"🔎 <b>{ButtonText.HELP_QUERIES} — {ButtonText.HELP_QUERIES_QUESTIONS}</b>\n\n"
            "Задайте любой вопрос боту, он ответит на него детализировано и развернуто.\n\n"
            "<b>Примеры запросов:</b>\n"
            "<blockquote>"
            "— «Как работает запоминание информации в мозге?»\n"
            "— «Объясни принцип дефолт системы мозга на языке нейробиологии»\n"
            "— «Как происходит гипертрофия мышц?»\n"
            "</blockquote>"
        )
        QUERIES_PHARMA = (
            f"🔎 <b>{ButtonText.HELP_QUERIES} — {ButtonText.HELP_QUERIES_PHARMA}</b>\n\n"
            "Задайте любой вопрос боту, подразумевающий список препаратов.\n\n"
            "<b>Примеры запросов:</b>\n"
            "<blockquote>"
            "— «Дай список препаратов для улучшения секса»\n"
            "— «Какие самые лучшие препараты для ...?»\n"
            "— «Чем заменить препарат ...?»\n"
            "— «Хочу стать умнее какие препараты помогут?»\n"
            "</blockquote>"
        )
        QUERIES_DRUG_SEARCH = (
            f"🔎 <b>{ButtonText.HELP_QUERIES} — {ButtonText.HELP_QUERIES_DRUG_SEARCH}</b>\n\n"
            "Введите название препарата на русском или английском, включая сленговые названия.\n\n"
            "<b>Примеры запросов:</b>\n"
            "— «Аспирин» или «Aspirin»\n"
            "— «Метформин 500»\n"
            "— «Витамин D3»\n"
            "— «Ноопепт» или «Фенибут»\n\n"
            "<i>Бот покажет полную информацию о препарате: дозировки, механизм действия, аналоги, исследования и т.д.</i>"
        )

        TOKENS_FREE = (
            "🔎 <b>Как получать токены?</b>\n\n"
            "<blockquote>"
            f"<b>Реферальная система</b> /referrals\n\n"
            f"<b>Токены за подписку на каналы</b> /free_tokens\n\n"
            f"<b>Купить подписку</b> /subscription"
            f"</blockquote>"
        )

        help_format_by_mode = {
            HelpSectionMode.MAIN: MAIN,
            HelpSectionMode.QUERIES: QUERIES,
            HelpSectionMode.TOKENS: TOKENS,
            HelpSectionMode.SUBSCRIPTION: SUBSCRIPTION,
            HelpSectionMode.QUERIES_QUESTIONS: QUERIES_QUESTIONS,
            HelpSectionMode.QUERIES_PHARMA_QUESTIONS: QUERIES_PHARMA,
            HelpSectionMode.QUERIES_DRUG_SEARCH: QUERIES_DRUG_SEARCH,
            HelpSectionMode.TOKENS_FREE: TOKENS_FREE,
        }

    # [ DRUGS ]
    DRUG_UPDATE_INFO: str = MessageTemplates.DRUG_UPDATE_INFO
    DRUG_BUY_REQUEST: str = MessageTemplates.DRUG_BUY_REQUEST
    DRUG_BUY_ALLOWED: str = MessageTemplates.DRUG_BUY_ALLOWED

    # [ positive / neutral ]
    DRUG_MANUAL_SEARCHING: str = "Поиск препарата.."

    DRUG_BUY_CREATED: str = "⏳ <i>Препарат создаётся...</i>"

    DRUG_UPDATING: str = "Препарат поставлен в очередь на обновление. Вы получите уведомление о завершении!"

    DRUG_BUY_QUEUED: str = "Данный препарат уже создаётся, попробуйте запрос через минуту."

    # [ negative ]
    DRUG_IS_BANNED: str = (
        "К сожалению, распространять информацию про нелегальные препараты запрещено законами РФ. "
        "Запрос отклонён."
    )

    DRUG_IS_NOT_EXIST: str = ("Такой препарат не существует. "
                              "Возможно, вы ошиблись в написании названия. "
                              "Попробуйте написать действующее вещество.")

    ERROR_DRUG: str = "Произошла ошибка, такой препарат не существует.."

    NOT_EXIST_DRUG: str = "Такого препарата не существует."

    # [ TOKENS ]
    NO_TOKENS: str = "🚫 У вас не осталось токенов для запросов.\n\n/tokens"

    NOT_ENOUGH_UPDATE_TOKENS: str = "⚠️ Недостаточно токенов для обновления препарата!"

    NOT_ENOUGH_CREATE_TOKENS: str = (
        "⚠️ У вас недостаточно токенов!"
    )

    NEED_SUBSCRIPTION: str = (
        "Для просмотра сомнительных препаратов необходима премиум подписка."
    )

    # [ PAYMENT ]
    TOKENS_BUY = MessageTemplates.TOKENS_BUY
    TOKENS_CONFIRMATION = MessageTemplates.TOKENS_BUY_CONFIRMATION

    SUBSCRIPTION_BUY_CHOOSE_TYPE = MessageTemplates.SUBSCRIPTION_BUY_CHOOSE_TYPE
    SUBSCRIPTION_BUY_CHOOSE_DURATION = MessageTemplates.SUBSCRIPTION_BUY_CHOOSE_DURATION
    SUBSCRIPTION_BUY_CONFIRMATION = MessageTemplates.SUBSCRIPTION_BUY_CONFIRMATION

    SUBSCRIPTION_UPGRADE = MessageTemplates.SUBSCRIPTION_UPGRADE
    SUBSCRIPTION_UPGRADE_CONFIRMATION = MessageTemplates.SUBSCRIPTION_UPGRADE_CONFIRMATION

    FINISH_PAYMENT = "Ожидание оплаты..."

    # [ STATIC ]
    HELLO: str = ("<b>💊 Привет!</b>\n\n"
                  "Я — Твой карманный специалист по фармакологии и медицине.\n\n"
                  "О каком препарате хочешь узнать?\n"
                  "Или у тебя есть какой-нибудь вопрос?")

    # [ Mailing ]
    ONLY_FOR_ADMINS = "Эта команда доступна только для администрации."
    SUCCESS_MAILING = "Рассылка передана брокеру задач.."

    # [ QUERY ]
    QUERY_IN_PROCESS: str = "Обработка запроса..."
    ASSISTANT_WAITING: str = "Ожидание ответа на вопрос у ассистента..."

    ANTISPAM_MESSAGE = MessageTemplates.ANTISPAM_MESSAGE

    MESSAGE_LENGTH_EXCEED = MessageTemplates.MESSAGE_LENGTH_EXCEED
    MESSAGE_LENGTH_EXCEED_PREMIUM = "⚠️ Вы превысили количество символов в сообщении!"

    # [ REFERRALS ]
    GET_FREE_TOKENS_MENU = (
        "🧚‍♀️ Здесь ты можешь получить токены бесплатно!"
    )

    REFERRALS_MENU = MessageTemplates.REFERRALS_MENU
