from enum import Enum


class SUBSCRIBE_TYPES(str, Enum):
    DEFAULT = "DEFAULT"
    LITE = "LITE"  # 10 запросов в день
    PREMIUM = "PREMIUM"  # безлимит + подписка на запрещенку


class ACTIONS_FROM_ASSISTANT(str, Enum):
    DRUG_SEARCH = "drug_search"
    DRUG_MENU = "drug_menu"
    QUESTION = "question"
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
