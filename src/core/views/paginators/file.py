import typing as t

import disnake

from .classic import ClassicPaginator

if t.TYPE_CHECKING:
    from src.utils.embeds import BaseEmbed


__all__: tuple[str, ...] = ("FilePaginator",)


class FilePaginator(ClassicPaginator):
    def __init__(self, user: disnake.Member, *, timeout: float = 180.0, items: list["BaseEmbed"]):
        super().__init__(user, timeout=timeout, items=items)
        self._cache: dict[int, str] = {}

    async def _update_message(
        self,
        interaction: disnake.MessageInteraction | disnake.ApplicationCommandInteraction,
    ) -> None:
        self._update_state()
        embed = self._items[self.page]
        if (file := self._cache.get(self.page)) is None:
            file = embed.file
            embed.set_image(url=f"attachment://{file.filename}")
            message = await interaction.edit_original_response(embed=embed, attachments=[], view=self, file=file)
            self._cache[self.page] = str(message.embeds[0].image.url)
            return
        embed.set_image(url=file)
        await interaction.edit_original_response(embed=embed, view=self, attachments=[])

    async def on_timeout(self) -> None:
        self._disable()
        embed = self._items[self.page]
        file = disnake.File(embed.file.fp, filename=embed.file.filename)
        embed.set_image(url=f"attachment://{file.filename}")
        await self.safe_edit(embed=embed, view=self, attachments=[], file=file)

    @classmethod
    async def start(
        cls,
        inter: disnake.ApplicationCommandInteraction,
        *,
        timeout: float = 180.0,
        items: list["BaseEmbed"],  # pyright: reportIncompatibleMethodOverride=false
    ) -> "FilePaginator":
        assert isinstance(inter.author, disnake.Member)
        paginator = cls(inter.author, timeout=timeout, items=items)
        paginator.message = await inter.original_response()
        await paginator._update_message(inter)
        return paginator
