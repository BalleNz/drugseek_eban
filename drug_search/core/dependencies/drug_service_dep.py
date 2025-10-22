from fastapi import Depends

from drug_search.core.dependencies.assistant_service_dep import get_assistant_service
from drug_search.core.dependencies.pubmed_service_dep import get_pubmed_service

from drug_search.core.services.assistant_service import AssistantService
from drug_search.core.services.models_service.drug_service import DrugService
from drug_search.core.services.pubmed_service import PubmedService
from drug_search.infrastructure.database.repository.drug_repo import DrugRepository, get_drug_repository


async def get_drug_service(
        repo: DrugRepository = Depends(get_drug_repository)
) -> DrugService:
    """Сервис препаратов без зависимостей"""
    return DrugService(repo=repo)


async def get_drug_service_with_deps(
        repo: DrugRepository = Depends(get_drug_repository),
        assistant: AssistantService = Depends(get_assistant_service),
        pubmed: PubmedService = Depends(get_pubmed_service)
) -> DrugService:
    """Сервис препаратов со всеми зависимостями (синглтоны)"""
    return DrugService(repo=repo, assistant_service=assistant, pubmed_service=pubmed)
