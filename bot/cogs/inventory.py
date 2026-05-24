import math

import discord
from discord import app_commands
from discord.ext import commands

from bot.database.connection import get_pool


CARD_BASE_VALUE = 100
CLAIM_VALUE_INCREMENT = 5
CARDS_PER_PAGE = 5


class InventoryView(discord.ui.View):
    def __init__(
        self,
        interaction_user_id: int,
        cards: list,
        total_value: int,
        order_label: str,
    ) -> None:
        super().__init__(timeout=120)

        self.interaction_user_id = interaction_user_id
        self.cards = cards
        self.total_value = total_value
        self.order_label = order_label
        self.current_page = 0
        self.total_pages = max(1, math.ceil(len(cards) / CARDS_PER_PAGE))

        self._update_buttons()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.interaction_user_id:
            await interaction.response.send_message(
                "Esse inventario nao e seu.",
                ephemeral=True,
            )
            return False

        return True

    def build_embed(self, display_name: str) -> discord.Embed:
        start = self.current_page * CARDS_PER_PAGE
        end = start + CARDS_PER_PAGE
        page_cards = self.cards[start:end]

        embed = discord.Embed(
            title=f"Inventario de {display_name}",
            description=(
                f"Cartas: **{len(self.cards)}**\n"
                f"Valor total: **{self.total_value} moedas**\n"
                f"Ordenacao: **{self.order_label}**"
            ),
            color=discord.Color.blue(),
        )

        for index, card in enumerate(page_cards, start=start + 1):
            team = card["time_atual"] or "Sem time informado"

            embed.add_field(
                name=f"{index}. {card['nome']} | ID {card['id']}",
                value=(
                    f"Jogo: {card['jogo']}\n"
                    f"Time: {team}\n"
                    f"Valor: {card['card_value']} moedas\n"
                    f"Claims globais: {card['total_claims']}"
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

        embed = self.build_embed(interaction.user.display_name)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Proxima", style=discord.ButtonStyle.secondary)
    async def next_page(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        self.current_page += 1
        self._update_buttons()

        embed = self.build_embed(interaction.user.display_name)
        await interaction.response.edit_message(embed=embed, view=self)


class InventoryCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="inventario", description="Mostra suas cartas")
    @app_commands.describe(
        ordenar_por="Escolha como ordenar seu inventario"
    )
    @app_commands.choices(
        ordenar_por=[
            app_commands.Choice(name="Mais recentes", value="recentes"),
            app_commands.Choice(name="Maior valor", value="valor"),
            app_commands.Choice(name="Nome", value="nome"),
        ]
    )
    async def inventory(
        self,
        interaction: discord.Interaction,
        ordenar_por: app_commands.Choice[str] | None = None,
    ) -> None:
        pool = get_pool()
        discord_id = interaction.user.id
        selected_order = ordenar_por.value if ordenar_por else "recentes"

        order_sql = {
            "recentes": "inventario.data_claim DESC",
            "valor": "jogadores.total_claims DESC, jogadores.nome ASC",
            "nome": "jogadores.nome ASC",
        }[selected_order]

        order_label = {
            "recentes": "Mais recentes",
            "valor": "Maior valor",
            "nome": "Nome",
        }[selected_order]

        query = f"""
            SELECT
                jogadores.id,
                jogadores.nome,
                jogadores.jogo,
                jogadores.time_atual,
                jogadores.total_claims,
                inventario.data_claim
            FROM inventario
            INNER JOIN jogadores
                ON jogadores.id = inventario.id_jogador
            WHERE inventario.id_usuario = $1
            ORDER BY {order_sql};
        """

        async with pool.acquire() as connection:
            rows = await connection.fetch(query, discord_id)

        if not rows:
            await interaction.response.send_message(
                "Voce ainda nao possui cartas. Use `/roll` para sortear uma carta.",
                ephemeral=True,
            )
            return

        cards = []
        total_value = 0

        for row in rows:
            card_value = CARD_BASE_VALUE + (
                row["total_claims"] * CLAIM_VALUE_INCREMENT
            )
            total_value += card_value

            cards.append(
                {
                    "id": row["id"],
                    "nome": row["nome"],
                    "jogo": row["jogo"],
                    "time_atual": row["time_atual"],
                    "total_claims": row["total_claims"],
                    "data_claim": row["data_claim"],
                    "card_value": card_value,
                }
            )

        view = InventoryView(
            interaction_user_id=discord_id,
            cards=cards,
            total_value=total_value,
            order_label=order_label,
        )

        embed = view.build_embed(interaction.user.display_name)

        await interaction.response.send_message(
            embed=embed,
            view=view,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(InventoryCog(bot))