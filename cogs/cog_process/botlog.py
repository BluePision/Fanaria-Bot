import discord
from discord.ext import commands
from typing import Optional, List

from configs.main import OwnerGuildID, AllBotLogChannelID

class BotLog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # キャッシュ用（None のままでも動作する）
        self._cache_channel: Optional[discord.TextChannel] = None

    async def _get_log_channel(self) -> Optional[discord.TextChannel]:
        """キャッシュまたは API からログチャンネルを取得するヘルパー"""
        if self._cache_channel:
            return self._cache_channel

        if AllBotLogChannelID is None:
            return None

        # まずキャッシュから取得
        ch = self.bot.get_channel(AllBotLogChannelID)
        if isinstance(ch, discord.TextChannel):
            self._cache_channel = ch
            return ch

        # キャッシュに無ければ fetch
        try:
            ch = await self.bot.fetch_channel(AllBotLogChannelID)
            if isinstance(ch, discord.TextChannel):
                self._cache_channel = ch
                return ch
        except Exception:
            return None

        return None

    async def initialize(self):
        """
        起動直後に呼ぶ初期化処理:
        - ログチャンネルをキャッシュ
        - 起動ログを送信（任意）
        """
        ch = await self._get_log_channel()
        if ch:
            # 起動ログを送る
            try:
                await ch.send(embed=discord.Embed(
                    title="Botが起動しました",
                    color=discord.Color.blue()
                ))

            except Exception as e:
                print(f"BotLog: 起動ログ送信に失敗: {e}")
        else:
            print("BotLog: ログチャンネルが取得できませんでした")

    async def send(
        self,
        content: Optional[str] = None,
        files: Optional[List[discord.File]] = None,
        embed: Optional[discord.Embed] = None,
        embeds: Optional[List[discord.Embed]] = None,
        layoutview: Optional[discord.ui.LayoutView] = None
    ) -> Optional[discord.Message]:
        """
        Bot ログ送信ユーティリティ

        - content: 送信するテキスト
        - files: discord.File のリスト
        - embed: 単一の Embed
        - embeds: Embed のリスト
        - layoutview: discord.ui.LayoutView
        """
        # 引数チェック
        if not (content or files or embed or embeds or layoutview):
            raise ValueError("content か files か embed/embeds か layoutview のいずれかを指定してください")

        if (embed or embeds) and layoutview:
            raise ValueError("embed/embeds と layoutview は共存できません")

        channel = await self._get_log_channel()
        if channel is None:
            # ログチャンネルが設定されていない／取得できない場合は None を返す
            print("BotLog: ログチャンネルが設定されていないか取得できませんでした")
            return None

        # embeds を統合
        final_embeds: List[discord.Embed] = []
        if embed:
            final_embeds.append(embed)
        if embeds:
            final_embeds.extend(embeds)

        # files の扱い: None か list[discord.File]
        send_kwargs = {}
        if content:
            send_kwargs["content"] = content
        if final_embeds:
            send_kwargs["embeds"] = final_embeds
        if layoutview:
            send_kwargs["view"] = layoutview
        if files:
            # discord.py の send は files 引数を受け取る
            send_kwargs["files"] = files

        try:
            # wait=True の場合は Message を返す
            message = await channel.send(**send_kwargs)
            return message
        except Exception as e:
            # 送信失敗時はログ出力して None を返す
            print(f"BotLog: メッセージ送信に失敗しました: {e}")
            return None

async def setup(bot: commands.Bot):
    cog = BotLog(bot)
    await bot.add_cog(cog)

    bot.botlog = cog
