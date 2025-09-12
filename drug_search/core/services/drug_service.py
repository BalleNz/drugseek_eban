import asyncio
import logging
import uuid
from typing import Optional

from fastapi import Depends
from pydantic import ValidationError

from drug_search.core.schemas import (AssistantResponseDrugResearch, DrugSchema,
                                      PubmedResearchSchema, ClearResearchesRequest)
from drug_search.core.services.assistant_service import Assistant
from drug_search.core.utils.pubmed_parser import get_pubmed_parser, PubmedParser
from drug_search.infrastructure.database.repository.drug_repo import DrugRepository, get_drug_repository

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

    async def update_drug(
            self,
            drug_in_process: DrugSchema,
            assistant_service: Assistant
    ) -> DrugSchema:
        """
        Обновляет все поля препарата, кроме исследований.

        :param drug_in_process: схема препарата в процессе создания.
        :param assistant_service: сервис ассистента.
        """
        try:
            # параллельное выполнение клиента ассистента
            assistant_response_dosages, assistant_response_pathways, assistant_response_combinations  = await asyncio.gather(
                assistant_service.get_dosage(drug_name=drug_in_process.name),
                assistant_service.get_pathways(drug_name=drug_in_process.name),
                assistant_service.get_synergists(drug_name=drug_in_process.name)
            )

            drug_after_dosages: DrugSchema = await self.repo.update_dosages(
                drug=drug_in_process,
                assistant_response=assistant_response_dosages
            )
            drug_after_pathways: DrugSchema = await self.repo.update_pathways(
                drug=drug_after_dosages,
                assistant_response=assistant_response_pathways
            )
            drug: DrugSchema = await self.repo.update_combinations(
                drug=drug_after_pathways,
                assistant_response=assistant_response_combinations
            )

            await self.repo.save_from_schema(drug)

            # Отдельный метод для исследований, тк исследования будут обновляться с выходом новых версий модели
            # Deepseek. Изначально список исследований не будет доступен и будет за доп плату в виде N токенов.

        except Exception as ex:
            logger.error(f"Ошибка при обновлении препарата.")
            raise ex

        return await self.repo.get(drug.id)

    async def new_drug(self, drug_name: str, assistant_service: Assistant) -> DrugSchema:
        """
        Создает новый препарат со всеми смежными таблицами после валидации нейронкой.

        :param drug_name: Действующее вещество на английском.
        :param assistant_service: Сервис ассистента
        """
        try:
            drug: DrugSchema = DrugSchema(
                id=uuid.uuid4(),
                name=drug_name
            )
            drug: DrugSchema = await self.update_drug(drug_in_process=drug, assistant_service=assistant_service)
            return drug
        except Exception as ex:
            logger.error(f"Ошибка при создании препарата: {ex}")
            raise ex

    async def update_drug_researches(self, drug_id: uuid.UUID, assistant_service: Assistant) -> None:
        """
        Обновляет таблицу с исследованиями препарата. Можно отдельно обновлять без обновления всего препарата целиком.
        """
        drug: DrugSchema = await self.repo.get(drug_id)
        drug_name: str = drug.name
        async with assistant_service as assistant_service:  # TODO

            try:
                pubmed_parser: PubmedParser = get_pubmed_parser()
                pubmed_researches: list[Optional[PubmedResearchSchema]] = pubmed_parser.get_researches(
                    drug_name=drug_name,
                    assistant_service=assistant_service
                )
            except Exception as ex:
                logger.error(f"Ошибка во время парсинга исследований для {drug_name}: {ex}")
                raise ex

            try:
                pubmed_researches_with_drug_name = ClearResearchesRequest(
                    researches=pubmed_researches,
                    drug_name=drug_name
                )
            except ValidationError as ex:
                logger.error(f"Ошибка при валидации Pydantic схемы ClearResearchesRequest: {ex}")
                raise ex

            try:
                drug_researches: list[AssistantResponseDrugResearch] = assistant_service.get_clear_researches(
                    pubmed_researches_with_drug_name=pubmed_researches_with_drug_name
                ).researches
            except Exception as ex:
                logger.error(f"Ошибка при получении исследований ассистентом: {ex}")
                raise ex

            await self.repo.update_researches(drug_id=drug_id, researches=drug_researches)


def get_drug_service(repo: DrugRepository = Depends(get_drug_repository)):
    return DrugService(repo=repo)
