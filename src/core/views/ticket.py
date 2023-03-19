import asyncio
import io
import typing as t

import chat_exporter
import disnake

from . import BaseView

if t.TYPE_CHECKING:
    from src import TemplateBot


class TicketCloseView(BaseView):
    def __init__(self, bot: "TemplateBot") -> None:
        super().__init__(timeout=None)
        self.bot = bot

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        await interaction.response.defer()
        self.interaction = interaction
        if isinstance(interaction.user, disnake.Member):
            if interaction.user.guild_permissions.manage_guild:
                return True

    @disnake.ui.button(
        emoji="🔓",
        label="Re-open",
        style=disnake.ButtonStyle.green,
        custom_id="persistent_view:reopen",
    )
    async def reopen_ticket(self, _: disnake.Button, interaction: disnake.MessageInteraction):
        await interaction.message.edit(view=None)
        for key in interaction.channel.overwrites:
            if isinstance(key, disnake.Member):
                await interaction.channel.set_permissions(key, read_messages=True, send_messages=True)
        view = InsideTicketView(self.bot)
        embed = disnake.Embed(
            description=f"<:tick:1001136782508826777> The ticket has been re-opened by {interaction.user.mention}.\n\n"
            "Click `🔒` to close the ticket.",
            color=disnake.Color.green(),
        )
        await interaction.edit_original_response(embed=embed, view=view)
        self.stop()

    @disnake.ui.button(
        emoji="📄",
        label="Transcript",
        style=disnake.ButtonStyle.gray,
        custom_id="persistent_view:transcript",
    )
    async def transcript(self, button: disnake.Button, interaction: disnake.MessageInteraction):
        system = await self.bot.db.tickets.get_ticket_system(interaction.guild.id)
        button.disabled = True
        await interaction.edit_original_response(view=self)
        archive_channel = self.bot.get_channel(system.archive_channel_id) or await self.bot.fetch_channel(
            system.archive_channel_id
        )
        embed = disnake.Embed(
            description=f"Preparing channel transcript and sending it to {archive_channel.mention}."
            f" This may take a few seconds...",
            color=disnake.Color.blue(),
        )
        web_msg = await interaction.channel.send(embed=embed)
        transcript = await chat_exporter.export(interaction.channel, tz_info="UTC")
        transcript_file = disnake.File(io.BytesIO(transcript.encode()), filename=f"{interaction.channel.name}.html")
        await archive_channel.send(f"{interaction.channel.name}", file=transcript_file)
        embed = disnake.Embed(description="✅ Done!", color=disnake.Color.green())
        await web_msg.edit(embed=embed)

    @disnake.ui.button(
        emoji="🗑️",
        label="Delete",
        style=disnake.ButtonStyle.red,
        custom_id="persistent_view:delete",
    )
    async def delete_ticket(self, _: disnake.Button, interaction: disnake.MessageInteraction):
        await interaction.message.edit(view=None)
        embed = disnake.Embed(description="Deleting the ticket in 5 seconds...", color=disnake.Color.red())
        await interaction.send(embed=embed, ephemeral=True)
        await asyncio.sleep(5)
        await interaction.channel.delete()
        self.stop()

    async def on_error(
        self,
        error: Exception,
        item: disnake.ui.Item[disnake.ui.View],
        interaction: disnake.MessageInteraction,
    ) -> None:
        await interaction.send(embed=self.bot.embeds.no_embed("Error", str(error)), ephemeral=True)
        tb = __import__("traceback").format_exception(type(error), error, error.__traceback__)
        self.bot.logger.error("".join(tb))
        return


class InsideTicketView(BaseView):
    def __init__(self, bot: "TemplateBot") -> None:
        super().__init__(timeout=None)
        self.bot = bot

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        await interaction.response.defer()
        self.interaction = interaction
        if isinstance(interaction.user, disnake.Member):
            if interaction.user.guild_permissions.manage_guild:
                return True

    @disnake.ui.button(
        emoji="🔒",
        label="Close",
        style=disnake.ButtonStyle.red,
        custom_id="persistent_view:close",
    )
    async def close_ticket(self, button: disnake.Button, interaction: disnake.MessageInteraction):
        button.disabled = True
        await interaction.edit_original_response(view=self)
        for key in interaction.channel.overwrites:
            if isinstance(key, disnake.Member):
                await interaction.channel.set_permissions(key, read_messages=False, send_messages=False)
        view = TicketCloseView(self.bot)
        embed = disnake.Embed(
            description=f"<:tick:1001136782508826777> The ticket has been closed by {interaction.user.mention}.\n\n"
            "Click `🔓` to reopen the ticket.\n"
            "Click `📄` to save the transcript.\n"
            "Click `🗑️` to delete the ticket.",
            color=disnake.Color.blue(),
        )
        await interaction.send(embed=embed, view=view)
        self.stop()

    async def on_error(
        self,
        error: Exception,
        item: disnake.ui.Item[disnake.ui.View],
        interaction: disnake.MessageInteraction,
    ) -> None:
        await interaction.send(embed=self.bot.embeds.no_embed("Error", str(error)), ephemeral=True)
        tb = __import__("traceback").format_exception(type(error), error, error.__traceback__)
        self.bot.logger.error("".join(tb))
        return


class TicketCreateView(BaseView):
    def __init__(self, bot: "TemplateBot") -> None:
        super().__init__(timeout=None)
        self.bot = bot

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        await interaction.response.defer()
        self.interaction = interaction
        if isinstance(interaction.user, disnake.Member):
            return True

    @disnake.ui.button(
        label="Create Ticket",
        style=disnake.ButtonStyle.green,
        custom_id="persistent_view:create",
        emoji="🎫",
    )
    async def create_ticket(self, _: disnake.Button, interaction: disnake.MessageInteraction):
        system = await self.bot.db.tickets.get_ticket_system(interaction.guild.id)
        for text_channel in interaction.guild.text_channels:
            if interaction.user.name.lower() in text_channel.name:
                embed = disnake.Embed(
                    description=f"<:no:1001136828738453514> You already have an open ticket."
                    f" Please head towards {text_channel.mention}.",
                    color=disnake.Color.red(),
                )
                return await interaction.send(embed=embed, ephemeral=True)
        manage_roles = [
            role for role in interaction.guild.roles if role.permissions.manage_roles or role.id in system.roles
        ]
        overwrites = {
            interaction.guild.default_role: disnake.PermissionOverwrite(read_messages=False),
            interaction.user: disnake.PermissionOverwrite(read_messages=True, send_messages=True),
            **{role: disnake.PermissionOverwrite(read_messages=True, send_messages=True) for role in manage_roles},
        }
        channel = await interaction.guild.create_text_channel(
            f"{str(interaction.user)}",
            category=interaction.channel.category,
            overwrites=overwrites,
        )
        await asyncio.sleep(2)
        a_embed = disnake.Embed(
            description=f"<:tick:1001136782508826777> Created ticket. Please head towards {channel.mention}.",
            color=disnake.Color.green(),
        )
        await interaction.send(embed=a_embed, ephemeral=True)
        create_time = disnake.utils.format_dt(channel.created_at, style="F")
        view = InsideTicketView(self.bot)
        embed = disnake.Embed(title="Support Ticket", color=disnake.Color.blue())
        embed.set_thumbnail(url=f"{interaction.user.display_avatar}")
        embed.add_field(name="Time Opened", value=f"{create_time}")
        embed.add_field(name="Opened For", value=str(interaction.user))
        embed.set_footer(text="Please be patient while a staff member gets to this ticket.")
        await asyncio.sleep(2)
        message = await channel.send(f"{interaction.user.mention}", embed=embed, view=view)
        await message.pin()

    @disnake.ui.button(
        label="Cancel",
        style=disnake.ButtonStyle.red,
        custom_id="persistent_view:cancel",
        emoji="🗑️",
    )
    async def cancel_ticket(self, _: disnake.Button, interaction: disnake.MessageInteraction) -> None:
        await self.bot.db.tickets.delete_ticket_system(interaction.guild.id)
        embed = disnake.Embed(
            description="✅ Successfully deleted the ticket system.",
            color=disnake.Color.green(),
        )
        await interaction.send(embed=embed, ephemeral=True)
        await interaction.delete_original_response()
        self.stop()

    async def on_error(
        self,
        error: Exception,
        item: disnake.ui.Item[disnake.ui.View],
        interaction: disnake.MessageInteraction,
    ) -> None:
        await interaction.send(embed=self.bot.embeds.no_embed("Error", str(error)), ephemeral=True)
        tb = __import__("traceback").format_exception(type(error), error, error.__traceback__)
        self.bot.logger.error("".join(tb))
        return
