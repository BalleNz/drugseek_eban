from fastapi.params import Depends

from drug_search.core.dependencies.assistant_service_dep import get_assistant_service
from drug_search.core.services.assistant_service import AssistantService
from drug_search.core.services.pubmed_service import PubmedService


async def get_pubmed_service(assistant_service: AssistantService = Depends(get_assistant_service)):
    """Return singletone object"""
    return PubmedService(assistant_service=assistant_service)
