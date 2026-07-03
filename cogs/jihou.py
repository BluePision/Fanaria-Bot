import os
import discord
from discord.ext import commands, tasks
import random
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

from configs.jihou_config import Jihou, JihouTime, JihouUser, JihouData

load_dotenv()
JihouWebhookURL = os.environ.get("JihouWebhookURL")

if not JihouWebhookURL:
    raise RuntimeError("JihouWebhookURL が設定されていません")

JST = timezone(timedelta(hours=9))

class JihouCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # 時報を初期化
        self.jihou = Jihou(bot, JihouWebhookURL)

        self._last_sent: str | None = None

        self.loop.start()

    def cog_unload(self):
        self.loop.cancel()

    @tasks.loop(seconds=10)
    async def loop(self):
        # 現在の時間
        now = datetime.now(JST)
        key = now.strftime("%Y-%m-%d %H:%M")

        # 前回送った時間が一緒なら戻る
        if self._last_sent == key:
            return

        # 何時何分の形にする
        current = now.strftime("%H:%M")

        # その時間が存在するか確認し、JihouTimeを受け取る
        try:
            time = JihouTime(current)

        except ValueError:
            return

        # ユーザーをランダムに選ぶ
        jihou_user = self.jihou.choice_user(time)
        user = self.bot.get_user(jihou_user.id)
        if user is None:
            user = await self.bot.fetch_user(jihou_user.id)

        # そのユーザーのメッセージリストを取得する
        messages = jihou_user.get_messages(time)
        if not messages:
            return

        # 時報を1つランダムに選ぶ
        message = random.choice(messages)

        # 時報を送信する
        await self.jihou.send(
            content = message,
            username = user.display_name,
            avatar_url = user.display_avatar.url
        )

        # 送った時間を記録する
        self._last_sent = key

    @loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(JihouCog(bot))