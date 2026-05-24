import math

import discord
from discord import app_commands
from discord.ext import commands

from bot.database.connection import get_pool


CARD_BASE_VALUE = 100
CLAIM_VALUE_INCREMENT = 5
PLAYERS_PER_PAGE = 10


class PlayersView(discord.ui.View):
    def __init__(self, players: list[dict]) -> None:
        super().__init__(timeout=120)

        self.players = players
        self.current_page = 0
        self.total_pages = max(1, math.ceil(len(players) / PLAYERS_PER_PAGE))

        self._update_buttons()

    def build_embed(self) -> discord.Embed:
        start = self.current_page * PLAYERS_PER_PAGE
        end = start + PLAYERS_PER_PAGE
        page_players = self.players[start:end]

        embed = discord.Embed(
            title="Jogadores cadastrados",
            description=(
                f"Total de jogadores: **{len(self.players)}**\n"
                "Ordenado por maior valor"
            ),
            color=discord.Color.gold(),
        )

        for index, player in enumerate(page_players, start=start + 1):
            team = player["time_atual"] or "Sem time informado"
            region = player["regiao"] or "Sem regiao"

            embed.add_field(
                name=f"{index}. {player['nome']} | ID {player['id']}",
                value=(
                    f"Time: {team}\n"
                    f"Regiao: {region}\n"
                    f"Valor: {player['card_value']} moedas\n"
                    f"Claims globais: {player['total_claims']}"
                ),
                inline=False,
            )

        embed.set_footer(
            text=f"Pagina {self.current_page + 1}/{self.total_pages}"
        )

        return embed

    def _update_buttons(self) -> None:
        self.previous_page.disabled = self.current_page <= 0
        self.next_page.disabled = self.current_page >= self.total_pages - 1

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.secondary)
    async def previous_page(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        self.current_page -= 1
        self._update_buttons()

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self,
        )

    @discord.ui.button(label="Proxima", style=discord.ButtonStyle.secondary)
    async def next_page(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        self.current_page += 1
        self._update_buttons()

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self,
        )


class PlayersCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="players",
        description="Lista os jogadores cadastrados por valor",
    )
    async def players(self, interaction: discord.Interaction) -> None:
        pool = get_pool()

        async with pool.acquire() as connection:
            rows = await connection.fetch(
                """
                SELECT
                    id,
                    nome,
                    jogo,
                    time_atual,
                    total_claims,
                    regiao
                FROM jogadores
                WHERE jogo = 'valorant'
                ORDER BY total_claims DESC, nome ASC;
                """
            )

        if not rows:
            await interaction.response.send_message(
                "Nenhum jogador cadastrado ainda.",
                ephemeral=True,
            )
            return

        players = []

        for row in rows:
            card_value = CARD_BASE_VALUE + (
                row["total_claims"] * CLAIM_VALUE_INCREMENT
            )

            players.append(
                {
                    "id": row["id"],
                    "nome": row["nome"],
                    "jogo": row["jogo"],
                    "time_atual": row["time_atual"],
                    "total_claims": row["total_claims"],
                    "regiao": row["regiao"],
                    "card_value": card_value,
                }
            )

        view = PlayersView(players)
        await interaction.response.send_message(
            embed=view.build_embed(),
            view=view,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PlayersCog(bot))