import datetime
import logging
import random

from drug_search.bot.lexicon.consts import SYMBOLS
from drug_search.bot.lexicon.enums import DrugMenu
from drug_search.bot.lexicon.message_templates import MessageTemplates
from drug_search.bot.utils.funcs import make_google_sources, get_time_when_refresh_tokens_text, \
    decline_tokens
from drug_search.core.lexicon.enums import SUBSCRIPTION_TYPES, TOKENS_LIMIT
from drug_search.core.schemas import UserSchema, DrugSchema, CombinationType, AllowedDrugsInfoSchema

logger = logging.getLogger(__name__)


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
    def format_pathways(drug: DrugSchema) -> str:
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

            pathway_info += f"<b>└─ <u>{drug_pathway.receptor}</u></b>\n"
            pathway_info += f"<b>└── Тип:</b> {drug_pathway.activation_type}\n"
            pathway_info += f"<b>└── Эффект:</b> {drug_pathway.effect}\n"
            pathway_info += f"<b>└── Сила связи:</b> {drug_pathway.affinity_description} | {drug_pathway.binding_affinity}\n"
            pathway_info += f"<b>└── Что делает:</b> {drug_pathway.note}\n"

            pathways_list += pathway_info

        secondary_actions_section = f"<b>Вторичные действия:\n</b>{drug.secondary_actions.capitalize()}.\n\n" if drug.secondary_actions else ""

        return MessageTemplates.DRUG_INFO_PATHWAYS.format(
            sources_section=sources_section,
            drug_name_ru=drug.name_ru.upper(),
            pathways_list=pathways_list,
            primary_action=drug.primary_action.capitalize() + ".",
            secondary_actions_section=secondary_actions_section,
        )

    @staticmethod
    def format_combinations(drug: DrugSchema) -> str:
        """Форматирование информации о взаимодействиях"""
        good_combinations: str = ""
        bad_combinations: str = ""

        for combination in drug.combinations:
            comb_products: str = ""

            # if combination.combination_type == CombinationType.GOOD:
            #     comb_products = f'({", ".join(combination.products)})'
            combination_text: str = f"<b>{combination.substance}</b> <i>{comb_products}</i>\n"

            combination_text += f"<b>└──</b> {combination.effect}\n"

            if combination.combination_type == CombinationType.GOOD:
                good_combinations += f"<b>└─</b> {combination_text}"

            if combination.combination_type == CombinationType.BAD:
                combination_text += f"<b>└──</b> {combination.risks.capitalize()}\n"

                bad_combinations += f"<b>└─</b> {combination_text}"

        return MessageTemplates.DRUG_INFO_COMBINATIONS.format(
            drug_name_ru=drug.name_ru.upper(),
            good_combinations=good_combinations or "Нет данных",
            bad_combinations=bad_combinations or "Нет данных"
        )

    @staticmethod
    def format_dosages(drug: DrugSchema) -> str:
        """Форматирование информации о дозировках"""

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
        dosages = ""
        for i, dosage in enumerate(drug.dosages):
            dosages += f"{SYMBOLS[i]} <b>{dosage.method.capitalize()}</b>\n"
            dosages += f"<b>└── Разовая дозировка:</b> {dosage.per_time} "
            if dosage.max_day:
                dosages += f"<i>(макс. {dosage.max_day} в день)</i>"
            dosages += "\n"

            if dosage.per_time_weight_based and dosage.max_day_weight_based:
                dosages += f"<b>└── Дозировка на вес тела:</b> {dosage.per_time_weight_based} <i>(макс. {dosage.max_day_weight_based} в день)</i>\n"

            dosages += f"<b>└──</b> {dosage.notes.capitalize()}.\n\n"

        dosages_fun_fact = f"{random.choice(drug.fun_facts)}\n\n"

        return MessageTemplates.DRUG_INFO_DOSAGES.format(
            drug_name_ru=drug.name_ru.upper(),
            dosages=dosages,
            sources_section=sources_section,
            dosages_fun_fact=dosages_fun_fact
        )

    @staticmethod
    def format_analogs(drug: DrugSchema) -> str:
        """Форматирование аналогов"""
        analogs_section: str = ""
        for i, analog in enumerate(sorted(drug.analogs, key=lambda x: x.percent, reverse=True), start=1):
            analogs_section += f"<b>{SYMBOLS[i]} {analog.analog_name}</b> <i>({str(analog.percent)}% схожести)</i>\n"
            analogs_section += f"<b>└─ </b>{analog.difference}\n\n"

        analogs_description: str = drug.analogs_description + "\n\n" if drug.analogs_description else ""

        return MessageTemplates.DRUGS_ANALOGS.format(
            drug_name_ru=drug.name_ru.upper(),
            analogs_description=analogs_description,
            analogs_section=analogs_section
        )

    @staticmethod
    def format_metabolism(drug: DrugSchema) -> str:
        """Фармакокинетика форматирование"""

        # [ пути метаболизма ]
        metabolism_phases = {
            "-1": "Экскреция",
            "1": "Фаза Ⅰ",
            "2": "Фаза Ⅱ",
            "3": "Фаза Ⅲ",
            "4": "Фаза Ⅳ",
            "5": "Фаза Ⅴ",
            "6": "Фаза Ⅵ",
        }
        metabolism: str = ""
        met_phases = []
        for met_pathway in drug.metabolism:
            # [ проверка была ли эта фаза ]
            if met_pathway.phase not in met_phases:
                met_phases.append(met_pathway.phase)
                metabolism += f"<b>└─ <u>{metabolism_phases[met_pathway.phase]}</u></b>\n"

            metabolism += f"<b>└── {met_pathway.process.capitalize()}: </b>"
            metabolism += f"<i>{met_pathway.result}</i>\n"

        # [ биодоступность для разных методов ]
        pharmacokinetics: str = ""
        for absorption_adm_method in drug.pharmacokinetics:
            pharmacokinetics += f"<b>└─ <u>{absorption_adm_method.route.capitalize()}</u></b>\n"
            pharmacokinetics += f"<b>└── Биодоступность:</b> {absorption_adm_method.bioavailability}%\n"
            pharmacokinetics += f"<b>└── Начало действия:</b> {absorption_adm_method.onset}\n"
            pharmacokinetics += f"<b>└── Cmax через:</b> {absorption_adm_method.time_to_peak}\n"
            pharmacokinetics += f"<b>└── Период полувыведения:</b> {absorption_adm_method.half_life}\n"
            pharmacokinetics += f"<b>└── Продолжительность действия:</b> {absorption_adm_method.duration}\n"

        # [ пути выведения ]
        elimination: str = ""
        for elimination_path in drug.elimination:
            elimination += f"<b>└─ <u>{elimination_path.excrement_type.capitalize()}</u>:</b> ~{elimination_path.output_percent}%\n"

        metabolism_description: str = drug.metabolism_description if drug.metabolism_description else ""

        return MessageTemplates.DRUG_INFO_METABOLISM.format(
            drug_name_ru=drug.name_ru.upper(),
            metabolism=metabolism,
            absorption=pharmacokinetics,
            elimination=elimination,
            metabolism_description=metabolism_description,
        )

    @staticmethod
    def format_researches(drug: DrugSchema, research_number: int) -> str:
        """Форматирование информации об исследованиях"""
        research_text: str | None = None
        if drug.researches:
            logger.info(f"research_number: {research_number}")
            research = drug.researches[research_number]

            research_text: str = ""
            if research.header_name:
                research_text += f"<b>{research.header}:</b>\n"
                research_text += f"<b>—</b> <a href='{research.url}'>{research.header_name}.</a>\n\n"
            else:
                research_text += f"<b><a href='{research.url}'>{research.header}</a></b>\n\n"

            research_text += f"<b>Дата:</b> {research.publication_date}\n"
            reading_level: str = "Лёгкий" if float(research.interest) > 0.8 else "Сложный"
            research_text += f"<b>Тип чтения:</b> {reading_level}\n\n"

            research_text += f"{research.description}\n\n"
            research_text += f"<b>Вывод</b>: {research.summary}\n"

        return MessageTemplates.DRUG_INFO_RESEARCHES.format(
            drug_name_ru=drug.name_ru.upper(),
            researches_list=research_text or "Исследования создаются, зайдите через минуту! \n(или их не существует для этого препарата)"
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
    def format_by_type(drug_menu: DrugMenu, drug: DrugSchema) -> str:
        """Форматирование информации в зависимости от типа описания"""
        format_methods = {
            DrugMenu.BRIEFLY: DrugMessageFormatter.format_drug_briefly,
            DrugMenu.DOSAGES: DrugMessageFormatter.format_dosages,
            DrugMenu.MECHANISM: DrugMessageFormatter.format_pathways,
            DrugMenu.COMBINATIONS: DrugMessageFormatter.format_combinations,
            DrugMenu.RESEARCHES: DrugMessageFormatter.format_researches,
            DrugMenu.METABOLISM: DrugMessageFormatter.format_metabolism,
            DrugMenu.ANALOGS: DrugMessageFormatter.format_analogs,
            DrugMenu.UPDATE_INFO: DrugMessageFormatter.format_drug_update_info
        }

        method = format_methods.get(drug_menu)
        if drug_menu == DrugMenu.RESEARCHES:
            return DrugMessageFormatter.format_researches(
                drug, 0
            )
        elif method:
            return method(drug)
        else:
            raise f"Неизвестный тип описания: {drug_menu}"


class UserProfileMessageFormatter:
    """Форматирование пользовательских сообщений"""

    @staticmethod
    def format_user_profile(user: UserSchema) -> str:
        """Форматирование профиля пользователя"""
        profile_name: str = ""
        profile_icon: str = ""
        match user.subscription_type:
            case SUBSCRIPTION_TYPES.DEFAULT:
                profile_name = "Ограниченный профиль"
                profile_icon = "🪰"
            case SUBSCRIPTION_TYPES.LITE:
                profile_name = "Профиль"
                profile_icon = "🧢"
            case SUBSCRIPTION_TYPES.PREMIUM:
                profile_name = "Премиум профиль"
                profile_icon = "💎"

        def get_subscription_end_at_text(subscription_end_at: datetime.datetime) -> str:
            """Получить текст конца подписки

            пример:
            — Подписка заканчивается через 3 дня.
            """
            now = datetime.datetime.now()
            time_difference = subscription_end_at - now

            # Если подписка уже истекла
            if time_difference.total_seconds() <= 0:
                return "— Подписка истекла."

            # Разбиваем разницу на составляющие
            days = time_difference.days
            hours = time_difference.seconds // 3600
            minutes = (time_difference.seconds % 3600) // 60
            seconds = time_difference.seconds % 60

            # Определяем подходящую единицу времени для отображения
            if days > 0:
                if days == 1:
                    return f"Подписка заканчивается через 1 день."
                elif str(days)[-1] in ("2", "3", "4"):
                    return f"Подписка заканчивается через {days} дня."
                else:
                    return f"Подписка заканчивается через {days} дней."
            elif hours > 0:
                if hours == 1:
                    return f"Подписка заканчивается через 1 час."
                elif str(hours)[-1] in ("2", "3", "4"):
                    return f"Подписка заканчивается через {hours} часа."
                else:
                    return f"Подписка заканчивается через {hours} часов."
            elif minutes > 0:
                if minutes == 1:
                    return f"Подписка заканчивается через 1 минуту."
                elif str(minutes)[-1] in ("2", "3", "4"):
                    return f"Подписка заканчивается через {minutes} минуты."
                else:
                    return f"Подписка заканчивается через {minutes} минут."
            else:
                if seconds == 1:
                    return f"Подписка заканчивается через 1 секунду."
                elif str(seconds)[-1] in ("2", "3", "4"):
                    return f"Подписка заканчивается через {seconds} секунды."
                else:
                    return f"Подписка заканчивается через {seconds} секунд."

        refresh_section: str = get_time_when_refresh_tokens_text(
            user.tokens_last_refresh,
            subscription_type=user.subscription_type
        )

        allowed_tokens = f"<u>{user.allowed_tokens}</u> / {TOKENS_LIMIT.get_limits_from_subscription_type(
            user.subscription_type
        )}"

        additional_tokens_text = f"Дополнительные токены: <u>{user.additional_tokens}</u>"

        return MessageTemplates.USER_PROFILE.format(
            profile_name=profile_name,
            profile_icon=profile_icon,
            refresh_section="||  " + refresh_section if refresh_section else "",
            allowed_tokens=allowed_tokens,
            token_word=decline_tokens(user.allowed_tokens),
            additional_tokens_text=additional_tokens_text if additional_tokens_text else "",
            additional_tokens_quote="<blockquote>Когда закончатся стандартные токены, начнут расходоваться дополнительные.</blockquote>\n\n" if additional_tokens_text else "",
            subscription_end_at=get_subscription_end_at_text(user.subscription_end) if user.subscription_end else ""
        )

    @staticmethod
    def format_user_description_profile(user: UserSchema):
        """Описание юзера в его профиле"""
        profile_icon: str = ""
        match user.subscription_type:
            case SUBSCRIPTION_TYPES.DEFAULT:
                profile_icon = "🪰"
            case SUBSCRIPTION_TYPES.LITE:
                profile_icon = "🧢"
            case SUBSCRIPTION_TYPES.PREMIUM:
                profile_icon = "👑"

        user_description: str = '.\n\n'.join(user.description.split(". ")) if user.description else ""

        return MessageTemplates.USER_PROFILE_DESCRIPTION.format(
            profile_icon=profile_icon,
            description_section=user_description,
        )
