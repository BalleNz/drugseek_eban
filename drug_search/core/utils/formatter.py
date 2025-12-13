from drug_search.core.lexicon import ASSISTANT_ANSWER_DRUG_COUNT_PER_PAGE, ARROW_TYPES
from drug_search.core.lexicon.message_templates import MessageTemplates
from drug_search.core.schemas import QuestionDrugsAssistantResponse, QuestionAssistantResponse


class TelegramMessageTemplates:
    """Форматирование сообщений для отправки в Telegram"""
    @staticmethod
    def format_assistant_answer_drugs(
            assistant_response: QuestionDrugsAssistantResponse,
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

    @staticmethod
    def format_assistant_answer(
            assistant_response: QuestionAssistantResponse,
    ):
        """Ответ на вопрос от ассистента"""

        # [ основной текст ]
        content: str = ""
        for blocks_content in assistant_response.blocks_content:
            block_header = blocks_content.blocks_header or ""
            block_description = blocks_content.blocks_description or ""

            # [ content appending ]
            content += f"<u>{block_header}</u>\n\n" if block_header else ""
            content += f"{block_description}\n\n" if block_description else ""

            for block in blocks_content.content:
                content += f"<b>{block.block_header}</b>\n"
                for i, brick in enumerate(block.bricks):

                    brick_header = ""
                    if brick.brick_header and brick.brick_description:
                        brick_header = f"<u>{brick.brick_header}</u>: {brick.brick_description}"
                    elif brick.brick_header:
                        brick_header = f"{brick.brick_header}"

                    if i == len(block.bricks) - 1:
                        content += f"<b>└──</b> {brick_header}\n\n"
                    else:
                        content += f"├── {brick_header}\n"

        # [ заключение ]
        conclusion_section: str = (
            f"<b>{assistant_response.conclusion.conclusion_header}</b>: "
            f"{assistant_response.conclusion.conclusion_description}"
        )

        return MessageTemplates.ASSISTANT_ANSWER.format(
            header_with_emoji=assistant_response.header,
            content=content,
            conclusion_section=conclusion_section
        )
