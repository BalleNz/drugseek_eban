import logging
from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from drug_search.core.dependencies.bot.cache_service_dep import get_cache_service
from drug_search.core.dependencies.task_service_dep import get_task_service
from drug_search.core.dependencies.user_service_dep import get_user_service, get_user_service_with_assistant
from drug_search.core.lexicon import SUBSCRIBE_TYPES, DANGER_CLASSIFICATION
from drug_search.core.schemas import (UserSchema, AddTokensRequest, BuyDrugRequest, BuyDrugResponse,
                                      BuyDrugStatuses, AllowedDrugsInfoSchema)
from drug_search.core.services.cache_logic.cache_service import CacheService
from drug_search.core.services.models_service.user_service import UserService
from drug_search.core.services.tasks_logic.task_service import TaskService
from drug_search.core.utils.auth import get_auth_user

user_router = APIRouter(prefix="/user")
logger = logging.getLogger(__name__)


@user_router.get(
    path="/",
    response_model=UserSchema,
    description="Получить описание юзера"
)
async def get_user(
        user: Annotated[UserSchema, Depends(get_auth_user)],
):
    return user


@user_router.get(
    path="/allowed",
    description="Получение всех разрешенных препаратов, а также общее количество препаратов в базе.",
    response_model=AllowedDrugsInfoSchema
)
async def get_drugs(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        user_service: Annotated[UserService, Depends(get_user_service)],
):
    return await user_service.get_allowed_drugs_info(user_id=user.id)


@user_router.post(path="/tokens/increment", description="Добавление токенов")
async def add_tokens(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        cache_service: Annotated[CacheService, Depends(get_cache_service)],
        request: AddTokensRequest
):
    await user_service.add_tokens(
        user.id,
        amount_search_tokens=request.amount_search_tokens,
        amount_question_tokens=request.amount_question_tokens
    )
    await cache_service.redis_service.invalidate_user_data(telegram_id=user.telegram_id)


@user_router.post(path="/tokens/reduce", description="Отнять токены")
async def reduce_tokens(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        user_service: Annotated[UserService, Depends(get_user_service)],
        cache_service: Annotated[CacheService, Depends(get_cache_service)],
        request: AddTokensRequest
):
    await user_service.reduce_tokens(
        user.id,
        amount_search_tokens=request.amount_search_tokens,
        amount_question_tokens=request.amount_question_tokens
    )
    await cache_service.redis_service.invalidate_user_data(telegram_id=user.telegram_id)


@user_router.post(path="/buy_drug")
async def buy_drug(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        user_service: Annotated[UserService, Depends(get_user_service_with_assistant)],
        task_service: Annotated[TaskService, Depends(get_task_service)],
        cache_service: Annotated[CacheService, Depends(get_cache_service)],
        request: BuyDrugRequest
):
    """Покупка препарата.
    Если не было в базе, то создается и добавляется.
    """
    if not user.allowed_search_requests:
        logger.info(f"У юзера нет токенов для покупки препарата, ID: {user.id}")
        return BuyDrugResponse(
            status=BuyDrugStatuses.NOT_ENOUGH_TOKENS
        )

    if user.subscription_type in SUBSCRIBE_TYPES.DEFAULT and request.danger_classification in DANGER_CLASSIFICATION.PREMIUM_NEED:
        logger.info(f"У юзера недостаточный уровень подписки, ID: {user.id}, drug_name: {request.drug_name}")
        return BuyDrugResponse(
            status=BuyDrugStatuses.NEED_PREMIUM
        )

    if request.danger_classification == DANGER_CLASSIFICATION.DANGER:
        logger.info(f"Юзер ищет запрещенный препарат.. {request.drug_name}")
        return BuyDrugResponse(
            status=BuyDrugStatuses.DANGER
        )

    await user_service.reduce_tokens(user.id, 1)

    if len(user.allowed_drugs) > 9:
        """Обновляем описание юзера"""
        await user_service.update_user_description(user_id=user.id)

    if request.drug_id:
        """Препарат уже есть в базе"""
        logger.info(f"Юзер {user.telegram_id} купил препарат {request.drug_name}")
        await user_service.allow_drug_to_user(user.id, request.drug_id)
        await cache_service.redis_service.invalidate_user_data(telegram_id=user.telegram_id)
        return BuyDrugResponse(
            status=BuyDrugStatuses.DRUG_ALLOWED,
            drug_name=request.drug_name
        )
    else:
        """Нужно его создать и разрешить"""
        logger.info(f"Юзер {user.telegram_id} купил препарат {request.drug_name}")
        job_response: dict = await task_service.enqueue_drug_creation(  # invalidation user data in task
            user_telegram_id=user.telegram_id,
            user_id=user.id,
            drug_name=request.drug_name
        )
        return BuyDrugResponse(
            status=BuyDrugStatuses.DRUG_CREATED,
            drug_name=request.drug_name,
            job_status=job_response['status']
        )
