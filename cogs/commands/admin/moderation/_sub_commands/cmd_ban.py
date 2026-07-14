from discord import app_commands, Interaction, Member, Embed, Color
from typing import Optional

from ...moderation._group import moderation_group
from ._check import check_not_mod_permission


@moderation_group.command(
    name="ban",
    description="ユーザーをBANする"
)
@app_commands.describe(
    user="BANするユーザー",
    reason="理由",
    delete_message_seconds="削除するメッセージの期間"
)
@app_commands.choices(
    delete_message_seconds=[
        app_commands.Choice(name="削除しない", value=0),

        app_commands.Choice(name="1時間", value=3600),
        app_commands.Choice(name="2時間", value=7200),
        app_commands.Choice(name="4時間", value=14400),
        app_commands.Choice(name="6時間", value=21600),
        app_commands.Choice(name="8時間", value=28800),
        app_commands.Choice(name="10時間", value=36000),
        app_commands.Choice(name="12時間", value=43200),
        app_commands.Choice(name="14時間", value=50400),
        app_commands.Choice(name="16時間", value=57600),
        app_commands.Choice(name="18時間", value=64800),
        app_commands.Choice(name="20時間", value=72000),
        app_commands.Choice(name="22時間", value=79200),

        app_commands.Choice(name="1日", value=86400),
        app_commands.Choice(name="2日", value=172800),
        app_commands.Choice(name="3日", value=259200),
        app_commands.Choice(name="4日", value=345600),
        app_commands.Choice(name="5日", value=432000),
        app_commands.Choice(name="6日", value=518400),
        app_commands.Choice(name="7日", value=604800),
    ]
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.guild_only()
async def ban(
    interaction: Interaction,
    user: Member,
    delete_message_seconds: Optional[int] = 0,
    reason: Optional[str] = None
):
    if await check_not_mod_permission(interaction, user):
        return

    try:
        await interaction.guild.ban(
            user,
            reason=reason,
            delete_message_seconds=delete_message_seconds
        )

        await interaction.response.send_message(
            embed=(
                Embed(
                    description=f"{user.mention} をBANしました。",
                    color=Color.red()
                )
                .add_field(
                    name="理由",
                    value=f"```{reason}```" if reason else "なし",
                    inline=True
                )
            )
        )

    except Exception as e:
        print(f"ban Error: {e}")