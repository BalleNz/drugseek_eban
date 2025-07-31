import logging
import uuid
from typing import Optional

from fastapi import Depends

from assistant import assistant
from core.database.repository.drug_repo import DrugRepository
from database.repository.drug_repo import get_drug_repository
from schemas import AssistantResponseCombinations, AssistantResponseDrugPathways, AssistantDosageDescriptionResponse
from schemas.drug_schemas import DrugSchema
from utils.exceptions import AssistantResponseError

logger = logging.getLogger("bot.core.drug_service")


class DrugService:
    def __init__(self, repo: DrugRepository):
        self.repo = repo

    # TODO user identify
    async def find_drug_by_query(self, user: ..., user_query: str) -> Optional[DrugSchema]:
        """
        Возвращает препарат по запросу юзера.

        - поиск препаратов по имени в таблице синонимов на русском.
        :returns: drug | None
        """
        drug: DrugSchema = await self.repo.find_drug_by_query(user_query=user_query)
        return drug

    async def update_drug(self, drug_id: uuid.UUID, drug_name: str) -> None:
        """
        Обновляет все поля препарата.
        :param drug_id: ID препарата.
        :param drug_name: строго правильное ДВ препарата.
        """
        try:
            assistant_response_dosages: AssistantDosageDescriptionResponse = assistant.get_dosage(drug_name=drug_name)
            if not assistant_response_dosages.drug_name:
                logger.error("Ассистент не может найти оффициальное название.")
                raise AssistantResponseError(f"Couldn't get official drugName for {drug_name}.")
            await self.repo.update_dosages(drug_id=drug_id, assistant_response=assistant_response_dosages)

            assistant_response_pathways: AssistantResponseDrugPathways = assistant.get_pathways(drug_name=drug_name)
            if not assistant_response_pathways:
                logger.error("Ассистент не может найти пути активации.")
                raise AssistantResponseError(f"Couldn't get pathways for {drug_name}")
            await self.repo.update_pathways(drug_id=drug_id, assistant_response=assistant_response_pathways)

            assistant_response_combinations: AssistantResponseCombinations = assistant.get_combinations(
                drug_name=drug_name)
            if not assistant_response_combinations:
                logger.error("Ассистент не может найти комбинации.")
                raise AssistantResponseError(f"Couldn't get combinations for {drug_name}")
            await self.repo.update_combinations(drug_id=drug_id, assistant_response=assistant_response_combinations)

        except Exception as ex:
            logger.error(f"Ошибка при обновлении препарата.")
            raise ex

    async def new_drug(self, drug_name: str) -> DrugSchema:
        """
        Создает новый препарат со всеми смежными таблицами после валидации нейронкой.

        :param drug_name: Действующее вещество на английском.
        """
        try:
            drug: DrugSchema = await self.repo.create_drug(drug_name)
            await self.update_drug(drug_name=drug.name, drug_id=drug.id)
            return DrugSchema.model_validate(self.repo._convert_to_drug_schema(await self.repo.get(drug.id)))
        except Exception as ex:
            logger.error(f"Ошибка при создании препарата: {ex}")
            raise ex

    async def validate_user_query(self, user_query: str) -> Optional[str]:
        """
        ВАЛИДИРУЕТ ЗАПРОС ПОЛЬЗОВАТЕЛЯ НА РЕАЛЬНОСТЬ ПРЕПАРАТА.
        :param user_query: Запрос пользователя, предполгаемое название препарата
        :returns: Действующее вещество на английском | None
        """
        return assistant.get_user_query_validation(user_query)


def get_drug_service(repo: DrugRepository = Depends(get_drug_repository)):
    return DrugService(repo=repo)
