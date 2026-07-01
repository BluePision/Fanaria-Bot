from discord import app_commands, Interaction, Member, User, Embed, Color
from ._group import user_group

@user_group.command(
    name="avatar_icon",
    description="ユーザーのアイコンを表示"
)
@app_commands.describe(
    user="表示するユーザー（省略可能）",
    avatar_type="表示するアバターの種類（省略可能）"
)
@app_commands.choices(
    avatar_type=[
        app_commands.Choice(name="メインプロフィール", value="global"),
        app_commands.Choice(name="サーバープロフィール", value="server")
    ]
)
@app_commands.guild_only()
async def avatar(
    interaction: Interaction,
    avatar_type: app_commands.Choice[str] = None,
    user: Member | User = None
):
    target_user = user or interaction.user
    avatar_type_value = avatar_type.value if avatar_type else "global"

    if interaction.guild is None and avatar_type_value == "server":
        await interaction.response.send_message("サーバープロフィールはDMでは表示できません", ephemeral=True)
        return

    if avatar_type_value == "global":
        avatar_url = target_user.avatar.url if target_user.avatar else None
        avatar_title = f"メインプロフィールのアイコン"

    elif avatar_type_value == "server":
        if isinstance(target_user, User):
            target_user = await interaction.guild.fetch_member(target_user.id)

        avatar_url = target_user.guild_avatar.url if target_user.guild_avatar else None
        avatar_title = f"サーバープロフィールのアイコン"

    else:
        avatar_url = None
        avatar_title = "アイコンはありません"

    embed = Embed(
        title=avatar_title,
        description=f"<@{target_user.id}>のアイコン",
        color=Color.blue()
    )

    if avatar_url:
        embed.set_image(url=avatar_url)
    else:
        embed.description = "そのアイコンはありません"

    await interaction.response.send_message(embed=embed)