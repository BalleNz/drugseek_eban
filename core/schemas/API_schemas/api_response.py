from pydantic import BaseModel

from schemas.API_schemas.drug_schemas import DrugSchema

"""
drug_router
"""


class DrugResponse(BaseModel):
    drug: DrugSchema
    is_allowed: bool


"""
user_router
"""
