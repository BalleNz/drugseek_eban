import asyncio
import logging
import uuid
from datetime import datetime
from typing import Optional, Union, AsyncGenerator

from fastapi import Depends
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from drug_search.core.schemas import (
    DrugCombinationsAssistantResponse, DrugSchema, DrugBrieflyAssistantResponse,
    DrugPathwaysAssistantResponse, DrugDosagesAssistantResponse,
    DrugAnalogsAssistantResponse, DrugMetabolismAssistantResponse,
    DrugResearchesAssistantResponse
)
from drug_search.infrastructure.database.engine import get_async_session
from drug_search.infrastructure.database.models.drug import (Drug, DrugSynonym, DrugCombination, DrugPathway,
                                                             DrugAnalog, DrugDosage, DrugResearch)
from drug_search.infrastructure.database.repository.base_repo import BaseRepository

logger = logging.getLogger(__name__)


class DrugRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Drug, session=session)
        self.DrugCreation = self.DrugCreation(session)

    async def find_drug_without_trigrams(
            self,
            drug_name_query: str
    ) -> DrugSchema | None:
        stmt = (
            select(Drug)
            .where(
                func.lower(Drug.name) == func.lower(drug_name_query)
            )
            .options(
                selectinload(Drug.analogs),
                selectinload(Drug.dosages),
                selectinload(Drug.pathways),
                selectinload(Drug.synonyms),
                selectinload(Drug.combinations),
                selectinload(Drug.prices),
                selectinload(Drug.researches)
            )
        )

        result = await self.session.execute(stmt)
        drug: Drug = result.scalar_one_or_none()

        if not drug:
            return None

        return drug.get_schema()

    async def find_drug_by_query(
            self,
            user_query: str
    ) -> Optional[DrugSchema]:
        """
        Поиск препарата по триграммному сходству с синонимами (один запрос).
        Возвращает DrugSchema с максимальной схожестью или None.

        :param user_query: Запрос пользователя.
        """
        stmt = (
            select(Drug)
            .join(Drug.synonyms)
            .where(
                func.similarity(
                    func.lower(DrugSynonym.synonym),
                    func.lower(user_query)
                ) > 0.43
            )
            .order_by(
                func.similarity(
                    func.lower(DrugSynonym.synonym),
                    func.lower(user_query)
                ).desc()
            )
            .limit(1)
            .options(
                selectinload(Drug.analogs),
                selectinload(Drug.dosages),
                selectinload(Drug.pathways),
                selectinload(Drug.synonyms),
                selectinload(Drug.combinations),
                selectinload(Drug.prices),
                selectinload(Drug.researches)
            )
        )

        result = await self.session.execute(stmt)
        drug: Drug = result.scalar_one_or_none()

        if not drug:
            return None

        return drug.get_schema()

    async def get_with_all_relationships(
            self,
            drug_id: uuid.UUID,
            need_model: bool = False
    ) -> Union[Drug, DrugSchema, None]:
        """
        Возращает модель или схему препарата в зависимости от флага need_model.

        :param drug_id: ID препарата в БД.
        :param need_model: Флаг, если активен — функция возвращает модель, иначе — API_schemas схему.
        """

        stmt = (
            select(Drug).where(
                Drug.id == drug_id
            )
            .options(
                selectinload(Drug.analogs),
                selectinload(Drug.dosages),
                selectinload(Drug.pathways),
                selectinload(Drug.synonyms),
                selectinload(Drug.combinations),
                selectinload(Drug.prices),
                selectinload(Drug.researches)
            )
        )

        result = await self.session.execute(stmt)
        drug: Drug = result.scalars().one_or_none()

        if not drug:
            return None

        # Если нужна модель
        if need_model:
            return drug

        return drug.get_schema()

    class DrugCreation:
        def __init__(self, session: AsyncSession):
            self.session = session

        async def update_or_create_drug(
                self,
                briefly_info: DrugBrieflyAssistantResponse,
                dosages: DrugDosagesAssistantResponse,
                analogs: DrugAnalogsAssistantResponse,
                metabolism: DrugMetabolismAssistantResponse,
                pathways: DrugPathwaysAssistantResponse,
                combinations: DrugCombinationsAssistantResponse,
                drug_id: uuid.UUID | None = None
        ) -> DrugSchema:
            """
            Создает или обновляет препарат в базе данных на основе данных от ассистента.
            Выполняет обновления параллельно для повышения производительности.

            :param briefly_info:
            :param dosages:
            :param analogs:
            :param metabolism:
            :param pathways:
            :param combinations:
            :param drug_id: Существующий препарат для обновления (если None - создается новый)
            :return: Обновленная или созданная модель Drug
            """
            try:
                need_to_clean = drug_id is not None

                if drug_id:
                    drug: Drug | None = await self.session.get(Drug, drug_id)
                    if not drug:
                        logger.exception(f"При обновлении препарата {drug_id} он не был найден в базе.")
                        raise

                    drug.updated_at = datetime.now()
                else:
                    drug = Drug(
                        id=uuid.uuid4(),
                        name=briefly_info.drug_name,
                        created_at=datetime.now()
                    )
                    self.session.add(drug)

                results = await asyncio.gather(
                    self.update_briefly_info(drug, briefly_info, need_to_clean),
                    self.update_dosages(drug, dosages, need_to_clean),
                    self.update_analogs(drug, analogs, need_to_clean),
                    self.update_metabolism(drug, metabolism),
                    self.update_pathways(drug, pathways, need_to_clean),
                    self.update_combinations(drug, combinations, need_to_clean),
                    return_exceptions=True
                )

                # [ check exceptions ]
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Error in parallel update {i}: {result}")
                        raise result

                await self.session.commit()
                await self.session.refresh(drug)

                logger.info(f"Successfully {'updated' if drug_id else 'created'} drug: {drug.name}")
                return drug.get_schema()

            except Exception as ex:
                await self.session.rollback()
                logger.exception(f"Failed to update drug: {str(ex)}")
                raise

        async def update_briefly_info(
                self, drug: Drug, assistant_response: DrugBrieflyAssistantResponse,
                need_to_clean: bool = False
        ) -> None:
            try:
                if need_to_clean:
                    await self.session.execute(delete(DrugSynonym).where(DrugSynonym.drug_id == drug.id))

                drug.name = assistant_response.drug_name
                drug.name_ru = assistant_response.drug_name_ru
                drug.latin_name = assistant_response.latin_name
                drug.description = assistant_response.description
                drug.classification = assistant_response.classification
                drug.fact = assistant_response.fact
                drug.danger_classification = assistant_response.danger_classification

                drug.synonyms = [
                    DrugSynonym(
                        drug_id=drug.id,
                        synonym=synonym
                    )
                    for synonym in assistant_response.synonyms
                ]

                drug.updated_at = datetime.now()

            except Exception as ex:
                logger.exception(f"Failed to update drug for {assistant_response.name}: {str(ex)}")
                raise

        async def update_dosages(
                self, drug: Drug, assistant_response: DrugDosagesAssistantResponse,
                need_to_clean: bool = False
        ) -> None:
            try:
                if need_to_clean:
                    await self.session.execute(delete(DrugDosage).where(DrugDosage.drug_id == drug.id))

                drug.dosages = [
                    DrugDosage(
                        route=dosage_response.route,
                        method=dosage_response.method,
                        per_time=dosage_response.per_time,
                        max_day=dosage_response.max_day,
                        per_time_weight_based=dosage_response.per_time_weight_based,
                        max_day_weight_based=dosage_response.max_day_weight_based,
                        onset=dosage_response.onset,
                        half_life=dosage_response.half_life,
                        duration=dosage_response.duration,
                        notes=dosage_response.notes,
                    ) for dosage_response in assistant_response.dosages
                ]
                drug.dosages_fun_facts = assistant_response.dosages_fun_facts
                drug.dosage_sources = assistant_response.dosage_sources

            except Exception as ex:
                logger.exception(f"Failed to update drug for {assistant_response.name}: {str(ex)}")
                raise

        async def update_analogs(
                self, drug: Drug, assistant_response: DrugAnalogsAssistantResponse,
                need_to_clean: bool = False
        ) -> None:
            try:
                if need_to_clean:
                    await self.session.execute(delete(DrugAnalog).where(DrugAnalog.drug_id == drug.id))

                drug.analogs = [
                    DrugAnalog(
                        analog_name=analog_response.analog_name,
                        percent=analog_response.percent,
                        difference=analog_response.difference,
                    )
                    for analog_response in assistant_response.analogs
                ]

                drug.analogs_description = assistant_response.analogs_description

            except Exception as ex:
                logger.exception(f"Failed to update drug for {assistant_response.name}: {str(ex)}")
                raise

        @staticmethod
        async def update_metabolism(
                drug: Drug, assistant_response: DrugMetabolismAssistantResponse
        ) -> None:
            try:
                drug.absorption = assistant_response.absorption
                drug.metabolism = assistant_response.metabolism
                drug.elimination = assistant_response.elimination
                drug.metabolism_description = assistant_response.metabolism_description

            except Exception as ex:
                logger.exception(f"Failed to update drug for {assistant_response.name}: {str(ex)}")
                raise

        async def update_pathways(
                self, drug: Drug, assistant_response: DrugPathwaysAssistantResponse,
                need_to_clean: bool = False
        ) -> None:
            try:
                if need_to_clean:
                    await self.session.execute(delete(DrugPathway).where(DrugPathway.drug_id == drug.id))

                drug.pathways = [
                    DrugPathway(
                        receptor=pathway_response.receptor,
                        binding_affinity=pathway_response.binding_affinity,
                        affinity_description=pathway_response.affinity_description,
                        activation_type=pathway_response.activation_type,
                        pathway=pathway_response.pathway,
                        effect=pathway_response.effect,
                        note=pathway_response.note,
                    )
                    for pathway_response in assistant_response.pathways
                ]

                drug.primary_action = assistant_response.mechanism_summary.primary_action
                drug.secondary_actions = assistant_response.mechanism_summary.secondary_actions
                drug.clinical_effects = assistant_response.mechanism_summary.clinical_effects

                drug.pathway_sources = assistant_response.pathway_sources

            except Exception as ex:
                logger.exception(f"Failed to update drug for {assistant_response.name}: {str(ex)}")
                raise

        async def update_combinations(
                self, drug: Drug, assistant_response: DrugCombinationsAssistantResponse,
                need_to_clean: bool = False
        ) -> None:
            try:
                if need_to_clean:
                    await self.session.execute(delete(DrugDosage).where(DrugDosage.drug_id == drug.id))

                drug.combinations = [
                    DrugCombination(
                        combination_type=combination_response.combination_type,
                        substance=combination_response.substance,
                        effect=combination_response.effect,
                        risks=combination_response.risks,
                        products=combination_response.products,
                    )
                    for combination_response in assistant_response.combinations
                ]

            except Exception as ex:
                logger.exception(f"Failed to update drug for {assistant_response.name}: {str(ex)}")
                raise

    @staticmethod
    async def update_researches(drug: Drug, researches: DrugResearchesAssistantResponse) -> Drug:
        try:
            drug.researches = [
                DrugResearch(
                    name=research_response.name,
                    description=research_response.description,
                    publication_date=research_response.publication_date,
                    url=research_response.url,
                    summary=research_response.summary,
                    journal=research_response.journal,
                    doi=research_response.doi,
                    authors=research_response.authors,
                    study_type=research_response.study_type,
                    interest=research_response.interest,
                )
                for research_response in researches.researches
            ]

            return drug

        except Exception as ex:
            logger.exception(f"Failed to update drug for {researches.name}: {str(ex)}")
            raise


async def get_drug_repository(
        session_generator: AsyncGenerator[AsyncSession, None] = Depends(get_async_session)
) -> DrugRepository:
    async with session_generator as session:
        return DrugRepository(session=session)
