from drug_search.bot.keyboards import DescribeTypes
from drug_search.bot.lexicon.consts import SYMBOLS
from drug_search.bot.lexicon.message_templates import MessageTemplates
from drug_search.bot.utils.funcs import make_google_sources, get_subscription_name, days_text, get_time_when_refresh
from drug_search.core.lexicon.enums import SUBSCRIBE_TYPES
from drug_search.core.schemas import UserSchema, DrugSchema, CombinationType, AllowedDrugsInfoSchema
from schemas import DrugDosageSchema


class DrugMessageFormatter:
    """Форматирование сообщений о препаратах"""

    @staticmethod
    def format_drug_briefly(drug: DrugSchema) -> str:
        """Форматирование краткой информации о препарате"""
        return MessageTemplates.DRUG_INFO_BRIEFLY.format(
            drug_name_ru=drug.name_ru,
            drug_name=drug.name,
            latin_name=drug.latin_name,
            classification=drug.classification,
            description=drug.description,
            clinical_effects=drug.clinical_effects,
            fun_fact=drug.fact or ""
        )

    @staticmethod
    def format_mechanism(drug: DrugSchema) -> str:
        """Форматирование информации о путях воздействия"""
        pathways_list: str = ""

        pathways: set = {pathway.pathway for pathway in
                         drug.pathways}  # все пути (например, Androgen receptor signaling pathway)

        google_sources: list[dict] = make_google_sources(drug.pathways_sources)
        sources_num: list = [
            f"<a href='{source["google_url"]}'><b>{i}</b></a>"
            for i, source in enumerate(google_sources, start=1)
        ]
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

        secondary_actions_section = f"<b>Вторичные действия:\n</b>{drug.secondary_actions}\n\n" if drug.secondary_actions else ""

        return MessageTemplates.DRUG_INFO_PATHWAYS.format(
            sources_section=sources_section,
            drug_name_ru=drug.name_ru,
            pathways_list=pathways_list,
            primary_action=drug.primary_action,
            secondary_actions_section=secondary_actions_section,

        )

    @staticmethod
    def format_combinations(drug: DrugSchema) -> str:
        """Форматирование информации о взаимодействиях"""
        good_combinations: str = ""
        bad_combinations: str = ""

        for combination in drug.combinations:
            comb_products: str = ""
            if combination.combination_type == CombinationType.GOOD:
                comb_products = f'({", ".join(combination.products)})'

            combination_text: str = f"        <b>▻ {combination.substance} {comb_products}</b>\n"
            combination_text += f"        <u>{combination.effect}</u>\n"

            if combination.combination_type == CombinationType.GOOD:
                good_combinations += f"{combination_text}\n"

            if combination.combination_type == CombinationType.BAD:
                combination_text += f"        <b>Вред:</b> {combination.risks.lower()}\n"

                bad_combinations += f"{combination_text}\n"

        return MessageTemplates.DRUG_INFO_COMBINATIONS.format(
            drug_name_ru=drug.name_ru,
            good_combinations=good_combinations or "Нет данных",
            bad_combinations=bad_combinations or "Нет данных"
        )

    @staticmethod
    def format_dosages(drug: DrugSchema) -> str:
        """Форматирование информации о дозировках"""

        def format_dosage_info(
                dosage: DrugDosageSchema,
                symbol: str
        ) -> str:
            """Форматирует информацию об одной дозировке"""
            sections = [
                f"<b>{symbol} <u>{dosage.method.capitalize()}</u></b>",

                f"<b>Разовая дозировка:</b> {dosage.per_time} <i>"
                f"{f'({dosage.per_time_weight_based})' if dosage.per_time_weight_based else ''}</i>" if dosage.per_time else None,

                f"<b>Макс. в сутки:</b> {dosage.max_day} <i>"
                f"{f'({dosage.max_day_weight_based})' if dosage.max_day_weight_based else ''}</i>" if dosage.max_day else None,

                f"<b>Время начала действия:</b> {dosage.onset}" if dosage.onset else None,
                f"<b>Период полувыведения:</b> {dosage.half_life}" if dosage.half_life else None,
                f"<b>Продолжительность действия:</b> {dosage.duration}" if dosage.duration else None,

                dosage.notes if dosage.notes else None
            ]

            return "\n".join(filter(None, sections))

        def create_sources_section(sources: list[dict]) -> str:
            """Создает секцию с источниками в виде пронумерованных ссылок"""
            source_links = [
                f"<a href='{source['google_url']}'><b>{i}</b></a>"
                for i, source in enumerate(sources, start=1)
            ]
            return ' '.join(source_links)

        # [ формирование секции с источниками ]
        google_sources = make_google_sources(drug.dosage_sources)
        sources_section = create_sources_section(google_sources)

        # [ формирование списка всех дозировок ]
        dosages_list = "\n\n".join(
            format_dosage_info(dosage, SYMBOLS[i])
            for i, dosage in enumerate(drug.dosages)
        )

        if dosages_list:
            dosages_list += "\n\n"

        dosage_fun_fact_section = f"{drug.dosages_fun_facts}\n\n" if drug.dosages_fun_facts else ""

        return MessageTemplates.DRUG_INFO_DOSAGES.format(
            drug_name_ru=drug.name_ru,
            dosages_list=dosages_list,
            sources_section=sources_section,
            dosage_fun_fact_section=dosage_fun_fact_section
        )

    @staticmethod
    def format_analogs(drug: DrugSchema) -> str:
        """Форматирование аналогов"""
        analogs_section: str = ""
        for i, analog in enumerate(sorted(drug.analogs, key=lambda x: x.percent, reverse=True), start=1):
            analogs_section += f"<b>{i}) " + analog.analog_name + "</b>\n"
            analogs_section += "        " + analog.difference + "\n"
            analogs_section += f"        <u>схожесть</u>: {str(analog.percent)}% \n\n"

        analogs_description: str = drug.analogs_description + "\n\n" if drug.analogs_description else ""

        return MessageTemplates.DRUGS_ANALOGS.format(
            drug_name_ru=drug.name_ru,
            analogs_description=analogs_description,
            analogs_section=analogs_section
        )

    @staticmethod
    def format_metabolism(drug: DrugSchema) -> str:
        """Фармакокинетика форматирование"""

        # [ биодоступность для разных методов ]
        absorption: str | None = "<b>Биодоступность:</b>\n" + drug.absorption + "\n\n" if drug.absorption else ""

        # TODO: пути метаболизма оформить как "Фаза I: ...\nФаза II: ..."
        # [ пути метаболизма ]
        metabolism: str | None = "<b>Метаболизм:</b>\n" + drug.metabolism + "\n\n" if drug.metabolism else ""

        elimination: str | None = "<b>Выведение:</b>\n" + drug.elimination + "\n\n" if drug.elimination else ""

        pharmacokinetics = absorption + metabolism + elimination
        pharmacokinetics += f"Максимальная концентрация в крови достигает через <b><u>{drug.time_to_peak}</u></b>" \
            if drug.time_to_peak else ""

        metabolism_description: str = drug.metabolism_description + "\n\n" if drug.metabolism_description else ""

        return MessageTemplates.DRUG_INFO_METABOLISM.format(
            drug_name_ru=drug.name_ru,
            metabolism_description=metabolism_description,
            pharmacokinetics=pharmacokinetics
        )

    @staticmethod
    def format_researches(drug: DrugSchema) -> str:
        """Форматирование информации об исследованиях"""
        researches_list = ""
        for research in drug.researches:
            researches_list += f"<a href='{research.url}'><b>{research.publication_date}</b></a>\n"
            researches_list += f"<b>{research.name}</b>\n"
            researches_list += f"{research.summary}\n\n" if research.summary else research.description

        return MessageTemplates.DRUG_INFO_RESEARCHES.format(
            drug_name_ru=drug.name_ru,
            researches_list=researches_list or "Нет данных об исследованиях."
        )

    @staticmethod
    def format_drugs_info(allowed_drugs_info: AllowedDrugsInfoSchema) -> str:
        return MessageTemplates.DRUGS_INFO.format(
            len_allowed_drugs=allowed_drugs_info.allowed_drugs_count,
        )

    @staticmethod
    def format_drug_update_info(drug: DrugSchema):
        return MessageTemplates.DRUG_UPDATE_INFO.format(
            drug_name=drug.name_ru,
            drug_last_update=drug.updated_at
        )

    @staticmethod
    def format_by_type(describe_type: DescribeTypes, drug: DrugSchema) -> str:
        """Форматирование информации в зависимости от типа описания"""
        format_methods = {
            DescribeTypes.BRIEFLY: DrugMessageFormatter.format_drug_briefly,
            DescribeTypes.DOSAGES: DrugMessageFormatter.format_dosages,
            DescribeTypes.MECHANISM: DrugMessageFormatter.format_mechanism,
            DescribeTypes.COMBINATIONS: DrugMessageFormatter.format_combinations,
            DescribeTypes.RESEARCHES: DrugMessageFormatter.format_researches,
            DescribeTypes.METABOLISM: DrugMessageFormatter.format_metabolism,
            DescribeTypes.ANALOGS: DrugMessageFormatter.format_analogs,
            DescribeTypes.UPDATE_INFO: DrugMessageFormatter.format_drug_update_info
        }

        method = format_methods.get(describe_type)
        if method:
            return method(drug)
        else:
            raise "Неизвестный тип описания"


class UserProfileMessageFormatter:
    """Форматирование пользовательских сообщений"""

    @staticmethod
    def format_user_profile(user: UserSchema) -> str:
        """Форматирование профиля пользователя"""
        profile_icon: str = ""
        match user.subscription_type:
            case SUBSCRIBE_TYPES.DEFAULT:
                profile_icon = "🪰"
            case SUBSCRIBE_TYPES.LITE:
                profile_icon = "🧢"
            case SUBSCRIBE_TYPES.PREMIUM:
                profile_icon = "👑"

        subscription: str = f"<u>Подписка:</u> {get_subscription_name(user.subscription_type)}"
        subscription_end: str = f" <i>(ещё {days_text(user.subscription_end)})</i>\n\n" if user.subscription_end else "\n\n"
        subscription_section = subscription + subscription_end

        refresh_section: str = get_time_when_refresh(user.requests_last_refresh)

        return MessageTemplates.USER_PROFILE.format(
            profile_icon=profile_icon,
            allowed_search_requests=user.allowed_search_requests,
            allowed_question_requests=user.allowed_question_requests,
            refresh_section=refresh_section,
            subscription_section=subscription_section
        )

    @staticmethod
    def format_user_description_profile(user: UserSchema):
        """Описание юзера в его профиле"""
        profile_icon: str = ""
        match user.subscription_type:
            case SUBSCRIBE_TYPES.DEFAULT:
                profile_icon = "🪰"
            case SUBSCRIBE_TYPES.LITE:
                profile_icon = "🧢"
            case SUBSCRIBE_TYPES.PREMIUM:
                profile_icon = "👑"

        user_description: str = '.\n\n'.join(user.description.split(". ")) if user.description else ""

        return MessageTemplates.USER_PROFILE_DESCRIPTION.format(
            profile_icon=profile_icon,
            description_section=user_description,
        )
