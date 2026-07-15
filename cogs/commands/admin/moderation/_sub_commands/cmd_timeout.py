from discord import app_commands, Interaction, Member, Embed, Color
from datetime import timedelta
from typing import Optional

from .._group import moderation_group
from ._check import check_not_mod_permission


@moderation_group.command(
    name="timeout",
    description="ユーザーをタイムアウトする"
)
@app_commands.describe(
    user="タイムアウトするユーザー",
    duration="タイムアウト時間",
    reason="理由"
)
@app_commands.choices(
    duration=[
        app_commands.Choice(name="5分", value=300),
        app_commands.Choice(name="10分", value=600),
        app_commands.Choice(name="30分", value=1800),
        app_commands.Choice(name="1時間", value=3600),
        app_commands.Choice(name="6時間", value=21600),
        app_commands.Choice(name="12時間", value=43200),
        app_commands.Choice(name="18時間", value=64800),

        app_commands.Choice(name="1日", value=86400),
        app_commands.Choice(name="2日", value=172800),
        app_commands.Choice(name="3日", value=259200),
        app_commands.Choice(name="5日", value=432000),
        app_commands.Choice(name="7日", value=604800),
        app_commands.Choice(name="10日", value=864000),
        app_commands.Choice(name="14日", value=1209600),
        app_commands.Choice(name="15日", value=1296000),
        app_commands.Choice(name="20日", value=1728000),
        app_commands.Choice(name="25日", value=2160000),
        app_commands.Choice(name="約28日", value=2419000),
    ]
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.guild_only()
async def timeout(
    interaction: Interaction,
    user: Member,
    duration: app_commands.Choice[int],
    reason: Optional[str] = None
):
    if await check_not_mod_permission(interaction, user):
        return

    if user.guild_permissions.moderate_members:
        await interaction.response.send_message("タイムアウトできる権限を持っているユーザーはタイムアウトできません", ephemeral=True)
        return

    try:
        await user.timeout(
            timedelta(seconds=duration.value),
            reason=reason
        )

        user = await interaction.guild.fetch_member(user.id)

        unix_ts = int(user.timed_out_until.timestamp())

        await interaction.response.send_message(
            embed=(
                Embed(
                    description=f"{user.mention} をタイムアウトしました。",
                    color=Color.orange()
                )
                .add_field(
                    name="理由",
                    value=f"```{reason}```" if reason else "なし",
                    inline=True
                )
                .add_field(
                    name="解除予定",
                    value=f"<t:{unix_ts}:F> (<t:{unix_ts}:R>)",
                    inline=True
                )
            )
        )

    except Exception as e:
        print(f"timeout Error: {e}")