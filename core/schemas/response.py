from pydantic import BaseModel, Field

from schemas.drug_schemas import DrugSchema

"""
drug_router
"""


class DrugResponse(BaseModel):
    drug: DrugSchema
    is_allowed: bool


"""
user_router
"""
