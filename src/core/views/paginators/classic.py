import enum
import typing as t

import disnake

from .. import BaseView

if t.TYPE_CHECKING:
    from src.utils.embeds import BaseEmbed


class Buttons(str, enum.Enum):
    PREVIOUS = "<:ArrowLeft:989134685068202024>"
    NEXT = "<:rightArrow:989136803284004874>"
    STOP = "<:dustbin:989150297333043220>"
    LAST = "<:DoubleArrowRight:989134892384256011>"
    FIRST = "<:DoubleArrowLeft:989134953142956152>"


class ClassicPaginator(BaseView):
    _footered: bool

    def __init__(self, user: disnake.Member, *, timeout: float = 180.0, items: list["BaseEmbed"]):
        super().__init__(user, timeout=timeout)
        self.page = 0
        self._items = items
        self._footered = False if not getattr(self, "_footered", False) else True
        self._update_state()

    def set_footer(self) -> None:
        for n, embed in enumerate(self._items, start=1):
            embed.add_footer(text=f"Page {n}/{len(self._items)}", icon_url=self.user.display_avatar)
        self._footered = True

    async def _update_message(
        self,
        interaction: disnake.MessageInteraction | disnake.ApplicationCommandInteraction,
    ) -> None:
        self._update_state()
        await interaction.edit_original_message(embed=self._items[self.page], view=self)

    def _update_state(self) -> None:
        self.set_footer() if not self._footered else None
        self.first.disabled = self.previous.disabled = self.page == 0
        self.next.disabled = self.last.disabled = self.page == len(self._items) - 1

    @disnake.ui.button(style=disnake.ButtonStyle.blurple, emoji=str(Buttons.FIRST.value))
    async def first(
        self,
        _button: disnake.ui.Button[disnake.ui.View],
        interaction: disnake.MessageInteraction,
    ) -> None:
        self.page = 0
        await self._update_message(interaction)

    @disnake.ui.button(style=disnake.ButtonStyle.blurple, emoji=str(Buttons.PREVIOUS.value))
    async def previous(
        self,
        _button: disnake.ui.Button[disnake.ui.View],
        interaction: disnake.MessageInteraction,
    ) -> None:
        self.page -= 1
        await self._update_message(interaction)

    @disnake.ui.button(style=disnake.ButtonStyle.blurple, emoji=str(Buttons.STOP.value))
    async def finish(
        self,
        _button: disnake.ui.Button[disnake.ui.View],
        interaction: disnake.MessageInteraction,
    ) -> None:
        await interaction.delete_original_response()
        self.stop()

    @disnake.ui.button(style=disnake.ButtonStyle.blurple, emoji=str(Buttons.NEXT.value))
    async def next(
        self,
        _button: disnake.ui.Button[disnake.ui.View],
        interaction: disnake.MessageInteraction,
    ) -> None:
        self.page += 1
        await self._update_message(interaction)

    @disnake.ui.button(style=disnake.ButtonStyle.blurple, emoji=str(Buttons.LAST.value))
    async def last(
        self,
        _button: disnake.ui.Button[disnake.ui.View],
        interaction: disnake.MessageInteraction,
    ) -> None:
        self.page = len(self._items) - 1
        await self._update_message(interaction)

    @classmethod
    async def start(
        cls,
        inter: disnake.ApplicationCommandInteraction,
        *,
        timeout: float = 180.0,
        items: list["BaseEmbed"],
    ) -> "ClassicPaginator":
        assert isinstance(inter.author, disnake.Member)
        assert isinstance(items, list)
        paginator = cls(inter.author, timeout=timeout, items=items)
        paginator.message = await inter.original_response()
        await paginator._update_message(inter)
        return paginator
