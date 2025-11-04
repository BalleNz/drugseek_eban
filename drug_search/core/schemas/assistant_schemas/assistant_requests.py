from pydantic import BaseModel, Field

from drug_search.core.schemas import PubmedResearchSchema


class ClearResearchesRequest(BaseModel):
    drug_name: str = Field(...)
    researches: list[PubmedResearchSchema] = Field(...)
