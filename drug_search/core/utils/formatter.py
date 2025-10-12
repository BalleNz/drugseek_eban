from drug_search.core.schemas import QuestionAssistantResponse
from drug_search.core.utils.message_templates import MessageTemplates


class ARQMessageTemplates:
    @staticmethod
    def format_assistant_answer(assistant_response: QuestionAssistantResponse):
        """Ответ со списком препаратов"""
        drugs_section: str = ""
        for i, drug in enumerate(assistant_response.drugs, start=1):
            drugs_section += (
                f"{i}) <b>{drug.drug_name}:</b>\n"
                f"{drug.description}\n"
                f"<u>Эффективность:</u> {drug.efficiency}\n\n"
            )

        return MessageTemplates.ASSISTANT_ANSWER_DRUGS.format(
            answer=assistant_response.answer,
            drugs_section=drugs_section
        )
