import asyncio
import random
import typing

import disnake

from src.core.errors import ModalException, ViewException, ViewTimeout
from src.utils.ansi import AnsiBuilder, Colors, Styles
from src.utils.constants import ERRORS

__all__: tuple[str, ...] = ("BaseView",)
# pyright: reportUnknownVariableType=false


class BaseView(disnake.ui.View):
    interaction: disnake.Interaction
    message: disnake.Message

    def __init__(self, user: disnake.Member | disnake.User, *, timeout: float = 180.0):
        super().__init__(timeout=timeout)
        self.user = user

    async def on_timeout(self) -> None:
        self._disable()
        await self.safe_edit(view=self)

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if interaction.user.id == self.user.id:
            await interaction.response.defer()
            self.interaction = interaction
            return True
        await interaction.send("You are not allowed to use this view.", ephemeral=True)
        return False

    async def safe_edit(self, **kwargs: typing.Any) -> None:
        try:
            await self.message.edit(**kwargs)
        except (AttributeError, disnake.NotFound, disnake.Forbidden):
            await self.interaction.edit_original_response(**kwargs)
        except Exception as e:
            try:
                await self.interaction.response.edit_message(**kwargs)
            except disnake.InteractionResponded:
                await self.interaction.client.on_error("view_error", e)

    def _disable(self) -> None:
        for child in self.children:
            if isinstance(child, disnake.ui.Button) or isinstance(child, disnake.ui.Select):
                child.disabled = True

    async def on_error(
        self,
        error: Exception,
        item: disnake.ui.Item[disnake.ui.View],
        interaction: disnake.MessageInteraction,
    ) -> None:
        if isinstance(error, ViewException):
            await self.safe_edit(
                embed=disnake.Embed(
                    title=random.choice(ERRORS),
                    description=AnsiBuilder.from_string_to_ansi(error.message, Colors.RED, Styles.BOLD),
                    color=disnake.Color.red(),
                ),
            )
        else:
            await interaction.send(
                embed=disnake.Embed(
                    description="An error occurred while processing your request.",
                    color=disnake.Color.red(),
                ),
                ephemeral=True,
            )
        await interaction.client.on_error("view_error", ViewException(error, item, interaction))


class BaseModal(disnake.ui.Modal):
    _future: asyncio.Future[bool]
    _interaction: disnake.ModalInteraction

    async def on_timeout(self) -> None:
        self._future.set_result(True)

    async def wait(self) -> disnake.ModalInteraction:
        self._future = asyncio.shield(asyncio.get_running_loop().create_future())
        if await self._future:
            raise ViewTimeout()
        return self._interaction

    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        interaction._state._modal_store.remove_modal(interaction.author.id, interaction.custom_id)
        self._interaction = interaction
        self._future.set_result(False)

    async def on_error(self, error: Exception, interaction: disnake.ModalInteraction) -> None:
        if isinstance(error, ModalException):
            await interaction.send(
                embed=disnake.Embed(
                    title=random.choice(ERRORS),
                    description=AnsiBuilder.from_string_to_ansi(error.message, Colors.RED, Styles.BOLD),
                    color=disnake.Color.red(),
                ),
                ephemeral=True,
            )
        else:
            await interaction.send(
                embed=disnake.Embed(
                    title="An error occurred while processing your request.",
                    color=disnake.Color.red(),
                ),
                ephemeral=True,
            )
        await interaction.client.on_error("view_error", ModalException(error, interaction))

    @property
    def interaction(self) -> disnake.ModalInteraction:
        return self._interaction
