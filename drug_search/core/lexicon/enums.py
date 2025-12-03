from enum import Enum
from typing import Optional

from drug_search.core.lexicon import SMALL_PACKET, ENTERPRISE_PACKET, ULTIMATE_PACKET, PRO_PACKET, BASIC_PACKET


class SUBSCRIPTION_TYPES(str, Enum):
    """Типы подписок"""
    DEFAULT = "DEFAULT"
    LITE = "LITE"  # 10 запросов в день
    PREMIUM = "PREMIUM"  # безлимит + подписка на запрещенку


class ACTIONS_FROM_ASSISTANT(str, Enum):
    DRUG_SEARCH = "drug_search"
    DRUG_MENU = "drug_menu"
    QUESTION = "question"
    QUESTION_DRUGS = "question_drugs"
    SPAM = "spam"  # будет давать предупреждение, в случае повтора даст мут
    OTHER = "other"


class EXIST_STATUS(str, Enum):
    EXIST: str = "exist"
    NOT_EXIST: str = "not exist"


class DANGER_CLASSIFICATION(str, Enum):
    SAFE: str = "SAFE"
    PREMIUM_NEED: str = "PREMIUM_NEED"
    DANGER: str = "DANGER"


class ARROW_TYPES(str, Enum):
    BACK = "back"
    FORWARD = "forward"


class JobStatuses(str, Enum):
    QUEUED = "queued"
    CREATED = "created"


# [ api response ]
class MailingStatuses(str, Enum):
    SUCCESS = "success"
    ONLY_FOR_ADMINS = "only_for_admins"


# [ Payment ]
class TokenPackage(Enum):
    """Пакеты токенов с указанием количества для покупки"""

    # [ key, название_пакета, количество_токенов, цена ]
    SMALL = ("small", f"{SMALL_PACKET} токенов", SMALL_PACKET, 199.0)
    BASIC = ("basic", f"{BASIC_PACKET} токенов", BASIC_PACKET, 399.0)
    PRO = ("pro", f"{PRO_PACKET} токенов", PRO_PACKET, 899.0)
    ENTERPRISE = ("business", f"{ENTERPRISE_PACKET} токенов", ENTERPRISE_PACKET, 1099.0)
    ULTIMATE = ("maximum", f"{ULTIMATE_PACKET} токенов", ULTIMATE_PACKET, 1900.0)

    @property
    def key(self):
        """Возвращает ключ пакета"""
        return self.value[0]

    @property
    def name(self):
        """Возвращает название пакета"""
        return self.value[1]

    @property
    def amount(self):
        """Возвращает количество токенов в пакете"""
        return self.value[2]

    @property
    def price(self):
        """Возвращает цену пакета"""
        return self.value[3]

    @classmethod
    def get_by_key(cls, package_key: str):
        """Получить пакет по key"""
        for package in cls:
            if package.key == package_key:
                return package
        raise ValueError(f"Unknown package ID: {package_key}")

    @classmethod
    def get_token_packages(cls) -> tuple["TokenPackage", ...]:
        return cls.SMALL, cls.BASIC, cls.PRO, cls.ENTERPRISE, cls.ULTIMATE


class SubscriptionPackage(Enum):
    """Пакеты с подписками

    ЦЕНЫ
    ДЛИТЕЛЬНОСТЬ
    """

    # LITE: в день 20 токенов
    # PREMIUM: в день безлимит или 100 токенов

    # [ Ключ, Название пакета (длительность), Тип подписки, длительность, цена ]

    # [ 7 дней ]
    LITE_7_PACKAGE = ("two_weeks_lite", "Неделя", SUBSCRIPTION_TYPES.LITE, "7", 299.0)

    # [ 14 дней ]
    PREMIUM_14_PACKAGE = ("two_weeks_premium", "Две недели", SUBSCRIPTION_TYPES.PREMIUM, "14", 899.0)

    # [ 30 дней ]
    LITE_30_PACKAGE = ("one_months_lite", "Месяц", SUBSCRIPTION_TYPES.LITE, "30", 1090.0)

    # [ 90 дней ]
    PREMIUM_90_PACKAGE = ("three_months_premium", "Три месяца", SUBSCRIPTION_TYPES.PREMIUM, "90", 2199.0)

    # [ 180 дней ]
    PREMIUM_180_PACKAGE = ("six_months_premium", "Полгода", SUBSCRIPTION_TYPES.PREMIUM, "180", 3290.0)

    # [ 365 дней ]
    PREMIUM_365_PACKAGE = ("year_premium", "Год", SUBSCRIPTION_TYPES.PREMIUM, "365", 4990.0)

    @property
    def key(self) -> str:
        return self.value[0]

    @property
    def name(self) -> str:
        return self.value[1]

    @property
    def subscription_type(self) -> str:
        """Тип подписки"""
        match self.value[2]:
            case SUBSCRIPTION_TYPES.PREMIUM:
                return "Премиум"
        match self.value[2]:
            case SUBSCRIPTION_TYPES.LITE:
                return "Лайт"
        return ""

    @property
    def duration(self) -> int:
        """длительность в целых днях"""
        return int(self.value[3])

    def price(self, subscription_days: int = 0) -> float:
        base_price = self.value[4]

        # Коэффициенты скидки в зависимости от количества дней
        days_discount = self._calculate_discount(subscription_days)

        # Применяем оба коэффициента
        final_price = base_price * days_discount

        return round(final_price, 2)

    def _calculate_discount(self, days: int) -> float:
        """Рассчитывает скидку в зависимости от количества дней"""
        return 1.0 - (days / 250)

    @classmethod
    def get_by_key(cls, package_key: str):
        """Получить пакет по key"""
        for package in cls:
            if package.key == package_key:
                return package
        raise ValueError(f"Unknown package ID: {package_key}")

    @classmethod
    def get_packages_by_type(cls, subscription_type: SUBSCRIPTION_TYPES) -> None | tuple["SubscriptionPackage", ...]:
        match subscription_type:
            case SUBSCRIPTION_TYPES.LITE:
                return cls.LITE_7_PACKAGE, cls.LITE_30_PACKAGE
            case SUBSCRIPTION_TYPES.PREMIUM:
                return cls.PREMIUM_14_PACKAGE, cls.PREMIUM_90_PACKAGE, cls.PREMIUM_180_PACKAGE, cls.PREMIUM_365_PACKAGE


class TOKENS_LIMIT(int, Enum):
    """
    Дневные | Недельные лимиты (в зависимости от типа подписки) токенов
    """
    TOKENS_AFTER_REGISTRATION = 5
    DEFAULT_TOKENS_LIMIT = 0

    LITE_TOKENS_LIMIT = 50

    PREMIUM_TOKENS_LIMIT = 100

    @classmethod
    def get_days_interval_to_refresh_tokens(cls, subscription_type: SUBSCRIPTION_TYPES) -> int | None:
        match subscription_type:
            case SUBSCRIPTION_TYPES.DEFAULT:
                return 0  # не обновляются
            case SUBSCRIPTION_TYPES.LITE:
                return 7
            case SUBSCRIPTION_TYPES.PREMIUM:
                return 1

    @classmethod
    def get_limits_from_subscription_type(cls, subscription_type: SUBSCRIPTION_TYPES) -> Optional[int]:
        match subscription_type:
            case SUBSCRIPTION_TYPES.DEFAULT:
                return cls.DEFAULT_TOKENS_LIMIT.value
            case SUBSCRIPTION_TYPES.LITE:
                return cls.LITE_TOKENS_LIMIT.value
            case SUBSCRIPTION_TYPES.PREMIUM:
                return cls.PREMIUM_TOKENS_LIMIT.value


class DrugMenu(str, Enum):
    BRIEFLY = "Briefly"
    DOSAGES = "Dosages"
    MECHANISM = "Mechanism"
    COMBINATIONS = "Combinations"
    RESEARCHES = "Researches"
    ANALOGS = "Analogs"
    METABOLISM = "Metabolism"
    UPDATE_INFO = "UpdateInfo"
