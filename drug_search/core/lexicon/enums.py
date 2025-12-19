from enum import Enum
from typing import Optional


class SubscriptionKeys(str, Enum):
    """Ключи подписок

    sub + duration_count + duration_type + sub_type
    """
    TWO_WEEKS_LITE = "sub_two_weeks_lite"
    TWO_WEEKS_PREMIUM = "sub_two_weeks_premium"
    ONE_MONTH_LITE = "sub_one_months_lite"
    THREE_MONTHS_PREMIUM = "sub_three_months_premium"
    SIX_MONTHS_PREMIUM = "sub_six_months_premium"
    YEAR_PREMIUM = "sub_one_year_premium"


class TokenKeys(str, Enum):
    """Ключи токенов

    tokens + package_name
    """
    SMALL = "tokens_small"
    BASIC = "tokens_basic"
    PRO = "tokens_pro"
    BUSINESS = "tokens_business"
    MAXIMUM = "tokens_maximum"


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
class TokensPackage(Enum):
    """Пакеты токенов с указанием количества для покупки"""

    # [ key, название_пакета, количество_токенов, цена ]
    SMALL = (TokenKeys.SMALL.value, "10 токенов", 10, 199)
    BASIC = (TokenKeys.BASIC.value, "25 токенов", 25, 499)
    PRO = (TokenKeys.PRO.value, "60 токенов", 60, 899)
    BUSINESS = (TokenKeys.BUSINESS.value, "100 токенов", 100, 1299)
    MAXIMUM = (TokenKeys.MAXIMUM.value, "200 токенов", 200, 1990)

    @property
    def key(self):
        """Возвращает ключ пакета"""
        return self.value[0]

    @property
    def name(self) -> str:
        """Возвращает название пакета"""
        return self.value[1]

    @property
    def quantity(self) -> int:
        """Возвращает количество токенов в пакете"""
        return self.value[2]

    @property
    def price(self) -> int:
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
    def get_token_packages(cls) -> tuple["TokensPackage", ...]:
        return cls.SMALL, cls.BASIC, cls.PRO, cls.BUSINESS, cls.MAXIMUM


class SubscriptionPackage(Enum):
    """Пакеты с подписками

    ЦЕНЫ
    ДЛИТЕЛЬНОСТЬ
    """

    # LITE: в день 20 токенов
    # PREMIUM: в день безлимит или 100 токенов

    # [ Ключ, Название пакета (длительность), Тип подписки, длительность, цена ]

    # [ 7 дней ]
    LITE_7_PACKAGE = (SubscriptionKeys.TWO_WEEKS_LITE.value, "Неделя", SUBSCRIPTION_TYPES.LITE, "7", 299)

    # [ 14 дней ]
    PREMIUM_14_PACKAGE = (SubscriptionKeys.TWO_WEEKS_PREMIUM.value, "Две недели", SUBSCRIPTION_TYPES.PREMIUM, "14", 899)

    # [ 30 дней ]
    LITE_30_PACKAGE = (SubscriptionKeys.ONE_MONTH_LITE.value, "Месяц", SUBSCRIPTION_TYPES.LITE, "30", 1090)

    # [ 90 дней ]
    PREMIUM_90_PACKAGE = (SubscriptionKeys.THREE_MONTHS_PREMIUM.value, "Три месяца", SUBSCRIPTION_TYPES.PREMIUM, "90", 2199)

    # [ 180 дней ]
    PREMIUM_180_PACKAGE = (SubscriptionKeys.SIX_MONTHS_PREMIUM.value, "Полгода", SUBSCRIPTION_TYPES.PREMIUM, "180", 3290)

    # [ 365 дней ]
    PREMIUM_365_PACKAGE = (SubscriptionKeys.YEAR_PREMIUM.value, "Год", SUBSCRIPTION_TYPES.PREMIUM, "365", 4990)

    @property
    def key(self) -> str:
        return self.value[0]

    @property
    def name(self) -> str:
        return self.value[1]

    @property
    def subscription_type(self) -> SUBSCRIPTION_TYPES:
        """Тип подписки"""
        return self.value[2]

    @property
    def subscription_type_text(self) -> str:
        """Тип подписки текстом"""
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

    def price(self, subscription_days: int = 0) -> int:
        base_price = self.value[4]

        # Коэффициенты скидки в зависимости от количества дней
        days_discount = self._calculate_discount(subscription_days)

        # Применяем оба коэффициента
        final_price = base_price * days_discount

        return round(final_price, 2)

    def _calculate_discount(self, days: int) -> int:
        """Рассчитывает скидку в зависимости от количества дней"""
        return int(1.0 - (days / 250))

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
    TOKENS_AFTER_REGISTRATION = 1
    DEFAULT_TOKENS_LIMIT = 0

    LITE_TOKENS_LIMIT = 50  # в неделю

    PREMIUM_TOKENS_LIMIT = 50

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
