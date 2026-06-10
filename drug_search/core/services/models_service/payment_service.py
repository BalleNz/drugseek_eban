import logging

from drug_search.core.lexicon import SubscriptionPackage, TokensPackage, DrugPackPackage
from drug_search.core.schemas.payment_schema import PaymentRequest, PaymentSchema
from drug_search.core.services.cache_logic.cache_service import CacheService
from drug_search.core.services.models_service.drug_service import DrugService
from drug_search.infrastructure.database.repository.payment_repo import PaymentRepository

logger = logging.getLogger(__name__)


class PaymentService:
    def __init__(
            self,
            repo: PaymentRepository,
            drug_service: DrugService | None = None,
    ):
        self.repo = repo
        self.drug_service = drug_service

    async def payment_process(
            self,
            payment_request: PaymentRequest,
            cache_service: CacheService
    ) -> PaymentSchema | None:
        """Обработка успешного платежа"""

        product_key: str = payment_request.product_key
        product_prefix = product_key.split("_")[0]

        payment_package: SubscriptionPackage | TokensPackage | DrugPackPackage | None = None
        price: int = 0
        match product_prefix:
            case "sub":
                payment_package: SubscriptionPackage = SubscriptionPackage.get_by_key(product_key)
                price = payment_package.price(
                    subscription_days=payment_request.sub_days
                )
            case "tokens":
                payment_package: TokensPackage = TokensPackage.get_by_key(product_key)
                price = payment_package.price
            case "pack":
                payment_package: DrugPackPackage = DrugPackPackage.get_by_key(product_key)
                price = payment_package.price

        package_key = payment_package.key
        payment_name = payment_package.name

        payment_response: PaymentSchema | None = None
        match product_prefix:
            case "sub":
                payment_response: PaymentSchema = await self.repo.give_subscription(
                    sub_type=payment_package.subscription_type,
                    sub_duration_days=payment_package.duration,
                    user_telegram_id=payment_request.user_telegram_id,
                    package_key=package_key,
                    payment_name=payment_name,
                    price=price
                )
            case "tokens":
                payment_response: PaymentSchema = await self.repo.give_tokens(
                    tokens_count=payment_package.quantity,
                    user_telegram_id=payment_request.user_telegram_id,
                    package_key=package_key,
                    payment_name=payment_name,
                    price=price
                )
            case "pack":
                drug_ids = await self.drug_service.repo.get_drug_ids_by_category(
                    payment_package.category
                )
                payment_response: PaymentSchema = await self.repo.give_drug_pack(
                    category=payment_package.category,
                    user_telegram_id=payment_request.user_telegram_id,
                    package_key=package_key,
                    payment_name=payment_name,
                    price=price,
                    drug_ids=drug_ids,
                )
                logger.info(
                    f"Выдан пак {payment_name}: {len(drug_ids)} препаратов "
                    f"пользователю {payment_request.user_telegram_id}"
                )

        await cache_service.redis_service.invalidate_user_data(
            payment_request.user_telegram_id
        )

        return payment_response
