from discord import app_commands, Interaction, Member, User, Embed, Color
from ._group import user_group

@user_group.command(
    name="banner",
    description="ユーザーのバナーを表示"
)
@app_commands.describe(
    user="表示するユーザー（省略可能）",
    banner_type="表示するバナーの種類（省略可能）"
)
@app_commands.choices(
    banner_type=[
        app_commands.Choice(name="メインプロフィール", value="global"),
        app_commands.Choice(name="サーバープロフィール", value="server")
    ]
)
async def banner(
    interaction: Interaction,
    banner_type: app_commands.Choice[str] = None,
    user: Member | User = None
):
    target_user = user or interaction.user
    banner_type_value = banner_type.value if banner_type else "global"

    if interaction.guild is None and banner_type_value == "server":
        await interaction.response.send_message("サーバープロフィールはDMでは表示できません", ephemeral=True)
        return

    if banner_type_value == "global":
        if target_user.banner is None:
            target_user = await interaction.client.fetch_user(target_user.id)

        banner_url = target_user.banner.url if target_user.banner else None
        banner_title = f"メインプロフィールのバナー"

    elif banner_type_value == "server":
        if isinstance(target_user, User):
            target_user = await interaction.guild.fetch_member(target_user.id)

        banner_url = target_user.guild_banner.url if target_user.guild_banner else None
        banner_title = f"サーバープロフィールのバナー"

    else:
        banner_url = None
        banner_title = "バナーがありません"

    embed = Embed(
        title=banner_title,
        description=f"<@{target_user.id}>のバナー",
        color=Color.blue()
    )

    if banner_url:
        embed.set_image(url=banner_url)
    else:
        embed.description = "そのバナーはありません"

    await interaction.response.send_message(embed=embed)