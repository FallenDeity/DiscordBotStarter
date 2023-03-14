import disnake
from disnake.ext import commands

from src.core.views.ticket import (InsideTicketView, TicketCloseView,
                                   TicketCreateView)
from src.database.models import TicketSystem

from . import BaseCog

__all__: tuple[str, ...] = ("Tickets",)


class Tickets(BaseCog):
    """
    Ticket system commands
    """

    async def cog_load(self) -> None:
        self.bot.add_view(TicketCreateView(self.bot))
        self.bot.add_view(TicketCloseView(self.bot))
        self.bot.add_view(InsideTicketView(self.bot))

    @commands.slash_command(name="ticket", description="Ticket system commands")
    async def ticket(self, inter: disnake.ApplicationCommandInteraction) -> None:
        ...

    @ticket.sub_command(name="create", description="Create a ticket system")
    async def ticket_create(
        self,
        inter: disnake.ApplicationCommandInteraction,
        channel: disnake.TextChannel,
        archive_channel: disnake.TextChannel,
    ) -> None:
        """
        Create a ticket system

        Parameters
        ----------
        inter : disnake.ApplicationCommandInteraction
            The interaction
        channel : disnake.TextChannel
            The channel where the tickets will be created
        archive_channel : disnake.TextChannel
            The channel where the tickets will be archived
        """
        system = await self.bot.db.tickets.get_ticket_system(inter.guild.id)
        if system is not None:
            raise commands.BadArgument("A ticket system already exists")
        roles = [
            role.id for role in inter.guild.roles if role.permissions.manage_channels
        ]
        system = TicketSystem(inter.guild.id, channel.id, archive_channel.id, roles)
        await self.bot.db.tickets.create_ticket_system(system)
        await inter.edit_original_response(
            embed=self.bot.embeds.yes_embed(
                "Created ticket system", "The ticket system has been created"
            )
        )
        await archive_channel.set_permissions(
            inter.guild.default_role, read_messages=False
        )
        await channel.send(
            embed=self.bot.embeds.ticket_embed(inter.guild),
            view=TicketCreateView(self.bot),
        )
