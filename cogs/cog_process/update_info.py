import asyncio
from discord import Interaction, Message, Guild, Member, TextChannel, Embed, Color, ui, components, ButtonStyle, HTTPException, AllowedMentions
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from typing import Optional

from .botlog import BotLog

from configs.main import OwnerGuildID, InfoChannelID

JST = timezone(timedelta(hours=9))

class UpdateInfo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self._cache_channel: Optional[TextChannel] = None
        self._cache_message: Optional[Message] = None

        self.guild: Optional[Guild] = None
        self.owner: Optional[Member] = None
        self.member_count: int = 0
        self.humans: int = 0
        self.bots: int = 0
        self.boost_count: int = 0
        self.boost_level: int = 0

    async def initialize(self) -> None:
        """
        起動直後に呼ぶ初期化処理。
        - サーバー / チャンネル / メッセージのキャッシュ
        - 初回の統計値取得
        """
        if OwnerGuildID is None:
            print("UpdateInfo: OwnerGuildID が未設定です")
            return

        await self._refresh_guild()

        # チャンネルキャッシュ
        if InfoChannelID is not None:
            ch = self.bot.get_channel(InfoChannelID)
            if isinstance(ch, TextChannel):
                self._cache_channel = ch
            else:
                try:
                    ch = await self.bot.fetch_channel(InfoChannelID)
                    if isinstance(ch, TextChannel):
                        self._cache_channel = ch
                except Exception as e:
                    print(f"UpdateInfo: チャンネル取得に失敗: {e}")

        # メッセージを履歴から探す
        if self._cache_channel:
            try:
                async for msg in self._cache_channel.history(limit=200):
                    if msg.author.id == self.bot.user.id:
                        self._cache_message = msg
                        break
            except Exception as e:
                print(f"UpdateInfo: メッセージ履歴取得に失敗: {e}")

        # 初回統計値更新
        await self._refresh_stats()

        await self.update()

        # 起動ログを BotLog に送る
        botlog: "BotLog" | None = self.bot.get_cog("BotLog")
        try:
            await botlog.send(embed=Embed(
                title="UpdateInfo",
                description=f"起動しました\n\n<#{InfoChannelID}> を更新しました",
                color=Color.blue()
            ))

        except Exception:
            pass

    async def _refresh_stats(self) -> None:
        """サーバー情報を更新する"""
        await self._refresh_guild()

        if not self.guild:
            return

        self.owner = self.guild.owner or self.guild.get_member(self.guild.owner_id)
        self.member_count = self.guild.member_count or 0
        self.humans = sum(1 for m in self.guild.members if not m.bot)
        self.bots = self.member_count - self.humans
        self.boost_count = self.guild.premium_subscription_count or 0
        self.boost_level = self.guild.premium_tier or 0

    async def _refresh_guild(self) -> None:
        try:
            guild = self.bot.get_guild(OwnerGuildID)

            if guild is None:
                guild = await self.bot.fetch_guild(OwnerGuildID)

            self.guild = guild

        except HTTPException as e:
            print(f"UpdateInfo: guild fetch失敗: {e}")
            self.guild = None

    async def _get_info_channel(self) -> Optional[TextChannel]:
        """キャッシュまたは API からインフォチャンネルを取得する"""
        if self._cache_channel:
            return self._cache_channel

        if InfoChannelID is None:
            return None

        ch = self.bot.get_channel(InfoChannelID)
        if isinstance(ch, TextChannel):
            self._cache_channel = ch
            return ch

        try:
            ch = await self.bot.fetch_channel(InfoChannelID)
            if isinstance(ch, TextChannel):
                self._cache_channel = ch
                return ch

        except Exception:
            return None

        return None

    async def _get_info_message(self) -> Optional[Message]:
        """キャッシュまたは API からインフォメッセージを取得する"""
        if self._cache_message:
            return self._cache_message

        channel = await self._get_info_channel()
        if channel is None:
            return None

        try:
            async for msg in channel.history(limit=200):
                if msg.author.id == self.bot.user.id:
                    self._cache_message = msg
                    break

        except Exception:
            return None

        return self._cache_message

    async def create_view(self) -> ui.LayoutView:
        """現時点のデータからLayoutViewを作成して返します"""
        view = ui.LayoutView(timeout=None)
        container = ui.Container(accent_color=Color.blue())

        container.add_item(ui.Section(
            ui.TextDisplay(
                f"- サーバー名\n> ## {self.guild.name}\n"
                f"- サーバーの作成日時\n> ## {self.guild.created_at.astimezone(JST).strftime('%Y/%m/%d %H:%M:%S')}"
            ),
            accessory=ui.Thumbnail(self.guild.icon.url if self.guild.icon else self.bot.user.display_avatar.url)
        ))

        container.add_item(ui.ActionRow(self.Guild(self))) # サーバー詳細情報展開ボタン

        container.add_item(ui.Separator())

        try:
            container.add_item(ui.Section(
                ui.TextDisplay(
                    "- サーバーオーナー\n"
                    f"> ## {self.owner.mention}\n"
                    f"> OwnerName: `{self.owner.name}`\n"
                    f"> OwnerID: `{self.owner.id}`"
                ),
                accessory=ui.Thumbnail(self.owner.display_avatar.url)
            ))
        except:
            container.add_item(ui.TextDisplay(
                "- サーバーオーナー\n"
                "> 取得中"
            ))

        # container.add_item(ui.ActionRow(self.Owner(self))) # オーナー詳細情報展開ボタン

        container.add_item(ui.Separator())

        container.add_item(ui.TextDisplay(
            f"- 総メンバー数\n"
            f"> ## {self.member_count}\n"
            f"- ユーザー数\n"
            f"> ## {self.humans}\n"
            f"- Bot数\n"
            f"> ## {self.bots}\n"
        ))

        container.add_item(ui.Separator())

        container.add_item(ui.TextDisplay(
            f"- サーバーブースト数\n"
            f"> {self.boost_count}\n"
            f"- サーバーレベル\n"
            f"> {self.boost_level}"
        ))

        container.add_item(ui.Separator())

        now_ts = int(datetime.now(JST).timestamp())

        container.add_item(ui.TextDisplay(
            f"-# 最終更新: <t:{now_ts}:F> (<t:{now_ts}:R>)"
        ))

        view.add_item(container)

        return view

    async def update(self) -> None:
        await self._refresh_stats()

        if not await self._get_info_message():
            await self._get_info_channel()

        if not self._cache_channel:
            return

        if self._cache_message:
            await self._cache_message.edit(
                view=await self.create_view(),
                allowed_mentions=AllowedMentions.none()
            )
        else:
            self._cache_message = await self._cache_channel.send(
                view=await self.create_view(),
                allowed_mentions=AllowedMentions.none()
            )

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member: Member):
        if member.guild.id != OwnerGuildID:
            return

        await self.update()

    @commands.Cog.listener("on_member_remove")
    async def on_member_remove(self, member: Member):
        if member.guild.id != OwnerGuildID:
            return

        await self.update()

    @commands.Cog.listener("on_guild_update")
    async def on_guild_update(self, before: Guild, after: Guild):
        if after.id != OwnerGuildID:
            return

        await self.update()

    async def create_guild_view(self) -> ui.LayoutView:
        """LayoutViewを作成して返す"""
        view = ui.LayoutView(timeout=None)
        container = ui.Container(accent_color=Color.blue())

        guild_description = f"```{self.guild.description}```" if self.guild.description else "なし"

        container.add_item(ui.Section(
            ui.TextDisplay(
                f"## サーバー名\n"
                f"> {self.guild.name}\n\n"
                f"## サーバーID\n"
                f"> {self.guild.id}\n\n"
                f"## サーバー概要\n"
                f"{guild_description}\n\n"
                f"## サーバーの作成日時\n"
                f"> {self.guild.created_at.astimezone(JST).strftime('%Y/%m/%d %H:%M:%S')}"
            ),
            accessory=ui.Thumbnail(self.guild.icon.url if self.guild.icon else self.bot.user.display_avatar.url)
        ))

        try:
            container.add_item(ui.Separator())

            container.add_item(ui.Section(
                ui.TextDisplay("## サーバーバナー画像"),
                accessory=ui.Thumbnail(self.guild.banner.url)
            ))
        except:
            pass

        try:
            container.add_item(ui.Separator())

            container.add_item(ui.Section(
                ui.TextDisplay("## サーバー招待画像"),
                accessory=ui.Thumbnail(self.guild.splash.url)
            ))
        except:
            pass

        view.add_item(container)

        return view

    class Guild(ui.Button):
        def __init__(self, info: "UpdateInfo"):
            self.info = info

            super().__init__(
                label="サーバーの詳細な情報",
                style=ButtonStyle.primary
            )

        async def callback(self, interaction: Interaction):
            await interaction.response.send_message(
                view=await self.info.create_guild_view(),
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    cog = UpdateInfo(bot)
    await bot.add_cog(cog)

    bot.update_info = cog
