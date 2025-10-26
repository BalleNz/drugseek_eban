from drug_search.core.lexicon import ASSISTANT_ANSWER_DRUG_COUNT_PER_PAGE, ARROW_TYPES
from drug_search.core.lexicon.message_templates import MessageTemplates
from drug_search.core.schemas import QuestionAssistantResponse


class ARQMessageTemplates:
    @staticmethod
    def format_assistant_answer(
            assistant_response: QuestionAssistantResponse,
            arrow: ARROW_TYPES
    ):
        """Ответ со списком препаратов"""
        drugs_section: str = ""
        start_index: int = 1 if arrow == ARROW_TYPES.FORWARD else ASSISTANT_ANSWER_DRUG_COUNT_PER_PAGE + 1
        end_index: int = 3 if arrow == ARROW_TYPES.FORWARD else 6

        for i, drug in enumerate(assistant_response.drugs[start_index-1:end_index], start=start_index):
            drugs_section += (
                f"{i}) <b>{drug.drug_name}:</b>\n"
                f"{drug.description}\n"
                f"<u>Эффективность:</u> {drug.efficiency}\n\n"
            )

        return MessageTemplates.ASSISTANT_ANSWER_DRUGS.format(
            answer=assistant_response.answer,
            drugs_section=drugs_section
        )
