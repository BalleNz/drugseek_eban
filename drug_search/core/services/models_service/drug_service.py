import asyncio
import logging
import uuid
from typing import Optional

from drug_search.core.schemas import DrugSchema, DrugResearchesAssistantResponse
from drug_search.core.services.assistant_service import AssistantService
from drug_search.core.services.pubmed_service import PubmedService
from drug_search.infrastructure.database.repository.drug_repo import DrugRepository

logger = logging.getLogger(__name__)


class DrugService:
    def __init__(
            self,
            repo: DrugRepository,
            assistant_service: AssistantService = None,
            pubmed_service: PubmedService = None,
    ):
        self.repo = repo
        self.assistant = assistant_service
        self.pubmed_service = pubmed_service

    async def find_drug_by_query(self, user_query: str) -> Optional[DrugSchema]:
        """
        Поиск по триграммам в таблице синонимов.
        :returns: drug | None
        """
        drug: DrugSchema = await self.repo.find_drug_by_query(user_query=user_query)
        return drug

    async def update_or_create_drug(
            self,
            drug_name: str,
            drug_id: uuid.UUID | None = None
    ) -> DrugSchema:
        """
        Обновляет или создает препарат, кроме исследований.

        Использует ассистента и (PubMed)
        :param drug_name:
        :param drug_id: при обновлении
        """
        try:
            # параллельное выполнение клиента ассистента
            drug_creation = self.assistant.drug_creation

            (
                assistant_response_briefly,
                assistant_response_dosages,
                assistant_response_analogs,
                assistant_response_metabolism,
                assistant_response_pathways,
                assistant_response_combinations,
            ) = await asyncio.gather(
                drug_creation.get_drug_briefly_info(drug_name=drug_name),
                drug_creation.get_drug_dosages(drug_name=drug_name),
                drug_creation.get_analogs(drug_name=drug_name),
                drug_creation.get_metabolism(drug_name=drug_name),
                drug_creation.get_pathways(drug_name=drug_name),
                drug_creation.get_combinations(drug_name=drug_name),
            )

            drug = await self.repo.DrugCreation.update_or_create_drug(
                briefly_info=assistant_response_briefly,
                dosages=assistant_response_dosages,
                analogs=assistant_response_analogs,
                metabolism=assistant_response_metabolism,
                pathways=assistant_response_pathways,
                combinations=assistant_response_combinations,
                drug_id=drug_id
            )

            # [ ФОНОВОЕ ОБНОВЛЕНИЕ ТАБЛИЦЫ ИССЛЕДОВАНИЙ ]
            if self.pubmed_service:
                asyncio.create_task(
                    self._update_drug_researches_background(drug.id, drug_name)
                )

            return drug

        except Exception as ex:
            logger.error(f"Ошибка при обновлении препарата.")
            raise ex

    async def _update_drug_researches_background(self, drug_id: uuid.UUID, drug_name: str) -> None:
        """Обновляет таблицу с исследованиями препарата.

        Использует: Pubmed Service
        """
        try:
            await self.repo.DrugCreation._delete_researches(drug_id)

            researches = await self.pubmed_service.get_researches_clearly(drug_name)
            await self.repo.DrugCreation.update_researches(drug_id=drug_id, researches=researches)
            logger.info(f"Исследования для препарата {drug_name} успешно обновлены")
        except Exception as ex:
            logger.error(f"Ошибка при фоновом обновлении исследований для {drug_name}: {ex}")
