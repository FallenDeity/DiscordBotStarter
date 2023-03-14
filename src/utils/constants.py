import enum
import pathlib
import typing as t

import attrs

__all__: tuple[str, ...] = (
    "CHANNELS",
    "PATHS",
    "DEVELOPERS",
    "TIPS",
    "EMOJIS",
    "GUILD_ID",
    "BOT_ID",
    "INVITE",
    "WEBSITE",
    "GITHUB",
)


class BaseEnum(enum.Enum):
    def __get__(self, *_: t.Any) -> t.Any:
        return self.value


@attrs.define(repr=False, slots=True, kw_only=True)
class Emoji:
    id: int
    name: str
    animated: bool = False

    def __repr__(self) -> str:
        animated = "a" if self.animated else ""
        return f"<{animated}:_:{self.id}>"


DEVELOPERS: set[int] = {656838010532265994}
TIPS: tuple[str] = ("Add some cool tips here!",)
GUILD_ID: int = 1075101106369216583
BOT_ID: int = 925605671997681674
INVITE: str = "rGM9tDxR6Y"
WEBSITE: str = ""
GITHUB: str = ""


class CHANNELS(enum.IntEnum):
    LOGS = 1085144172064948285


class PATHS(BaseEnum):
    BASE = pathlib.Path("src")
    BIN = pathlib.Path("src/bin")
    DATABASE = pathlib.Path("src/database")
    EXTENSIONS = pathlib.Path("src/ext")
    MIGRATIONS = pathlib.Path("src/bin/migrations")
    TABLES = pathlib.Path("src/database/tables")


class EMOJIS(BaseEnum):
    def __get__(self, *_: t.Any) -> Emoji:
        return self.value
