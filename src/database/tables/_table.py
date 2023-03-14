import abc
import typing

if typing.TYPE_CHECKING:
    from .. import Database


__all__: tuple[str, ...] = ("Table",)


class Table(abc.ABC):
    def __init__(self, database: "Database") -> None:
        self.db = database

    @abc.abstractmethod
    async def setup(self) -> None:
        ...
