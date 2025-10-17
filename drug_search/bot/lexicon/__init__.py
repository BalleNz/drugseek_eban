from drug_search.bot.lexicon.message_text import MessageTemplates
from drug_search.bot.utils.format_message_text import DrugMessageFormatter, UserProfileMessageFormatter


__all__ = [
    'MessageTemplates',
    'MessageText'
]


class MessageText:
    """Класс, копирующий функции из *MessageFormatters
    """

    # static messages
    HELLO = MessageTemplates.HELLO

    # drugs
    format_drug_briefly = DrugMessageFormatter.format_drug_briefly
    format_by_type = DrugMessageFormatter.format_by_type
    format_drugs_info = DrugMessageFormatter.format_drugs_info

    # user profile
    format_user_profile = UserProfileMessageFormatter.format_user_profile
