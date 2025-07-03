from typing import TypeVar, Generic

T = TypeVar("T")


class BaseInterface(Generic[T]):
    def __init__(self):
        self.model = ...


# TODO: ПОПРАВИТЬ, добавить интерфейс (если нужно) и определить методы

class Base(BaseInterface):
    ...
