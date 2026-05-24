import discord
from discord import app_commands
from discord.ext import commands

from bot.database.connection import get_pool


CARD_BASE_VALUE = 100
CLAIM_VALUE_INCREMENT = 3


class ClaimsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="claim", description="Adiciona uma carta ao seu inventario")
    @app_commands.describe(card_id="ID da carta exibido no /roll")
    async def claim(self, interaction: discord.Interaction, card_id: int) -> None:
        pool = get_pool()
        discord_id = interaction.user.id

        async with pool.acquire() as connection:
            async with connection.transaction():
                player = await connection.fetchrow(
                    """
                    SELECT
                        id,
                        nome,
                        jogo,
                        time_atual,
                        total_claims
                    FROM jogadores
                    WHERE id = $1;
                    """,
                    card_id,
                )

                if player is None:
                    await interaction.response.send_message(
                        "Nao encontrei uma carta com esse ID.",
                        ephemeral=True,
                    )
                    return

                await connection.execute(
                    """
                    INSERT INTO usuarios (discord_id)
                    VALUES ($1)
                    ON CONFLICT (discord_id) DO NOTHING;
                    """,
                    discord_id,
                )

                claimed = await connection.fetchrow(
                    """
                    INSERT INTO inventario (id_usuario, id_jogador)
                    VALUES ($1, $2)
                    ON CONFLICT (id_usuario, id_jogador) DO NOTHING
                    RETURNING id;
                    """,
                    discord_id,
                    player["id"],
                )

                if claimed is None:
                    await interaction.response.send_message(
                        f"Voce ja possui a carta de **{player['nome']}**.",
                        ephemeral=True,
                    )
                    return

                updated_player = await connection.fetchrow(
                    """
                    UPDATE jogadores
                    SET total_claims = total_claims + 1
                    WHERE id = $1
                    RETURNING
                        id,
                        nome,
                        jogo,
                        time_atual,
                        total_claims;
                    """,
                    player["id"],
                )

        card_value = CARD_BASE_VALUE + (
            updated_player["total_claims"] * CLAIM_VALUE_INCREMENT
        )

        embed = discord.Embed(
            title="Carta adicionada ao inventario",
            description=f"Voce deu claim em **{updated_player['nome']}**.",
            color=discord.Color.green(),
        )

        embed.add_field(
            name="Jogo",
            value=updated_player["jogo"],
            inline=True,
        )

        embed.add_field(
            name="Time atual",
            value=updated_player["time_atual"] or "Sem time informado",
            inline=True,
        )

        embed.add_field(
            name="Valor atual",
            value=f"{card_value} moedas",
            inline=True,
        )

        embed.add_field(
            name="Claims globais",
            value=str(updated_player["total_claims"]),
            inline=True,
        )

        embed.set_footer(text=f"ID da carta: {updated_player['id']}")

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ClaimsCog(bot))