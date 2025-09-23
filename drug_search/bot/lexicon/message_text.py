from drug_search.bot.keyboards import DescribeTypes
from drug_search.core.schemas import AllowedDrugsSchema, UserSchema, DrugSchema, CombinationType

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


class MessageText:
    HELLO = "💊 Привет! Напиши любой препарат, а я тебе пришлю его характеристику."

    DRUG_INFO_BRIEFLY = (
        "<b>{drug_name_ru} ({drug_name}, {latin_name})</b>\n\n"
        "<b>Классификация:</b> {classification}\n\n"
        "<b>Описание:</b>\n{description}\n\n"
        "<b>Основное действие:</b>\n{primary_action}\n\n"
        "{secondary_actions_section}\n\n"
        "<b>Клинические эффекты:</b>\n{clinical_effects}\n\n"
    )

    DRUG_INFO_PATHWAYS = (
        "<b>Пути активации {name} {sources_section}</b>\n"
        "{pathways_list}\n"
    )

    DRUG_INFO_COMBINATIONS = (
        "<b>Взаимодействия {drug_name_ru}</b>\n\n"
        "<b>Полезные комбинации:</b>\n{good_combinations}\n"
        "<b>Опасные комбинации:</b>\n{bad_combinations}"
    )

    DRUG_INFO_DOSAGES = (
        "<b>Дозировки {drug_name_ru}</b> {sources_section}\n\n"
        "{dosages_list}"
        "{pharmacokinetics}\n\n"
        "{dosage_fun_fact_section}"
    )

    DRUG_INFO_RESEARCHES = (
        "<b>Исследования {drug_name_ru}</b>\n\n"
        "{researches_list}"
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

    @staticmethod
    def format_drug_briefly(drug: DrugSchema) -> str:
        """Форматирование краткой информации о препарате"""
        secondary_actions_section = f"<b>Вторичные действия:\n</b>{drug.secondary_actions}" if drug.secondary_actions else ""

        return MessageText.DRUG_INFO_BRIEFLY.format(
            drug_name_ru=drug.name_ru,
            drug_name=drug.name,
            latin_name=drug.latin_name,
            classification=drug.classification,
            description=drug.description,
            clinical_effects=drug.clinical_effects,
            primary_action=drug.primary_action,
            secondary_actions_section=secondary_actions_section,

        )

    @staticmethod
    def format_pathways(drug: DrugSchema) -> str:
        """Форматирование информации о путях воздействия"""
        pathways_list: str = ""

        pathways: set = {pathway.pathway for pathway in
                         drug.pathways}  # все пути (например, Androgen receptor signaling pathway)

        google_sources: list[dict] = make_google_sources(drug.pathways_sources)
        num_symbols = "¹²³⁴⁵⁶⁷⁸⁹"
        sources_num: list = [f"<a href='{source["google_url"]}'><b>{num_symbols[i]}</b></a>" for i, source in enumerate(google_sources)]
        sources_section: str = ' '.join(sources_num)

        for i, drug_pathway in enumerate(drug.pathways):
            pathway_info: str = ""
            if (signaling_pathway := drug_pathway.pathway) in pathways:
                pathway_info += f"\n<b>{SYMBOLS[i]} {signaling_pathway}</b>\n"
                pathways.remove(signaling_pathway)

            pathway_info += f"<b>     ▻ <u>{drug_pathway.receptor}</u></b>\n"
            pathway_info += f"        <b>Тип:</b> {drug_pathway.activation_type}\n"
            pathway_info += f"        <b>Эффект:</b> {drug_pathway.effect}\n"
            pathway_info += f"        <b>Сила связи:</b> {drug_pathway.affinity_description} | {drug_pathway.binding_affinity}\n"
            pathway_info += f"        <b>Что делает:</b> {drug_pathway.note}\n"

            pathways_list += pathway_info

        return MessageText.DRUG_INFO_PATHWAYS.format(
            sources_section=sources_section,
            name=drug.name,
            pathways_list=pathways_list,
        )

    @staticmethod
    def format_combinations(drug: DrugSchema) -> str:
        """Форматирование информации о взаимодействиях"""
        good_combinations = ""
        bad_combinations = ""

        for i, combination in enumerate(drug.combinations):
            combination_text: str = ""
            combination_text += f"<b>{i}) {combination.substance}</b>\n"
            combination_text += f"Эффект: {combination.effect}\n"

            if combination.combination_type == CombinationType.GOOD:
                combination_text += (
                    f"Препараты:\n"
                )
                for product in combination.products:
                    combination_text += f"      •{product}\n"

                good_combinations += combination_text + "\n"

            if combination.combination_type == CombinationType.BAD:
                combination_text += f"{combination.risks}\n"

                bad_combinations += combination_text

        return MessageText.DRUG_INFO_COMBINATIONS.format(
            drug_name_ru=drug.name_ru,
            good_combinations=good_combinations or "Нет данных",
            bad_combinations=bad_combinations or "Нет данных"
        )

    @staticmethod
    def format_dosages(drug: DrugSchema) -> str:
        """Форматирование информации о дозировках"""
        dosages_list = ""

        google_sources: list[dict] = make_google_sources(drug.pathways_sources)
        num_symbols = "¹²³⁴⁵⁶⁷⁸⁹"
        sources_num: list = [f"<a href='{source["google_url"]}'><b>{num_symbols[i]}</b></a>" for i, source in enumerate(google_sources)]
        sources_section: str = ' '.join(sources_num)

        for i, dosage in enumerate(drug.dosages):
            # проходит по списку дозировок и делает красивую строку
            dosage_info: str = ""
            dosage_info += f"<b> {SYMBOLS[i]} <u>{dosage.method.capitalize()}</u></b>\n"

            per_time_weight: str = f"({dosage.per_time_weight_based})" if dosage.per_time_weight_based else ""
            max_day_weight: str = f"({dosage.max_day_weight_based})" if dosage.max_day_weight_based else ""
            dosage_info += f"      <b>Разовая дозировка:</b> {dosage.per_time} <i>  {per_time_weight}</i>\n" if dosage.per_time else ""
            dosage_info += f"      <b>Макс. в сутки:</b> {dosage.max_day} <i>  {max_day_weight}</i>\n" if dosage.max_day else ""
            dosage_info += f"      <b>Время начала действия:</b> {dosage.onset}\n" if dosage.onset else ""
            dosage_info += f"      <b>Период полувыведения:</b> {dosage.half_life}\n" if dosage.half_life else ""
            dosage_info += f"      <b>Продолжительность действия:</b> {dosage.duration}\n" if dosage.duration else ""
            dosage_info += f"      <b>Примечания:</b> {dosage.notes}\n" if dosage.notes else "\n"

            dosages_list += dosage_info + "\n"

        pharmacokinetics = f"<b>Биодоступность:</b> \n{drug.absorption}\n\n" if drug.absorption else ""
        pharmacokinetics += f"<b>Метаболизм:</b> \n{drug.metabolism}\n\n" if drug.metabolism else ""
        pharmacokinetics += f"<b>Выведение:</b> \n{drug.elimination}\n\n" if drug.elimination else ""
        pharmacokinetics += f"<b>Максимальная концентрация в крови через:</b> <u>{drug.time_to_peak}</u>" if drug.time_to_peak else ""

        dosage_fun_fact_section = f"{drug.dosages_fun_fact}\n\n" if drug.dosages_fun_fact else ""

        return MessageText.DRUG_INFO_DOSAGES.format(
            drug_name_ru=drug.name_ru,
            dosages_list=dosages_list,
            sources_section=sources_section,
            pharmacokinetics=pharmacokinetics,
            dosage_fun_fact_section=dosage_fun_fact_section
        )

    @staticmethod
    def format_researches(drug: DrugSchema) -> str:
        """Форматирование информации об исследованиях"""
        researches_list = ""
        for research in drug.researches:
            authors = f" | Авторы: {research.authors}" if research.authors else ""
            study_type = f" | Тип: {research.study_type}" if research.study_type else ""
            interest = f" | Интерес: {research.interest}%" if research.interest else ""

            researches_list += f"• <b>{research.name}</b>\n"
            researches_list += f"<i>Дата: {research.publication_date}{authors}{study_type}{interest}</i>\n"
            researches_list += f"{research.description}\n"

            if research.summary:
                researches_list += f"<b>Вывод:</b> {research.summary}\n"

            researches_list += f"<a href='{research.url}'>Ссылка на исследование</a>\n\n"

        return MessageText.DRUG_INFO_RESEARCHES.format(
            drug_name_ru=drug.name_ru,
            researches_list=researches_list or "Нет данных об исследованиях"
        )

    @staticmethod
    def format_user_profile(user_data: UserSchema) -> str:
        """Форматирование профиля пользователя"""
        description = user_data.description
        description_section = f"<b>Описание:</b>\n{description}\n" if description else ""

        subscription: str = f"<b>Подписка на запрещенку</b>: <b>Активна</b>\n" if user_data.drug_subscription else "Подписка отсутствует :(\n"
        subscription_end: str = f"Окончание подписки: {user_data.drug_subscription_end}\n" if user_data.drug_subscription else ""
        subscription_section = subscription + subscription_end

        return MessageText.USER_PROFILE.format(
            username=user_data.username,
            used_requests=user_data.used_requests,
            allowed_requests=user_data.allowed_requests,
            description_section=description_section,
            subscription_section=subscription_section
        )

    @staticmethod
    def format_drugs_info(allowed_drugs_info: AllowedDrugsSchema) -> str:
        return MessageText.DRUGS_INFO.format(
            len_allowed_drugs=allowed_drugs_info.allowed_drugs_count,
            len_drugs=allowed_drugs_info.drugs_count
        )

    @staticmethod
    def format_by_type(describe_type: DescribeTypes, drug: DrugSchema) -> str:
        """Форматирование информации в зависимости от типа описания"""
        format_methods = {
            DescribeTypes.BRIEFLY: MessageText.format_drug_briefly,
            DescribeTypes.DOSAGES: MessageText.format_dosages,
            DescribeTypes.PATHWAYS: MessageText.format_pathways,
            DescribeTypes.COMBINATIONS: MessageText.format_combinations,
            DescribeTypes.RESEARCHES: MessageText.format_researches,
        }

        method = format_methods.get(describe_type)
        if method:
            return method(drug)
        else:
            raise "Неизвестный тип описания"
