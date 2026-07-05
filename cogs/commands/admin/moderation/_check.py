from discord import Interaction, Member


async def check_not_mod_permission(
    interaction: Interaction,
    member: Member
) -> bool:
    """
    権限が足りているか判断させて応答まで終わらせる関数

    処罰できるならFalseが返される
    """

    # サーバーオーナーは煽る
    if interaction.user.id == interaction.guild.owner_id:
        await interaction.response.send_message(
            "何やってんすかオーナーさん",
            ephemeral=True
        )
        return True

    # 対象がオーナーの場合は詰める
    if member.id == interaction.guild.owner_id:
        await interaction.response.send_message(
            "反逆罪？",
            ephemeral=True
        )
        return True

    # まぁ煽る
    if interaction.user.id == member.id:
        await interaction.response.send_message(
            "あなたを処罰しろって言うんですか？",
            ephemeral=True
        )
        return True

    # 管理者とかの権限を持つユーザーは拒否する
    if member.guild_permissions.administrator:
        await interaction.response.send_message(
            "管理者権限を持つユーザーのため操作できません",
            ephemeral=True
        )
        return True

    # 引かせる
    if interaction.guild.me.top_role < member.top_role:
        await interaction.response.send_message(
            "わ、私よりも強い位置にいるんですけど……",
            ephemeral=True
        )
        return True

    return False