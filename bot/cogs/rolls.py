import discord
from discord import app_commands
from discord.ext import commands

from bot.database.connection import get_pool


CARD_BASE_VALUE = 100
CLAIM_VALUE_INCREMENT = 3


class RollsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="roll", description="Sorteia uma carta de jogador")
    async def roll(self, interaction: discord.Interaction) -> None:
        pool = get_pool()

        async with pool.acquire() as connection:
            player = await connection.fetchrow(
                """
                SELECT
                    id,
                    nome,
                    jogo,
                    time_atual,
                    imagem_url,
                    total_claims
                FROM jogadores
                WHERE jogo = 'valorant'
                ORDER BY RANDOM()
                LIMIT 1;
                """
            )

        if player is None:
            await interaction.response.send_message(
                "Nenhum jogador cadastrado ainda.",
                ephemeral=True,
            )
            return

        card_value = CARD_BASE_VALUE + (player["total_claims"] * CLAIM_VALUE_INCREMENT)

        embed = discord.Embed(
            title=player["nome"],
            description=f"Carta de jogador profissional de {player['jogo']}.",
            color=discord.Color.red(),
        )

        embed.add_field(
            name="Time atual",
            value=player["time_atual"] or "Sem time informado",
            inline=True,
        )

        embed.add_field(
            name="Valor",
            value=f"{card_value} moedas",
            inline=True,
        )

        embed.add_field(
            name="Claims globais",
            value=str(player["total_claims"]),
            inline=True,
        )

        embed.set_footer(text=f"ID da carta: {player['id']}")

        if player["imagem_url"]:
            embed.set_image(url=player["imagem_url"])

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RollsCog(bot))