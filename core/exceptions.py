class NotFound(Exception):
    """Custom exception raises when an item from DB is not found."""
    pass


class InvalidAssistantResponseStructureError(Exception):
    """Custom exception raised when an assistant returns a response that does not conform to the required structure."""
    pass
