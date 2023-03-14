import asyncio
import typing

import disnake

from src.core.errors import ViewException, ViewTimeout

__all__: tuple[str, ...] = (
    "BaseView",
    "BaseModal",
)
# pyright: reportUnknownVariableType=false


class BaseView(disnake.ui.View):
    interaction: disnake.MessageInteraction
    message: disnake.Message

    def __init__(
        self,
        user: disnake.Member | disnake.User = None,
        *,
        timeout: float | None = 180.0
    ):
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
            await self.interaction.edit_original_response(**kwargs)
        except disnake.NotFound:
            return
        except Exception as e:
            try:
                await self.message.edit(**kwargs)
            except (disnake.NotFound, disnake.HTTPException):
                await self.interaction.response.edit_message(**kwargs)
            except disnake.InteractionResponded:
                await self.interaction.client.on_error("view_error", e)

    def _disable(self) -> None:
        for child in self.children:
            if isinstance(child, disnake.ui.Button):
                child.disabled = True
            elif isinstance(child, disnake.ui.Select):
                child.disabled = True

    async def on_error(
        self,
        error: Exception,
        item: disnake.ui.Item[disnake.ui.View],
        interaction: disnake.MessageInteraction,
    ) -> None:
        await interaction.edit_original_response(
            content=None,
            embed=disnake.Embed(
                description="An error occurred while processing your request.",
                color=disnake.Color.red(),
            ),
            view=None,
            attachments=[],
        )
        await interaction.client.on_error(
            "view_error", ViewException(error, item, interaction)
        )
        await self.on_timeout()


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
