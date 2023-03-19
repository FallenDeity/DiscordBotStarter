import typing as t

import disnake

from .classic import ClassicPaginator

if t.TYPE_CHECKING:
    from src import TemplateBot
    from src.utils.embeds import BaseEmbed

    from .. import BaseView  # noqa: F401

__all__: tuple[str, ...] = (
    "MenuPaginator",
    "MenuFilePaginator",
)


class MenuPaginator(ClassicPaginator):
    def __init__(
        self,
        user: disnake.Member,
        *,
        timeout: float = 180.0,
        items: dict[str, list["BaseEmbed"]],
        bot: t.Optional["TemplateBot"] = None,
    ):
        self.user = user
        self.bot = bot
        self.categories = list(items.keys())
        self.category = self.categories[0]
        self._data = items
        self.set_footer()
        self.select = CategorySelect(self, categories=self.categories)
        super().__init__(user, timeout=timeout, items=self._data[self.category])
        self.add_item(self.select)

    def set_footer(self) -> None:
        for category in self.categories:
            for n, embed in enumerate(self._data[category], start=1):
                embed.add_footer(
                    text=f"Page {n}/{len(self._data[category])}",
                    icon_url=self.user.display_avatar,
                )
        self._footered = True

    @classmethod
    async def start(
        cls,
        inter: disnake.ApplicationCommandInteraction,
        *,
        timeout: float = 180.0,
        bot: t.Optional["TemplateBot"] = None,
        items: dict[str, list["BaseEmbed"]],  # pyright: reportIncompatibleMethodOverride=false
    ) -> "MenuPaginator":
        assert isinstance(inter.author, disnake.Member)
        assert isinstance(items, dict)
        paginator = cls(inter.author, timeout=timeout, items=items, bot=bot)  # type: ignore
        paginator.message = await inter.original_response()
        await paginator._update_message(inter)
        return paginator


class CategorySelect(disnake.ui.StringSelect["BaseView"]):
    def __init__(
        self,
        paginator: MenuPaginator,
        *,
        placeholder: str = "Select a category",
        categories: list[str],
    ):
        self.paginator = paginator
        options = []
        for category in categories:
            emoji = self.paginator.bot.emoji(category) if self.paginator.bot else None
            options.append(disnake.SelectOption(label=category, value=category, emoji=emoji))
        super().__init__(
            placeholder=placeholder,
            options=options,
        )

    async def callback(self, interaction: disnake.MessageInteraction) -> None:
        self.paginator.category = self.values[0]
        self.paginator.page = 0
        self.paginator._items = self.paginator._data[self.paginator.category]
        await self.paginator._update_message(interaction)


class MenuFilePaginator(MenuPaginator):
    def __init__(
        self,
        user: disnake.Member,
        *,
        timeout: int = 180,
        items: dict[str, list["BaseEmbed"]],
        bot: t.Optional["TemplateBot"] = None,
    ):
        self.user = user
        self._data = items
        self._cache: dict[str, dict[int, str]] = {}
        super().__init__(user, timeout=timeout, items=items, bot=bot)

    async def _update_message(
        self,
        interaction: disnake.MessageInteraction | disnake.ApplicationCommandInteraction,
    ) -> None:
        self._update_state()
        embed = self._items[self.page]
        _cache_category = self._cache.get(self.category, {})
        if self.page in _cache_category:
            embed.set_image(url=_cache_category[self.page])
            await interaction.edit_original_response(embed=embed, view=self, attachments=[])
            return
        file = embed.file
        embed.set_image(url=f"attachment://{file.filename}")
        message = await interaction.edit_original_response(embed=embed, files=[file], view=self)
        self._cache.setdefault(self.category, {})[self.page] = str(message.embeds[0].image.url)

    async def on_timeout(self) -> None:
        self._disable()
        embed = self._items[self.page]
        file = embed.file
        embed.set_image(url=f"attachment://{file.filename}")
        await self.safe_edit(embed=embed, view=self, attachments=[], file=file)

    @classmethod
    async def start(
        cls,
        inter: disnake.ApplicationCommandInteraction,
        *,
        timeout: int = 180,
        bot: t.Optional["TemplateBot"] = None,
        items: dict[str, list["BaseEmbed"]],  # pyright: reportIncompatibleMethodOverride=false
    ) -> "MenuFilePaginator":
        assert isinstance(inter.author, disnake.Member)
        assert isinstance(items, dict)
        paginator = cls(inter.author, timeout=timeout, items=items, bot=bot)  # type: ignore
        paginator.message = await inter.original_response()
        await paginator._update_message(inter)
        return paginator
