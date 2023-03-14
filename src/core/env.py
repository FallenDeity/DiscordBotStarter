import os
import typing as t
from dataclasses import dataclass

from dotenv import load_dotenv

from .errors import ConversionError, MissingEnvironmentVariable

__all__: tuple[str, ...] = (
    "TEMPLATEENV",
    "MISSING",
)


MISSING = object()
# pyright: reportUnknownVariableType=false
load_dotenv()
# we need to do due to generic typing of load_dotenv


@dataclass(kw_only=True)
class Variable:
    name: str
    default: t.Any = MISSING
    cast: t.Callable[[str], t.Any] = str
    required: bool = False

    def __post_init__(self) -> None:
        self.default = os.getenv(self.name, self.default)
        if self.default is MISSING and self.required:
            raise MissingEnvironmentVariable(self.name)
        try:
            self.default = self.cast(self.default)
        except Exception as e:
            raise ConversionError(self.name, self.cast, e) from e

    def __str__(self) -> str:
        if self.cast is str:
            return self.default
        else:
            return str(super())

    def __call__(self) -> t.Any:
        return self.default

    def __get__(self, instance: t.Any, owner: t.Any) -> t.Any:
        return self.default


class Environment:
    TOKEN = Variable(name="TOKEN")
    PGURL = Variable(name="PGURL")


TEMPLATEENV = Environment()
