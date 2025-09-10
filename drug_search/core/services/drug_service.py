import asyncio
import logging
import uuid
from typing import Optional

from fastapi import Depends
from pydantic import ValidationError

from drug_search.core.schemas import AssistantResponseCombinations, AssistantResponseDrugPathways, \
    AssistantDosageDescriptionResponse, AssistantResponseDrugResearch
from drug_search.core.schemas.drug_schemas import DrugSchema
from drug_search.core.schemas.pubmed_schema import PubmedResearchSchema, ClearResearchesRequest
from drug_search.core.utils.exceptions import AssistantResponseError
from drug_search.core.utils.pubmed_parser import get_pubmed_parser, PubmedParser
from drug_search.infrastructure.database.repository.drug_repo import DrugRepository, get_drug_repository
from drug_search.core.services.assistant_service import Assistant

logger = logging.getLogger("bot.core.drug_service")


class DrugService:
    def __init__(self, repo: DrugRepository):
        self.repo = repo

    async def find_drug_by_query(self, user_query: str) -> Optional[DrugSchema]:
        """
        Поиск по триграммам в таблице синонимов.
        :returns: drug | None
        """
        drug: DrugSchema = await self.repo.find_drug_by_query(user_query=user_query)
        return drug

    async def update_dosages(self, drug_id: uuid.UUID, drug_name: str, assistant_service: Assistant):
        """Обновление дозировок препарата"""
        try:
            assistant_response_dosages: AssistantDosageDescriptionResponse = assistant_service.get_dosage(drug_name=drug_name)
            if not assistant_response_dosages:
                logger.error("Ассистент не может найти дозировки.")
                raise AssistantResponseError(f"Couldn't get dosages for {drug_name}.")

            await self.repo.update_dosages(drug_id=drug_id, assistant_response=assistant_response_dosages)
        except Exception as ex:
            logger.error(f"Exceptions while updating drug: {ex}")

    async def update_pathways(self, drug_id: uuid.UUID, drug_name: str, assistant_service: Assistant):
        """Обновление путей активации препарата"""
        try:
            assistant_response_pathways: AssistantResponseDrugPathways = assistant_service.get_pathways(drug_name=drug_name)
            if not assistant_response_pathways:
                logger.error("Ассистент не может найти пути активации.")
                raise AssistantResponseError(f"Couldn't get pathways for {drug_name}")
            await self.repo.update_pathways(drug_id=drug_id, assistant_response=assistant_response_pathways)
        except Exception as ex:
            logger.error(f"Exceptions while updating drug: {ex}")

    async def update_combinations(self, drug_id: uuid.UUID, drug_name: str, assistant_service: Assistant):
        """Обновление комбинаций препарата"""
        try:
            assistant_response_combinations: AssistantResponseCombinations = assistant_service.get_synergists(
                drug_name=drug_name)
            if not assistant_response_combinations:
                logger.error("Ассистент не может найти комбинации.")
                raise AssistantResponseError(f"Couldn't get combinations for {drug_name}")
            await self.repo.update_combinations(drug_id=drug_id, assistant_response=assistant_response_combinations)
        except Exception as ex:
            logger.error(f"Exceptions while updating drug: {ex}")

    async def update_drug(self, drug_id: uuid.UUID, drug_name: str, assistant_service: Assistant) -> DrugSchema:
        """
        Обновляет все поля препарата, кроме исследований.
        :param drug_id: ID препарата.
        :param drug_name: ДВ препарата на англ.
        """
        try:
            # параллельное выполнение клиента ассистента
            await asyncio.gather(
                self.update_dosages(drug_id=drug_id, drug_name=drug_name, assistant_service=assistant_service),
                self.update_pathways(drug_id=drug_id, drug_name=drug_name, assistant_service=assistant_service),
                self.update_combinations(drug_id=drug_id, drug_name=drug_name, assistant_service=assistant_service)
            )

            # Отдельный метод для исследований, тк исследования будут обновляться с выходом новых версий модели Deepseek.
            # Изначально список исследований не будет доступен и будет за доп плату в виде N токенов.

        except Exception as ex:
            logger.error(f"Ошибка при обновлении препарата.")
            raise ex

        return await self.repo.get_drug(drug_id)

    async def new_drug(self, drug_name: str, assistant_service: Assistant) -> DrugSchema:
        """
        Создает новый препарат со всеми смежными таблицами после валидации нейронкой.

        :param drug_name: Действующее вещество на английском.
        """
        try:
            drug: DrugSchema = await self.repo.create_drug(drug_name)
            await self.update_drug(drug_id=drug.id, drug_name=drug.name, assistant_service=assistant_service)

            drug_model = await self.repo.get_drug(drug.id)
            return DrugSchema.model_validate(drug_model.get_schema())

        except Exception as ex:
            logger.error(f"Ошибка при создании препарата: {ex}")
            raise ex

    async def update_drug_researchs(self, drug_id: uuid.UUID, assistant_service: Assistant) -> None:
        """
        Обновляет таблицу с исследованиями препарата. Можно отдельно обновлять без обновления всего препарата целиком.
        """
        drug: DrugSchema = await self.repo.get_drug(drug_id)
        drug_name: str = drug.name

        try:
            pubmed_parser: PubmedParser = get_pubmed_parser()
            pubmed_researchs: list[Optional[PubmedResearchSchema]] = pubmed_parser.get_researchs(drug_name=drug_name)
        except Exception as ex:
            logger.error(f"Ошибка во время парсинга исследований для {drug_name}: {ex}")
            raise ex

        try:
            pubmed_researches_with_drug_name = ClearResearchesRequest(
                researchs=pubmed_researchs,
                drug_name=drug_name
            )
        except ValidationError as ex:
            logger.error(f"Ошибка при валидации Pydantic схемы ClearResearchesRequest: {ex}")
            raise ex

        try:
            drug_researches: list[AssistantResponseDrugResearch] = assistant_service.get_clear_researchs(
                pubmed_researchs_with_drug_name=pubmed_researches_with_drug_name
            ).researchs
        except Exception as ex:
            logger.error(f"Ошибка при получении исследований ассистентом: {ex}")
            raise ex

        await self.repo.update_researchs(drug_id=drug_id, researchs=drug_researches)


def get_drug_service(repo: DrugRepository = Depends(get_drug_repository)):
    return DrugService(repo=repo)
