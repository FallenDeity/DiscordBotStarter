import enum

__all__: tuple[str, ...] = (
    "Colors",
    "BackgroundColors",
    "Styles",
    "AnsiBuilder",
)


class Style(enum.IntEnum):
    def __str__(self) -> str:
        return f"{self.value}"


class Colors(Style):
    GRAY = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37


class BackgroundColors(Style):
    FIREFLY_DARK_BLUE = 40
    ORANGE = 41
    MARBLE_BLUE = 42
    GREYISH_TURQUOISE = 43
    GRAY = 44
    INDIGO = 45
    LIGHT_GRAY = 47
    WHITE = 48


class Styles(Style):
    NORMAL = 0
    BOLD = 1
    UNDERLINE = 4


class AnsiBuilder:
    def __init__(self, text: str, *styles: Style) -> None:
        self.text = text if text else "No text provided"
        self.cursor = 0
        self.styles: list[Style] = list(styles)

    def __str__(self) -> str:
        return self.build()

    def write(self, text: str, cursor: int = -1) -> None:
        self.text = self.text[:cursor] + text + self.text[cursor:]

    def build(self, block: bool = True) -> str:
        text = f"\033[{';'.join(str(style) for style in self.styles)}m{self.text}\033[0m"
        return f"```ansi\n{text}```" if block else text

    @classmethod
    def from_string_to_ansi(cls, text: str, *styles: Style) -> str:
        return str(cls(text, *styles))
