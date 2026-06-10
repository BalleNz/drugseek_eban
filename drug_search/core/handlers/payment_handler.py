import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from drug_search.core.dependencies.bot.cache_service_dep import get_cache_service
from drug_search.core.dependencies.payment_service_dep import get_payment_service
from drug_search.core.dependencies.task_service_dep import get_task_service
from drug_search.core.dependencies.telegram_service_dep import get_telegram_service
from drug_search.core.schemas import PaymentRequest, PaymentSchema
from drug_search.core.services.cache_logic.cache_service import CacheService
from drug_search.core.services.models_service.payment_service import PaymentService
from drug_search.core.services.tasks_logic.task_service import TaskService
from drug_search.core.services.telegram_service import TelegramService
logger = logging.getLogger(__name__)
payment_router = APIRouter(prefix="/payment")


@payment_router.post(
    "/process",
    description="Обработка успешного платежа",
    include_in_schema=False,
)
async def payment_process(
        payment: PaymentRequest,
        payment_service: Annotated[PaymentService, Depends(get_payment_service)],
        cache_service: Annotated[CacheService, Depends(get_cache_service)],
        task_service: Annotated[TaskService, Depends(get_task_service)],
        telegram_service: Annotated[TelegramService, Depends(get_telegram_service)]
):
    """запись в бд платежа + бизнес логика выдачи покупки"""
    payment_result: PaymentSchema = await payment_service.payment_process(
        payment,
        cache_service
    )

    await task_service.enqueue_yookassa_update_to_admins(
        username=payment.user_telegram_id,
        price=payment_result.price,
        payment_description=payment_result.payment_name
    )

    # [ оповещение юзеру ]
    message_text: str = ""
    match payment_result.package_key.split("_")[0]:
        case "sub":
            message_text = "Подписка успешно активирована!"
        case "tokens":
            message_text = "Токены успешно начислены!"
        case "pack":
            message_text = "Пак препаратов успешно активирован! Все препараты категории добавлены в вашу базу."
    await telegram_service.send_message(
        payment.user_telegram_id,
        message=message_text
    )
