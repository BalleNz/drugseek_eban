from enum import Enum


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
    STARTER = ("small", "Малый пакет", 10, 199.0)
    BASIC = ("basic", "Базовый пакет", 25, 399.0)
    PRO = ("pro", "Профессиональный пакет", 50, 899.0)
    ENTERPRISE = ("business", "Бизнес пакет", 70, 1099.0)
    ULTIMATE = ("maximum", "Максимальный пакет", 200, 1900.0)

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
        return cls.STARTER, cls.BASIC, cls.PRO, cls.ENTERPRISE, cls.ULTIMATE


class SubscriptionPackage(Enum):
    """Пакеты с подписками"""
    # LITE: в день 20 токенов
    # PREMIUM: в день безлимит или 100 токенов

    # [ Ключ, Название пакета (длительность), Тип подписки, длительность, цена ]
    # [ 14 дней ]
    LITE_14_PACKAGE = ("two_weeks_lite", "Две недели", SUBSCRIPTION_TYPES.LITE, "14", 299.0)
    PREMIUM_14_PACKAGE = ("two_weeks_premium", "Две недели", SUBSCRIPTION_TYPES.PREMIUM, "14", 599.0)

    # [ 90 дней ]
    LITE_90_PACKAGE = ("three_months_lite", "Три месяца", SUBSCRIPTION_TYPES.LITE, "90", 1190.0)
    PREMIUM_90_PACKAGE = ("three_months_premium", "Три месяца", SUBSCRIPTION_TYPES.PREMIUM, "90", 1799.0)

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
    def subscription_type(self) -> SUBSCRIPTION_TYPES:
        return self.value[2]

    @property
    def duration(self) -> str:
        return self.value[3]

    @property
    def price(self) -> float:
        return self.value[4]

    @classmethod
    def get_by_key(cls, package_key: str):
        """Получить пакет по key"""
        for package in cls:
            if package.key == package_key:
                return package
        raise ValueError(f"Unknown package ID: {package_key}")

    def price_with_discount(self, discount: float) -> float:
        """Стоимость подписки со скидкой (в процентах)"""
        return self.price * (1 - discount)

    @classmethod
    def get_packages_by_type(cls, subscription_type: SUBSCRIPTION_TYPES) -> None | tuple["SubscriptionPackage", ...]:
        match subscription_type:
            case SUBSCRIPTION_TYPES.LITE:
                return cls.LITE_14_PACKAGE, cls.LITE_90_PACKAGE
            case SUBSCRIPTION_TYPES.PREMIUM:
                return cls.PREMIUM_14_PACKAGE, cls.PREMIUM_90_PACKAGE, cls.PREMIUM_180_PACKAGE, cls.PREMIUM_365_PACKAGE
