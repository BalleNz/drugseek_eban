from core.database.repository.drug import DrugRepository


class DrugService:
    """
    ONLY FOR DEPENDENCY INJECTIONS,
    BECAUSE OF SESSION.

    example:
        with
    """
    def __init__(self):
        self._repo = DrugRepository(session=...)
