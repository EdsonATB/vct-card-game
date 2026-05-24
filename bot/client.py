import discord
from discord.ext import commands
from bot.config import Settings
from bot.database.connection import close_pool, create_pool


class VCTBot(commands.Bot):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

        intents = discord.Intents.default()

        super().__init__(
            command_prefix=settings.command_prefix,
            intents=intents,
        )

    async def setup_hook(self) -> None:
        await self.load_extension("bot.cogs.general")
        await self.load_extension("bot.cogs.rolls")

        if self.settings.sync_commands:
            synced = await self.tree.sync()
            print(f"Sincronizados {len(synced)} comandos.")

    async def on_ready(self) -> None:
        print(f"Bot {self.user} esta rodando!.")

    
    async def setup_hook(self) -> None:
        await create_pool(self.settings.database_url)

        await self.load_extension("bot.cogs.general")
        await self.load_extension("bot.cogs.rolls")
        await self.load_extension("bot.cogs.claims")
        await self.load_extension("bot.cogs.inventory")
        await self.load_extension("bot.cogs.players")

        if self.settings.sync_commands:
            synced = await self.tree.sync()
            print(f"Sincronizados {len(synced)} comandos.")

    
    async def close(self) -> None:
        await close_pool()
        await super().close()
