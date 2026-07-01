from discord import app_commands, Interaction, Member, Embed, Color
from typing import Optional

from ._group import moderation_group


@moderation_group.command(
    name="kick",
    description="ユーザーをキックする"
)
@app_commands.describe(
    user="キックするユーザー",
    reason="理由"
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.guild_only()
async def kick(
    interaction: Interaction,
    user: Member,
    reason: Optional[str] = None
):
    await interaction.guild.kick(
        user,
        reason=reason
    )

    await interaction.response.send_message(
        embed=Embed(
            description=f"{user.mention} をキックしました。",
            color=Color.orange()
        )
    )