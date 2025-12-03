from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from drug_search.core.dependencies.task_service_dep import get_task_service
from drug_search.core.lexicon import ADMINS_TG_ID, MailingStatuses
from drug_search.core.schemas import MailingRequest, UserSchema
from drug_search.core.services.tasks_logic.task_service import TaskService
from drug_search.core.utils.auth import get_auth_user

admin_router = APIRouter(prefix="/admin")


@admin_router.post(path="/mailing")
async def mailing(
        request: MailingRequest,
        task_service: Annotated[TaskService, Depends(get_task_service)],
        user: Annotated[UserSchema, Depends(get_auth_user)]
):
    if user.telegram_id in ADMINS_TG_ID:
        await task_service.enqueue_mailing(
            message=request.message,
        )
        return {
            "status": MailingStatuses.SUCCESS
        }
    else:
        return {
            "status": MailingStatuses.ONLY_FOR_ADMINS
        }
