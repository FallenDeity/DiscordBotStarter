from src.database.models import TicketSystem

from . import Table

__all__: tuple[str, ...] = ("Tickets",)


class Tickets(Table):
    async def setup(self) -> None:
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS tickets "
            "(guild_id BIGINT,"
            " channel_id BIGINT,"
            " archive_channel_id BIGINT,"
            " roles BIGINT [] DEFAULT '{}',"
            " PRIMARY KEY (guild_id))"
        )

    async def get_ticket_system(self, guild_id: int) -> TicketSystem | None:
        data = await self.db.fetchrow("SELECT * FROM tickets WHERE guild_id = $1", guild_id)
        if data is None:
            return None
        return TicketSystem(*data)

    async def create_ticket_system(self, data: TicketSystem) -> None:
        await self.db.execute(
            "INSERT INTO tickets (guild_id, channel_id, archive_channel_id, roles) " "VALUES ($1, $2, $3, $4)",
            data.guild_id,
            data.channel_id,
            data.archive_channel_id,
            data.roles,
        )

    async def update_ticket_system(self, data: TicketSystem) -> None:
        await self.db.execute(
            "UPDATE tickets SET channel_id = $1, archive_channel_id = $2, roles = $3 WHERE guild_id = $4",
            data.channel_id,
            data.archive_channel_id,
            data.roles,
            data.guild_id,
        )

    async def delete_ticket_system(self, guild_id: int) -> None:
        await self.db.execute("DELETE FROM tickets WHERE guild_id = $1", guild_id)
