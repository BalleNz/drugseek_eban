import logging
import uuid
from datetime import datetime
from typing import Optional, Union, AsyncGenerator

from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from drug_search.core.schemas import (AssistantResponseCombinations, DrugSchema, DrugBrieflyAssistantResponse,
                                      AssistantResponseDrugPathways, AssistantResponseDrugResearch)
from drug_search.core.utils.exceptions import AssistantResponseError, DrugNotFound
from drug_search.infrastructure.database.engine import get_async_session
from drug_search.infrastructure.database.models.drug import (Drug, DrugSynonym, DrugCombination, DrugPathway,
                                                             DrugAnalog, DrugDosage, DrugResearch)
from drug_search.infrastructure.database.repository.base_repo import BaseRepository

logger = logging.getLogger(__name__)


class DrugRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Drug, session=session)

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

    async def update_dosages(
            self,
            drug: DrugSchema,
            assistant_response: DrugBrieflyAssistantResponse
    ) -> DrugSchema:
        """
        Обновляет три смежные таблицы:
            - Обновляет данные о дозировках препарата.
            - Обновляет синонимы.
            - Обновляет аналоги препарата.
        """
        logger.info(f"UpdateDosages: {drug.model_json_schema()}")

        drug: Drug = self.model.from_pydantic(drug)
        try:
            drug.name = assistant_response.drug_name
            drug.name_ru = assistant_response.drug_name_ru
            drug.latin_name = assistant_response.latin_name
            drug.description = assistant_response.description
            drug.classification = assistant_response.classification
            drug.dosages_fun_fact = assistant_response.dosages_fun_fact
            drug.fun_fact = assistant_response.fun_fact
            drug.analogs_description = assistant_response.analogs_description
            drug.metabolism_description = assistant_response.metabolism_description
            drug.dosage_sources = assistant_response.dosage_sources
            drug.absorption = assistant_response.absorption
            drug.metabolism = assistant_response.metabolism
            drug.elimination = assistant_response.elimination
            drug.time_to_peak = assistant_response.time_to_peak
            drug.danger_classification = assistant_response.danger_classification
            dosages_data = []  #TODO чекнуть дебаг поля некоторые не обновляются
            for route, methods in assistant_response.dosages.items():
                if methods and route:
                    for method, params in methods.items():
                        if params:
                            dosage = DrugDosage(
                                drug_id=drug.id,
                                route=route,
                                method=method,
                                **params.model_dump(exclude_none=True)
                            )
                            dosages_data.append(dosage)
            drug.dosages = dosages_data
            drug.synonyms = [
                DrugSynonym(
                    synonym=synonym
                )
                for synonym in assistant_response.synonyms
            ]
            drug.analogs = [
                DrugAnalog(
                    analog_name=analog.analog_name,
                    percent=analog.percent,
                    difference=analog.difference
                )
                for analog in assistant_response.analogs
            ]
            drug.updated_at = datetime.now()
        except Exception as ex:
            logger.error(f"Failed to update dosages for {drug.name}: {str(ex)}")
            raise ex
        return drug.get_schema()

    async def update_pathways(
            self,
            drug: DrugSchema,
            assistant_response: AssistantResponseDrugPathways
    ) -> DrugSchema:
        """
        Обновляет таблицу:
            — Пути активации препарата.
        """
        drug: Drug = self.model.from_pydantic(drug)
        try:
            if assistant_response.mechanism_summary:
                drug.primary_action = assistant_response.mechanism_summary.primary_action
                drug.secondary_actions = assistant_response.mechanism_summary.secondary_actions
                drug.clinical_effects = assistant_response.mechanism_summary.clinical_effects
            else:
                logger.error("ASSISTANT RESPONSE: Missing mechanism summary!")
                raise AssistantResponseError

            # Создаем новые DrugPathways объекты
            new_pathways = []
            for pathway_data in assistant_response.pathways:
                new_pathways.append(DrugPathway(
                    drug_id=drug.id,
                    receptor=pathway_data.receptor,
                    binding_affinity=pathway_data.binding_affinity,
                    affinity_description=pathway_data.affinity_description,
                    activation_type=pathway_data.activation_type,
                    pathway=pathway_data.pathway,
                    effect=pathway_data.effect,
                    note=pathway_data.note,
                ))
            drug.pathways = new_pathways
            drug.pathways_sources = assistant_response.pathway_sources
        except Exception as ex:
            logger.error(f"Failed to update pathways for {drug.name}: {str(ex)}")
            raise ex
        return drug.get_schema()

    async def update_combinations(
            self,
            drug: DrugSchema,
            assistant_response: AssistantResponseCombinations
    ) -> DrugSchema:
        """
        Обновляет таблицу:
            — Комбинации препарата.
        """
        drug: Drug = self.model.from_pydantic(drug)
        try:
            new_combinations = []
            for combination in assistant_response.combinations:
                new_combinations.append(DrugCombination(
                    drug_id=drug.id,
                    combination_type=combination.combination_type,
                    substance=combination.substance,
                    effect=combination.effect,
                    risks=combination.risks,
                    products=combination.products,
                ))
            drug.combinations = new_combinations
        except Exception as ex:
            logger.error(f"Failed to update combinations for {drug.name}, {drug.id}: {str(ex)}")
            raise ex
        return drug.get_schema()

    async def update_researches(
            self,
            drug_id: uuid.UUID,
            researches: list[AssistantResponseDrugResearch]
    ) -> None:
        """
        Обновляет таблицу:
            — Исследования препарата.
        """
        drug: Drug = await self.get_model(drug_id)
        if not drug:
            raise DrugNotFound
        try:
            old_researches_doi = [res.doi for res in drug.researches]
            new_researches = drug.researches.copy()
            for research in researches:
                if research.doi in old_researches_doi:
                    continue
                new_researches.append(
                    DrugResearch(
                        name=research.name,
                        description=research.description,
                        publication_date=research.publication_date,
                        url=research.url,
                        summary=research.summary,
                        journal=research.journal,
                        doi=research.doi,
                        authors=research.authors,
                        study_type=research.study_type,
                        interest=research.interest
                    )
                )
                drug.researches += new_researches
        except Exception as ex:
            logger.error(f"Error while updating researches model: {ex}")
            raise ex
        await self.save(drug)


async def get_drug_repository(
        session_generator: AsyncGenerator[AsyncSession, None] = Depends(get_async_session)
) -> DrugRepository:
    async with session_generator as session:
        return DrugRepository(session=session)
