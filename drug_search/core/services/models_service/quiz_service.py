import logging
import random
import uuid

from drug_search.core.schemas import UserSchema
from drug_search.core.schemas.quiz_schemas import (
    QuizAnswerResponse,
    QuizDrugSchema,
    QuizOptionSchema,
    QuizQuestionResponse,
)
from drug_search.core.services.cache_logic.redis_service import RedisService
from drug_search.infrastructure.database.repository.drug_repo import DrugRepository

logger = logging.getLogger(__name__)

QUIZ_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("description", "Описание", "Какой препарат описан так:\n\n«{value}»?"),
    ("classification", "Классификация", "К какому препарату относится классификация:\n\n«{value}»?"),
    ("primary_action", "Механизм", "Какой препарат действует так:\n\n«{value}»?"),
    ("fact", "Факт", "Какому препарату принадлежит факт:\n\n«{value}»?"),
)

QUIZ_TTL_SECONDS = 600


class QuizService:
    def __init__(self, drug_repo: DrugRepository, redis_service: RedisService):
        self.drug_repo = drug_repo
        self.redis_service = redis_service

    @staticmethod
    def _display_name(drug: QuizDrugSchema) -> str:
        return drug.drug_name_ru or drug.drug_name

    @staticmethod
    def _truncate(text: str, max_len: int = 280) -> str:
        if len(text) <= max_len:
            return text
        return text[: max_len - 3].rstrip() + "..."

    async def generate_question(self, user: UserSchema) -> QuizQuestionResponse:
        allowed_ids = user.allowed_drug_ids()
        drugs = await self.drug_repo.get_drugs_for_quiz(allowed_ids, limit=30)

        if len(drugs) < 4:
            raise ValueError("Недостаточно препаратов в базе для викторины")

        correct_drug = random.choice(drugs)
        wrong_drugs = random.sample(
            [drug for drug in drugs if drug.drug_id != correct_drug.drug_id],
            3,
        )

        available_fields = [
            (field, title, template)
            for field, title, template in QUIZ_FIELDS
            if getattr(correct_drug, field)
        ]
        if not available_fields:
            raise ValueError("У выбранного препарата недостаточно данных для вопроса")

        field_name, _, question_template = random.choice(available_fields)
        field_value = self._truncate(getattr(correct_drug, field_name))
        question_text = question_template.format(value=field_value)

        options_drugs = [correct_drug, *wrong_drugs]
        random.shuffle(options_drugs)

        quiz_id = str(uuid.uuid4())
        await self.redis_service.redis.setex(
            f"quiz:{quiz_id}",
            QUIZ_TTL_SECONDS,
            str(correct_drug.drug_id),
        )

        return QuizQuestionResponse(
            quiz_id=quiz_id,
            question=question_text,
            options=[
                QuizOptionSchema(
                    drug_id=drug.drug_id,
                    name=self._display_name(drug),
                )
                for drug in options_drugs
            ],
        )

    async def check_answer(
            self,
            quiz_id: str,
            selected_drug_id: uuid.UUID,
            user: UserSchema,
    ) -> QuizAnswerResponse:
        correct_drug_id_raw = await self.redis_service.redis.get(f"quiz:{quiz_id}")
        if not correct_drug_id_raw:
            raise ValueError("Викторина истекла. Начните новый вопрос.")

        correct_drug_id = uuid.UUID(
            correct_drug_id_raw.decode() if isinstance(correct_drug_id_raw, bytes) else correct_drug_id_raw
        )
        await self.redis_service.redis.delete(f"quiz:{quiz_id}")

        correct_drug = await self.drug_repo.get_with_all_relationships(correct_drug_id)
        correct_name = self._display_name(
            QuizDrugSchema(
                drug_id=correct_drug_id,
                drug_name=correct_drug.name if correct_drug else "",
                drug_name_ru=correct_drug.name_ru if correct_drug else None,
            )
        ) if correct_drug else "неизвестно"

        is_correct = selected_drug_id == correct_drug_id
        explanation = None
        if not is_correct:
            explanation = f"Правильный ответ: <b>{correct_name}</b>"

        return QuizAnswerResponse(
            is_correct=is_correct,
            correct_name=correct_name,
            explanation=explanation,
        )
