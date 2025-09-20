from pydantic import BaseModel

from drug_search.bot.keyboards import DescribeTypes
from drug_search.core.schemas import AllowedDrugsSchema, UserSchema
from schemas import DrugSchema


class MessageText:
    HELLO = "💊 Привет! Напиши любой препарат, а я тебе пришлю его характеристику."

    DRUG_INFO_BRIEFLY = (
        "<b>💊 {drug_name_ru} ({latin_name})</b>\n\n"
        "<b>Классификация:</b> {classification}\n\n"
        "<b>Клинические эффекты:</b>\n{clinical_effects}\n\n"
        "<b>Описание:</b>\n{description}\n\n"
        "{fun_fact_section}"
    )

    DRUG_INFO_PATHWAYS = (
        "<b>🔬 Механизм действия {drug_name_ru}</b>\n\n"
        "<b>Основное действие:</b>\n{primary_action}\n\n"
        "{secondary_actions_section}"
        "<b>Клинические эффекты:</b>\n{clinical_effects}\n\n"
        "<b>Пути активации:</b>\n{pathways_list}\n\n"
    )

    DRUG_INFO_COMBINATIONS = (
        "<b>⚗️ Взаимодействия {drug_name_ru}</b>\n\n"
        "<b>Полезные комбинации:</b>\n{good_combinations}\n\n"
        "<b>Опасные комбинации:</b>\n{bad_combinations}"
    )

    DRUG_INFO_DOSAGES = (
        "<b>💉 Дозировки {drug_name_ru}</b>\n\n"
        "{dosages_list}\n\n"
        "<b>Фармакокинетика:</b>\n{pharmacokinetics}\n\n"
        "<b>Источники:</b> {sources}"
    )

    DRUG_INFO_RESEARCHES = (
        "<b>📊 Исследования {drug_name_ru}</b>\n\n"
        "{researches_list}"
    )

    USER_PROFILE = (
        "<b>👤 Профиль пользователя</b>\n"
        "@{username}\n\n"
        "<b>Статистика запросов:</b>\n"
        "• Использовано: {used_requests}\n"
        "• Доступно: {allowed_requests}\n\n"
        "{description_section}"
        "{subscription_section}"
    )

    DRUGS_INFO = (
        "<b>Все ваши купленные препараты расположенны на этой странице!</b>\n\n"
        "Всего купленных препаратов: <b>{len_allowed_drugs}</b>\n"
        "Всего препаратов в БАЗЕ: <b>{len_drugs}</b>"
    )

    @staticmethod
    def format_drug_briefly(drug_data: DrugSchema) -> str:
        """Форматирование краткой информации о препарате"""
        # TODO

        fun_fact_section = f"<b>Интересный факт:</b>\n{drug_data.dosages_fun_fact}\n\n" if drug_data.dosages_fun_fact else ""

        return MessageText.DRUG_INFO_BRIEFLY.format(
            drug_name_ru=drug_data.name_ru,
            latin_name=drug_data.latin_name,
            classification=drug_data.classification,
            description=drug_data.description,
            fun_fact_section=fun_fact_section,
            clinical_effects=drug_data.clinical_effects,
        )

    @staticmethod
    def format_pathways(drug: DrugSchema) -> str:
        """Форматирование информации о путях воздействия"""
        pathways_list = ""
        for i, pathway in enumerate(drug.pathways, start=1):
            pathway_info: str = ""
            pathway_info += f"  <b>{i}) <u>{pathway.receptor}</u></b>\n"
            pathway_info += f"      <b>Эффект:</b> {pathway.effect}\n"
            pathway_info += f"      <b>Сила связывания:</b> {pathway.affinity_description} ({pathway.binding_affinity})\n"
            pathway_info += f"      <b>Тип активации:</b> {pathway.activation_type}\n"
            pathway_info += f"      <b>Полный путь активации:</b> {pathway.pathway}\n"
            pathway_info += f"      <b>Что делает:</b> {pathway.note}\n\n"

            pathways_list += pathway_info

        secondary_actions_section = f"<b>Вторичные действия:</b>\n{drug.secondary_actions}\n\n" if drug.secondary_actions else ""

        return MessageText.DRUG_INFO_PATHWAYS.format(
            drug_name_ru=drug.name_ru,
            primary_action=drug.primary_action,
            clinical_effects=drug.clinical_effects,
            secondary_actions_section=secondary_actions_section,
            pathways_list=pathways_list
        )

    @staticmethod
    def format_combinations(combinations_data: dict) -> str:
        """Форматирование информации о взаимодействиях"""
        good_combinations = ""
        bad_combinations = ""

        for combo in combinations_data.get('combinations', []):
            if combo.get('combination_type') == 'good':
                products = ", ".join(combo.get('products', [])) if combo.get('products') else "Нет примеров"
                good_combinations += f"• <b>{combo.get('substance', 'Нет данных')}</b>: {combo.get('effect', 'Нет данных')} ({products})\n"
            else:
                bad_combinations += f"• <b>{combo.get('substance', 'Нет данных')}</b>: {combo.get('effect', 'Нет данных')} ({combo.get('risks', 'Нет данных')})\n"

        return MessageText.DRUG_INFO_COMBINATIONS.format(
            drug_name_ru=combinations_data.get('drug_name_ru', 'Нет названия'),
            good_combinations=good_combinations or "Нет данных",
            bad_combinations=bad_combinations or "Нет данных"
        )

    @staticmethod
    def format_dosages(drug: DrugSchema) -> str:
        """Форматирование информации о дозировках"""
        dosages_list = ""
        for dosage in drug.dosages:
            route_method = f"{dosage.route} {dosage.method}".strip()
            per_time = dosage.per_time
            max_day = dosage.max_day
            notes = dosage.notes

            dosages_list += f"• <b>{route_method}</b>: {per_time} (макс. в сутки: {max_day})"
            if notes:
                dosages_list += f" | <i>Примечание: {notes}</i>"
            dosages_list += "\n"

        pharmacokinetics = f"Биодоступность: {drug.pharmacokinetics.absorption}\n"
        pharmacokinetics += f"Метаболизм: {drug.pharmacokinetics.metabolism}\n"
        pharmacokinetics += f"Выведение: {drug.pharmacokinetics.elimination}\n"
        pharmacokinetics += f"Tmax: {drug.pharmacokinetics.time_to_peak}"

        return MessageText.DRUG_INFO_DOSAGES.format(
            drug_name_ru=dosages_data.get('drug_name_ru', 'Нет названия'),
            dosages_list=dosages_list or "Нет данных",
            pharmacokinetics=pharmacokinetics,
            sources=", ".join(dosages_data.get('sources', [])) or "Нет данных"
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
    def format_by_type(describe_type: DescribeTypes, drug_data: BaseModel) -> str:
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
            return method(drug_data)
        else:
            return "Неизвестный тип описания"

    # TODO: заменить в теле функции на схему (щас словарь)