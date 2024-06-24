import abc
import typing

if typing.TYPE_CHECKING:
    from .. import Database
    from ..models import Record


__all__: tuple[str, ...] = ("Table",)


T = typing.TypeVar("T", bound="Record")


class Table(abc.ABC, typing.Generic[T]):
    def __init__(self, database: "Database") -> None:
        self.db = database

    @abc.abstractmethod
    async def setup(self) -> None:
        ...

    @abc.abstractmethod
    async def get_all(self) -> list[T]:
        ...

    @abc.abstractmethod
    async def get(self, id: int) -> T:
        ...

    @abc.abstractmethod
    async def create(self, record: T) -> None:
        ...

    @abc.abstractmethod
    async def update(self, record: T) -> None:
        ...

    @abc.abstractmethod
    async def delete(self, record: T) -> None:
        ...
