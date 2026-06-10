from fastapi.params import Depends

from drug_search.core.dependencies.drug_service_dep import get_drug_service
from drug_search.core.services.models_service.drug_service import DrugService
from drug_search.core.services.models_service.payment_service import PaymentService
from drug_search.infrastructure.database.repository.payment_repo import PaymentRepository, get_payment_repo


async def get_payment_service(
        repo: PaymentRepository = Depends(get_payment_repo),
        drug_service: DrugService = Depends(get_drug_service),
) -> PaymentService:
    return PaymentService(repo, drug_service)