import discord
from discord.ext import commands
from discord import app_commands

from datetime import datetime, timedelta, timezone

from configs.main import OwnerGuildID

class SelfTimeOut(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.autocomplete()
    async def _timeout_minute_autocomplete(self, interaction: discord.Interaction, current: str):
        """0～59分を選択できるオートコンプリート"""
        input_text = (current or "").lower()
        all_choices = [
            app_commands.Choice(name=f"{i}分", value=i * 60)
            for i in range(60)
        ]
        filtered = [c for c in all_choices if input_text in c.name.lower()]
        return filtered[:25]

    @app_commands.autocomplete()
    async def _timeout_second_autocomplete(self, interaction: discord.Interaction, current: str):
        """0～59秒を選択できるオートコンプリート"""
        input_text = (current or "").lower()
        all_choices = [
            app_commands.Choice(name=f"{i}秒", value=i)
            for i in range(60)
        ]
        filtered = [c for c in all_choices if input_text in c.name.lower()]
        return filtered[:25]

    # スラッシュコマンド
    @app_commands.command(
        name="self_timeout",
        description="セルフタイムアウトを実行します"
    )
    @app_commands.describe(
        day="タイムアウトの期間(日)",
        hour="タイムアウトの期間(時間)",
        minute="タイムアウトの期間(分)",
        second="タイムアウトの期間(秒)"
    )
    @app_commands.choices(
        day=[app_commands.Choice(name=f"{i}日", value=i * 86400) for i in range(0, 8)],
        hour=[app_commands.Choice(name=f"{i}時間", value=i * 3600) for i in range(0, 24)],
        minute=[app_commands.Choice(name=f"{i}分", value=i * 60) for i in range(0, 60, 5)],
        second=[app_commands.Choice(name=f"{i}秒", value=i) for i in range(0, 60, 5)]
    )
    @app_commands.guilds(discord.Object(id=OwnerGuildID))
    @app_commands.guild_only()
    async def selftimeout(
        self,
        interaction: discord.Interaction,
        day: int = 0,
        hour: int = 3600,
        minute: int = 0,
        second: int = 0
    ):
        # サーバーの確認
        if OwnerGuildID is not None and interaction.guild_id != OwnerGuildID:
            await interaction.response.send_message("このBotは特定サーバー専用です", ephemeral=True)
            return

        # interaction.user が Member か確認
        member = interaction.user if isinstance(interaction.user, discord.Member) else interaction.guild.get_member(interaction.user.id)
        if member is None:
            await interaction.response.send_message("メンバー情報が取得できませんでした", ephemeral=True)
            return

        # サーバーオーナーは正気か問う
        if member.id == interaction.guild.owner_id:
            await interaction.response.send_message("オーナーさん！？気を確かに！！あなたはオーナーですよ！？", ephemeral=True)
            return

        # 管理者とかの権限を持つユーザーは拒否する
        if member.guild_permissions.administrator or member.guild_permissions.moderate_members:
            await interaction.response.send_message("管理者権限を持つユーザーはセルフタイムアウトできません", ephemeral=True)
            return

        final_seconds = day + hour + minute + second
        if final_seconds <= 0:
            await interaction.response.send_message("タイムアウト時間は 1 秒以上にしてください", ephemeral=True)
            return

        # 時間を分解して見やすくする
        days, remainder = divmod(final_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        embed_time = f"{days}日{hours}時間{minutes}分{seconds}秒"

        try:
            until = datetime.now(timezone.utc) + timedelta(seconds=final_seconds)
            await member.timeout(until, reason="セルフタイムアウト")

            embed = discord.Embed(
                title="セルフタイムアウト",
                description=f"{interaction.user.mention}さんが自ら自身を追放しました",
                color=discord.Color.blue()
            )
            embed.add_field(name="期間", value=embed_time, inline=False)
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="失敗しました",
                description=f"```{e}```",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

# Cogを登録
async def setup(bot: commands.Bot):
    await bot.add_cog(SelfTimeOut(bot))