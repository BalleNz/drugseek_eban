SYMBOLS = ["▤", "▥", "▨", "▧", "▦", "▩"] * 2


def make_google_sources(sources: list[str]) -> list[dict]:
    """Возвращает ссылки на поиск гугл различных источников,
    например, Articles, DrugbankID..
    """
    return [
        {
            "source_name": source,
            "google_url": f'https://www.google.com/search?q={source}'
        }
        for source in sources
    ]


class MessageTemplates:
    HELLO = "💊 Привет! Напиши любой препарат, а я тебе пришлю его характеристику."

    DRUG_INFO_BRIEFLY = (
        "<b>{drug_name_ru}, {drug_name}, {latin_name}.</b>\n\n"
        "<b>Классификация:</b> {classification}\n\n"
        "<b>Описание:</b>\n{description}\n\n"
        "<b>Основное действие:</b>\n{primary_action}\n\n"
        "{secondary_actions_section}"
        "<b>Клинические эффекты:</b>\n{clinical_effects}\n\n"
    )

    DRUG_INFO_PATHWAYS = (
        "<b>{drug_name_ru} пути активации. {sources_section}</b>\n"
        "{pathways_list}\n"
    )

    DRUG_INFO_COMBINATIONS = (
        "<b>{drug_name_ru} комбинации.</b>\n\n"
        "<b>Полезные комбинации:</b>\n{good_combinations}\n"
        "<b>Опасные комбинации:</b>\n{bad_combinations}"
    )

    DRUG_INFO_DOSAGES = (
        "<b>{drug_name_ru} дозировки.</b> {sources_section}\n\n"
        "{dosages_list}"
        "{dosage_fun_fact_section}"
    )

    DRUG_INFO_METABOLISM = (
        "<b>{drug_name_ru} метаболизм.</b>\n\n"
        "{metabolism_description}\n\n"
        "{pharmacokinetics}"
    )

    DRUG_INFO_RESEARCHES = (
        "<b>{drug_name_ru} исследования.</b>\n\n"
        "{researches_list}"
    )

    DRUGS_ANALOGS: str = (
        "<b>{drug_name_ru} аналоги.</b>\n\n"
        "{analogs_section}"
        "{analogs_description}\n\n"
    )

    USER_PROFILE = (
        "<b>Профиль пользователя</b>\n"
        "@{username}\n\n"
        "<b>Статистика запросов:</b>\n"
        "• Использовано: {used_requests}\n"
        "• Доступно: {allowed_requests}\n\n"
        "{description_section}"
        "{subscription_section}"
    )

    DRUGS_INFO = (
        "<b>Все ваши купленные препараты расположены на этой странице!</b>\n\n"
        "Всего купленных препаратов: <b>{len_allowed_drugs}</b>\n"
        "Всего препаратов в БАЗЕ: <b>{len_drugs}</b>"
    )
