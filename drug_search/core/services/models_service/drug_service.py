import asyncio
import logging
import uuid
from typing import Optional

from drug_search.core.schemas import DrugSchema
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

    async def update_drug(
            self,
            drug_in_process: None | DrugSchema = None,
            drug_id: uuid.UUID | None = None
    ) -> DrugSchema:
        """
        Обновляет все поля препарата, кроме исследований.

        Использует ассистента и (PubMed)
        :param drug_id: обновление по drug_id
        :param drug_in_process: схема препарата в процессе создания.
        """
        if not drug_in_process:
            drug_in_process = self.repo.get_with_all_relationships(drug_id)

        try:
            # параллельное выполнение клиента ассистента
            assistant_response_dosages, assistant_response_pathways, assistant_response_combinations = await asyncio.gather(
                self.assistant.get_drug_dosages(drug_name=drug_in_process.name),
                self.assistant.get_pathways(drug_name=drug_in_process.name),
                self.assistant.get_combinations(drug_name=drug_in_process.name)
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
            # TODO: сделать один метод который бы сохранял всю модель (тупо сложить методы и передавать все assistant responses)

            await self.repo.save_from_schema(drug)

            # Отдельный метод для исследований, тк исследования будут обновляться с выходом новых версий модели
            # Deepseek. Изначально список исследований не будет доступен и будет за доп плату в виде N токенов.

        except Exception as ex:
            logger.error(f"Ошибка при обновлении препарата.")
            raise ex

        return await self.repo.get(drug.id)

    async def new_drug(self, drug_name: str) -> DrugSchema:
        """
        Создает новый препарат со всеми смежными таблицами после валидации нейронкой.
        :param drug_name: Действующее вещество на английском.
        """
        try:
            drug: DrugSchema = DrugSchema(
                id=uuid.uuid4(),
                name=drug_name
            )
            drug: DrugSchema = await self.update_drug(drug_in_process=drug)
            return drug
        except Exception as ex:
            logger.error(f"Ошибка при создании препарата: {ex}")
            raise ex

    async def update_drug_researches(self, drug_id: uuid.UUID) -> None:
        """Обновляет таблицу с исследованиями препарата.

        Использует: Pubmed Service
        """
        drug: DrugSchema = await self.repo.get(drug_id)
        drug_name: str = drug.name

        researches = await self.pubmed_service.get_researches_clearly(drug_name)
        await self.repo.update_researches(drug_id=drug_id, researches=researches)
