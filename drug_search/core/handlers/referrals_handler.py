import logging
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends

from drug_search.core.dependencies.bot.cache_service_dep import get_cache_service
from drug_search.core.dependencies.user_service_dep import get_user_service_with_assistant
from drug_search.core.lexicon import FREE_TOKENS_AMOUNT
from drug_search.core.schemas import UserSchema, NewReferralsRequest
from drug_search.core.services.cache_logic.cache_service import CacheService
from drug_search.core.services.models_service.user_service import UserService
from drug_search.core.utils.auth import get_auth_user

logger = logging.getLogger(__name__)
referrals_router = APIRouter(prefix="/referrals")


@referrals_router.put(path="/new_referral")
async def new_referral(
        user_service: Annotated[UserService, Depends(get_user_service_with_assistant)],
        cache_service: Annotated[CacheService, Depends(get_cache_service)],
        request: NewReferralsRequest
):
    """Новый реферал перешел по ссылке"""

    referrer_telegram_id = request.referrer_telegram_id
    referral_telegram_id = request.referral_telegram_id

    referrer_user: UserSchema = await user_service.repo.get_user_from_telegram_id(referrer_telegram_id)
    referral_user: UserSchema = await user_service.repo.get_user_from_telegram_id(referral_telegram_id)

    if datetime.now() - referral_user.created_at < timedelta(minutes=1) and not referral_user.referred_by_telegram_id:
        await user_service.repo.create_referral(
            referrer_user=referrer_user,
            referral_user=referral_user
        )
        logger.info(f"Новый реферал для юзера {referrer_user.username}!")

        await cache_service.redis_service.invalidate_user_data(referrer_telegram_id)


@referrals_router.put(path="/free_tokens")
async def get_free_tokens(
        user: Annotated[UserSchema, Depends(get_auth_user)],
        user_service: Annotated[UserService, Depends(get_user_service_with_assistant)],
        cache_service: Annotated[CacheService, Depends(get_cache_service)],
):
    """Разовое получение токенов"""
    if user.got_free_tokens:
        return

    await user_service.repo.update(
        user.id,
        got_free_tokens=True,
        additional_tokens=user.additional_tokens+FREE_TOKENS_AMOUNT
    )
    logger.info(f"Юзер {user.telegram_id} получил доп токены")

    await cache_service.redis_service.invalidate_user_data(user.telegram_id)
