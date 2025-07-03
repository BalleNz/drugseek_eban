from typing import TypeVar, Generic, Type

from core.database.models.base import IDMixin

T = TypeVar("T", bound=IDMixin)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get_model(self):
        ...

    def create_model(self):
        ...

    def update_model(self):
        # updated_at update
        ...

    def delete_model(self):
        ...
