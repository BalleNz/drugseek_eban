from sqlalchemy import Enum

from drug_search.core.lexicon.enums import DANGER_CLASSIFICATION

DangerClassificationEnum = Enum(
    DANGER_CLASSIFICATION,
    name="danger_classification",
    values_callable=lambda obj: [e.value for e in obj]
)
