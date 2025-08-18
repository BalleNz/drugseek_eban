from pydantic import BaseModel

from drug_search.core.schemas.drug_schemas import DrugSchema


class DrugExistingResponse(BaseModel):
    drug_exist: bool
    drug: DrugSchema
    is_allowed: bool
