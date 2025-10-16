from drug_search.bot.keyboards import ArrowTypes
from drug_search.core.lexicon import ASSISTANT_ANSWER_DRUG_COUNT
from drug_search.core.schemas import QuestionAssistantResponse
from drug_search.core.utils.message_templates import MessageTemplates


class ARQMessageTemplates:
    @staticmethod
    def format_assistant_answer(
            assistant_response: QuestionAssistantResponse,
            arrow: ArrowTypes
    ):
        """Ответ со списком препаратов"""
        drugs_section: str = ""
        start_index: int = 1 if arrow == ArrowTypes.FORWARD else ASSISTANT_ANSWER_DRUG_COUNT + 1

        for i, drug in enumerate(assistant_response.drugs, start=start_index):
            drugs_section += (
                f"{i}) <b>{drug.drug_name}:</b>\n"
                f"{drug.description}\n"
                f"<u>Эффективность:</u> {drug.efficiency}\n\n"
            )

        return MessageTemplates.ASSISTANT_ANSWER_DRUGS.format(
            answer=assistant_response.answer,
            drugs_section=drugs_section
        )
