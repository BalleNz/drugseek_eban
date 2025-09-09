import logging
import uuid
from datetime import datetime
from typing import Optional, Union, AsyncGenerator

from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from drug_search.core.schemas import (AssistantResponseCombinations, DrugSchema, AssistantDosageDescriptionResponse,
                                      AssistantResponseDrugPathways, AssistantResponseDrugResearch)
from drug_search.core.utils.exceptions import AssistantResponseError, DrugNotFound
from drug_search.infrastructure.database.engine import get_async_session
from drug_search.infrastructure.database.models.drug import (Drug, DrugSynonym, DrugCombination, DrugPathway,
                                                             DrugAnalog, DrugDosage, DrugResearch)
from drug_search.infrastructure.database.repository.base_repo import BaseRepository

logger = logging.getLogger("bot.core.repository.drug")


class DrugRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Drug, session=session)

    # FUTURE: рефакторинг, схемы в моделях бд + методы преобразования из схемы в модель и наоборот
    @staticmethod
    def _convert_to_drug_schema(drug: Drug):
        # Явное преобразование в словарь для вложенных объектов
        drug_dict = {
            **{k: v for k, v in drug.__dict__.items() if not k.startswith('_')},
            "dosages": [dosage.__dict__ for dosage in drug.dosages],
            "pathways": [pathway.__dict__ for pathway in drug.pathways],
            "synonyms": [synonym.__dict__ for synonym in drug.synonyms],
            "analogs": [analog.__dict__ for analog in drug.analogs],
            "combinations": [combination.__dict__ for combination in drug.combinations],
            # "prices": [price.__dict__ for price in drug.prices],
        }
        return DrugSchema.model_validate(drug_dict)

    async def find_drug_by_query(self, user_query: str) -> Optional[DrugSchema]:
        """
        Поиск препарата по триграммному сходству с синонимами (один запрос).
        Возвращает DrugSchema с максимальной схожестью или None.

        :param user_query: Запрос пользователя для поиска препарата используя триграммы.
        """
        stmt = (
            select(Drug)
            .join(Drug.synonyms)
            .where(
                func.similarity(
                    func.lower(DrugSynonym.synonym),
                    func.lower(user_query)
                ) > 0.5
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
                selectinload(Drug.researchs)
            )
        )

        result = await self.session.execute(stmt)
        drug: Drug = result.scalar_one_or_none()

        if not drug:
            return None

        return self._convert_to_drug_schema(drug)

    async def get_with_all_relationships(self, drug_id: uuid.UUID, need_model: bool = False)\
            -> Union[Drug, DrugSchema, None]:
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
                selectinload(Drug.researchs)
            )
        )

        result = await self.session.execute(stmt)
        drug = result.scalars().one_or_none()

        if not drug:
            return None

        # Если нужна модель
        if need_model:
            return drug

        return self._convert_to_drug_schema(drug)

    async def create_drug(self, drug_name: str) -> DrugSchema:
        """
        Создает модель препарата после валидации перед обновлением его таблиц.

        :param drug_name: ДВ на английском.
        """
        drug: Drug = Drug(
            name=drug_name,
        )
        await self.save(drug)
        return DrugSchema.model_validate(drug)

    async def update_dosages(
            self,
            drug_id: uuid.UUID,
            assistant_response: AssistantDosageDescriptionResponse
    ) -> None:
        """
        Обновляет три смежные таблицы:
            - Обновляет данные о дозировках препарата.
            - Обновляет синонимы.
            - Обновляет аналоги препарата.
        """
        drug: Drug = await self.get_model(drug_id)
        if not drug:
            raise DrugNotFound

        try:
            drug.name = assistant_response.drug_name
            drug.name_ru = assistant_response.drug_name_ru
            drug.latin_name = assistant_response.latin_name
            drug.description = assistant_response.description
            drug.classification = assistant_response.classification
            drug.dosages_fun_fact = assistant_response.dosages_fun_fact
            drug.dosages_sources = assistant_response.sources
            drug.is_danger = assistant_response.is_danger

            drug.absorption = assistant_response.pharmacokinetics.absorption
            drug.metabolism = assistant_response.pharmacokinetics.metabolism
            drug.elimination = assistant_response.pharmacokinetics.elimination
            drug.time_to_peak = assistant_response.pharmacokinetics.time_to_peak

            dosages_data = []
            for route, methods in assistant_response.dosages.items():
                if methods:
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

            await self.save(drug)

        except Exception as ex:
            logger.error(f"Failed to update dosages for {drug.name}: {str(ex)}")
            raise ex

    async def update_pathways(
            self,
            drug_id: uuid.UUID,
            assistant_response: AssistantResponseDrugPathways
    ) -> None:
        """
        Обновляет таблицу:
            — Пути активации препарата.
        """
        drug: Drug = await self.get_model(drug_id)
        if not drug:
            raise DrugNotFound

        try:
            if assistant_response.mechanism_summary:
                drug.pathways_sources = assistant_response.mechanism_summary.sources
                drug.primary_action = assistant_response.mechanism_summary.primary_action
                drug.secondary_actions = assistant_response.mechanism_summary.secondary_actions
                drug.clinical_effects = assistant_response.mechanism_summary.clinical_effects
            else:
                logger.warning("ASSISTANT RESPONSE: Missing mechanism summary!")
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

            await self.save(drug)

        except Exception as ex:
            logger.error(f"Failed to update pathways for {drug.name}: {str(ex)}")
            raise ex

    async def update_combinations(
            self,
            drug_id: uuid.UUID,
            assistant_response: AssistantResponseCombinations
    ) -> None:
        """
        Обновляет таблицу:
            — Комбинации препарата.
        """
        drug: Drug = await self.get_model(drug_id)
        if not drug:
            raise DrugNotFound

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
                    sources=combination.sources
                ))

            drug.combinations = new_combinations

            await self.save(drug)

        except Exception as ex:
            logger.error(f"Failed to update combinations for {drug.name}, {drug.id}: {str(ex)}")
            raise ex

    async def update_researchs(
            self,
            drug_id: uuid.UUID,
            researchs: list[AssistantResponseDrugResearch]
    ) -> None:
        """
        Обновляет таблицу:
            — Исследования препарата.
        """
        drug: Drug = await self.get_model(drug_id)
        if not drug:
            raise DrugNotFound

        try:
            old_researchs_doi = [res.doi for res in drug.researchs]
            new_researchs = []
            # каждый раз будет новый список,
            # TODO на стороне клиента обновление исследований будет доступно раз в месяц.
            for research in researchs:
                if research.doi in old_researchs_doi:
                    continue
                new_researchs.append(
                    DrugResearch(
                        name=research.name,
                        description=research.description,
                        date=research.publication_date,
                        url=research.url,
                        summary=research.summary,
                        journal=research.journal,
                        doi=research.doi,
                        authors=research.authors,
                        study_type=research.study_type,
                        interest=research.interest
                    )
                )

                drug.researchs += new_researchs

                await self.save(drug)

        except Exception as ex:
            logger.error(f"Error while updating researchs model: {ex}")
            raise ex

    async def get_drug(self, drug_id: uuid.UUID) -> DrugSchema:
        """Возращает описание препарата без смежных таблиц"""
        drug_model: Drug = await self.session.get(self.model, drug_id)
        return DrugSchema.model_validate(drug_model)


async def get_drug_repository(
        session_generator: AsyncGenerator[AsyncSession, None] = Depends(get_async_session)
) -> DrugRepository:
    async with session_generator as session:
        return DrugRepository(session=session)
