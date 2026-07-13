import asyncio
import random
from discord import app_commands, Interaction, User, Member, Embed, Color, NotFound
from typing import Optional

from ._group import tool_group


hands = {
    "✊": "グー",
    "✌️": "チョキ",
    "🖐️": "パー"
}

@tool_group.command(
    name="predict_janken",
    description="じゃんけんの次の手を予想する"
)
@app_commands.describe(
    user="予想する対象（省略可能）"
)
@app_commands.guild_only()
async def predict_janken(
    interaction: Interaction,
    user: User | None = None
):
    embed = Embed(color=Color.blue())

    if user is not None:
        embed.description = f"{user.mention} さんが出しそうな手は……"

    else:
        embed.description = "次の手は……"

    hand_emoji = random.choice(list(hands.keys()))
    hand_name = hands[hand_emoji]

    embed.description += f"\n\n## ||{hand_name} {hand_emoji}||！"

    await interaction.response.send_message(embed=embed)