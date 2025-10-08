from drug_search.core.schemas import QuestionAssistantResponse
from drug_search.core.utils.message_templates import MessageTemplates


class ARQMessageTemplates:
    @staticmethod
    def format_assistant_answer(assistant_response: QuestionAssistantResponse):
        """Ответ со списком препаратов"""
        drugs_section: str = ""
        for i, drug in enumerate(assistant_response.drugs, start=1):
            drugs_section += f"""
            {i}) <b>{drug.drug_name}:</b>
            {drug.description}
            <u>Эффективность:</u> {drug.efficiency}
            """

        return MessageTemplates.ASSISTANT_ANSWER_DRUGS.format(
            answer=assistant_response.answer,
            drugs_section=drugs_section
        )
