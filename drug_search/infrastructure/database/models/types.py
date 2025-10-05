from sqlalchemy import Enum

from drug_search.core.lexicon.enums import DANGER_CLASSIFICATION, SUBSCRIBE_TYPES

DangerClassificationEnum = Enum(
    DANGER_CLASSIFICATION,
    name="danger_classification",
    values_callable=lambda obj: [e.value for e in obj]
)

UserSubscriptionTypes = Enum(
    SUBSCRIBE_TYPES,
    name="subscription_types",
    values_callable=lambda obj: [e.value for e in obj]
)
