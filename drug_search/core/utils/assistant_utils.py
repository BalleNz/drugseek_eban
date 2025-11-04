import json

from drug_search.core.schemas.assistant_schemas.assistant_requests import ClearResearchesRequest


def serialize_researches_request(request: ClearResearchesRequest) -> str:
    """Превращение Pydantic схемы исследований в строку"""
    json_query = {
        "drug_name": request.drug_name,
        "researches": [
            {
                **research.model_dump(exclude_none=True),
                "publication_date": research.publication_date.isoformat()
            }
            for research in request.researches
        ]
    }
    return json.dumps(json_query, indent=4, ensure_ascii=False)
