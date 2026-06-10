from typing import Annotated

from fastapi import Depends

from drug_search.core.dependencies.drug_service_dep import get_drug_service
from drug_search.core.dependencies.redis_service_dep import get_redis_service
from drug_search.core.services.cache_logic.redis_service import RedisService
from drug_search.core.services.models_service.drug_service import DrugService
from drug_search.core.services.models_service.quiz_service import QuizService
from drug_search.infrastructure.database.repository.drug_repo import DrugRepository


async def get_quiz_service(
        drug_service: Annotated[DrugService, Depends(get_drug_service)],
        redis_service: Annotated[RedisService, Depends(get_redis_service)],
) -> QuizService:
    drug_repo: DrugRepository = drug_service.repo
    return QuizService(drug_repo=drug_repo, redis_service=redis_service)
