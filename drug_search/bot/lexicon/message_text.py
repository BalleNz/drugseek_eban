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
        "<b>{drug_name_ru} ({drug_name}, {latin_name})</b>\n\n"
        "<i>({classification})</i>\n\n"
        "{description}\n\n"
        "<b>Клинические эффекты:</b>\n{clinical_effects}\n\n"
        "{fun_fact}"
    )

    DRUG_INFO_PATHWAYS = (
        "<b>{drug_name_ru} механизм действия {sources_section}</b>\n\n"
        "<b>Основное действие: </b>\n{primary_action}\n\n"
        "{secondary_actions_section}"
        "<b>┫Пути активации:</b>"
        "{pathways_list}\n"
    )

    DRUG_INFO_COMBINATIONS = (
        "<b>{drug_name_ru} комбинации.</b>\n\n"
        "<b>Полезные комбинации:</b>\n{good_combinations}\n"
        "<b>Опасные комбинации:</b>\n{bad_combinations}"
    )

    DRUG_INFO_DOSAGES = (
        "<b>{drug_name_ru} дозировки {sources_section}</b>\n\n"
        "{dosages_list}"
        "{dosage_fun_fact_section}"
    )

    DRUG_INFO_METABOLISM = (
        "<b>{drug_name_ru} метаболизм.</b>\n\n"
        "{metabolism_description}"
        "{pharmacokinetics}"
    )

    DRUG_INFO_RESEARCHES = (
        "<b>{drug_name_ru} исследования.</b>\n\n"
        "{researches_list}"
    )

    DRUGS_ANALOGS: str = (
        "<b>{drug_name_ru} аналоги.</b>\n\n"
        "{analogs_description}"
        "{analogs_section}"
    )

    USER_PROFILE = (
        "<b>{profile_icon} Твой профиль</b>\n\n"
        "Использовано запросов за сегодня: {used_requests}\n"
        "Осталось запросов сегодня: {allowed_requests}\n\n"
        "{subscription_section}"
        "{description_section}"
    )  # TODO логику поменять. *Использовано за сегодня.

    DRUG_UPDATE_INFO = (
        "{drug_name}\n\n"
        "Последнее обновление препарата: {drug_last_update}\n"
    )

    DRUGS_INFO = (
        "<b>Все ваши препараты расположены на этой странице!</b>\n\n"
        "Всего препаратов в <b>Базе:</b> {len_allowed_drugs}"
    )

    # ASSISTANT
    ASSISTANT_ANSWER_DRUGS = (
        "{answer}\n\n"
        "<b>Список препаратов, которые вам помогут:</b>"
        "{drugs_section}"
    )

    # ARQ
    DRUG_CREATED_JOB_FINISHED = (
        "<b>Препарат {name_ru} теперь доступен в вашей Базе!</b>"
    )

