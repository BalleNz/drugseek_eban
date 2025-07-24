import pytest

from sqlalchemy import text
from core.database.models.drug import Drug, DrugSynonym
from core.database.repository.drug import DrugRepository
from services.drug import DrugService


@pytest.mark.asyncio
def test_search_drug(
        user: ...,
):
    ...
