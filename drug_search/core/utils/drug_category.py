from drug_search.core.lexicon import DRUG_CATEGORY, DANGER_CLASSIFICATION

STEROID_KEYWORDS: tuple[str, ...] = (
    "steroid",
    "anabolic",
    "androgen",
    "testosterone",
    "aas",
    "стероид",
    "андроген",
    "тестостерон",
    "анабол",
)


def steroid_classification_sql(alias: str = "classification") -> str:
    conditions = " OR ".join(
        f"LOWER(COALESCE({alias}, '')) LIKE '%{keyword}%'"
        for keyword in STEROID_KEYWORDS
    )
    return f"({conditions})"


def category_filter_sql(category: DRUG_CATEGORY | None) -> str:
    steroid_sql = steroid_classification_sql("d.classification")

    if category == DRUG_CATEGORY.PROHIBITED:
        return f"d.danger_classification = '{DANGER_CLASSIFICATION.DANGER.value}'"

    if category == DRUG_CATEGORY.STEROID:
        return steroid_sql

    if category == DRUG_CATEGORY.PHARMA:
        return (
            f"d.danger_classification = '{DANGER_CLASSIFICATION.SAFE.value}' "
            f"AND NOT {steroid_sql}"
        )

    complex_parts = [
        f"d.danger_classification = '{DANGER_CLASSIFICATION.DANGER.value}'",
        steroid_sql,
        (
            f"d.danger_classification = '{DANGER_CLASSIFICATION.SAFE.value}' "
            f"AND NOT {steroid_sql}"
        ),
    ]
    return f"({' OR '.join(complex_parts)})"
