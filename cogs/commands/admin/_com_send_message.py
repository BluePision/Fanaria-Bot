import asyncio
from discord import app_commands, Interaction, Member, Embed, Color, NotFound
from typing import Optional

from cogs import BotLog
from ._group import admin_group


@admin_group.command(
    name="send_message",
    description="FanariaBotとしてメッセージを送信する"
)
@app_commands.describe(
    message="送信させたい内容",
    reply_message_id="返信先メッセージID",
    reply_mention="返信する場合相手にメンションするかどうか(デフォルトはしない)",
    input_time="入力時間"
)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.guild_only()
async def send_message(
    interaction: Interaction,
    message: str,
    reply_message_id: str = None,
    reply_mention: bool = False,
    input_time: float = None
):
    await interaction.response.defer(ephemeral=True)

    if not message:
        return

    send_channel = interaction.client.get_channel(interaction.channel.id)

    if input_time is None:
        input_time = 1 + (len(message) * 0.1)

    if reply_mention is None:
        reply_mention = False

    async with send_channel.typing():
        await asyncio.sleep(input_time)

    formatted_message = (
        message
        .replace("[Server]", interaction.guild.name)
        .replace("\\n", "\n")
    )

    if reply_message_id:
        try:
            target_message = await send_channel.fetch_message(int(reply_message_id))
            sent_message = await target_message.reply(
                content=formatted_message,
                mention_author=reply_mention
            )

        # 見つからなければ普通に送信する
        except NotFound:
            sent_message = await send_channel.send(formatted_message)

    else:
        sent_message = await send_channel.send(formatted_message)

    await interaction.followup.send("メッセージを送信しました", ephemeral=True)

    botlog: Optional[BotLog] = interaction.client.get_cog("BotLog")
    await botlog.send(embed=(
        Embed(
            title="SendMessage",
            description=message,
            color=Color.blue()
        )
        .add_field(
            name="送信者",
            value=interaction.user.mention,
            inline=True
        )
        .add_field(
            name="メッセージ",
            value=sent_message.jump_url,
            inline=True
        )
    ))