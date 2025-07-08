class InvalidAssistantResponseStructureError(Exception):
    """Custom exception raised when an assistant returns a response that does not conform to the required structure."""
    pass


class DrugNotFound(Exception):
    "Препарат не найден, но он точно существует. Может быть ошибка из-за неправильного написания названия на стороне клиента."
    pass

class AssistantResponseError(Exception):
    "Wrong response data from assistant."
    pass