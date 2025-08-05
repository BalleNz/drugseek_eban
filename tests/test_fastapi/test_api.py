import pytest

from sqlalchemy import text
from core.database.models.drug import Drug, DrugSynonym
from core.database.repository.drug_repo import DrugRepository
from services.drug_service import DrugService


@pytest.mark.asyncio
def test_search_drug(
        user: ...,
):
    ...
