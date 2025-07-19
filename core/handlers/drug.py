from typing import Union, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Path

from database.models.user import User
from schemas.drug_schemas import DrugSchema
from schemas.response import DrugResponse
from services.drug import DrugService, get_drug_service
from services.user import UserService, get_user_service

drug_router = APIRouter(prefix="/drugs", tags=["Drugs"])

# для бота: если ручка get_drug вернет None, то нужно дернуть за
# user_router.reduce_tokens, drug_router.new_drug, user_router.allow_drug


@drug_router.post(path="/", response_model=DrugSchema)
async def new_drug(
        drug: DrugSchema,
        user: User = ...,
        drug_service: DrugService = Depends(get_drug_service),
) -> Union[DrugSchema, HTTPException]:
    try:
        return await drug_service.create_drug(drug_name=drug.name)
    except Exception as ex:
        return HTTPException(401, detail=f"{ex}")


@drug_router.get("/{user_query}")
async def search_request(
        user_query: Path(),
        user: User = ...,  # TODO: auth with O2auth schema via telegram
        drug_service: DrugService = Depends(get_drug_service)
):

    drug: DrugSchema = await drug_service.find_drug_by_query(
        user=user,
        user_query=user_query
    )

    if not drug:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Drug not found")

    is_allowed = drug.id in user.allowed_drugs

    return DrugResponse(
        drug=drug,
        is_allowed=is_allowed,
    )
