"""
Botのステータスを変更する処理を行うCog
"""

import asyncio
import random
from discord import CustomActivity, Game, HTTPException
from discord.ext import commands

from configs.change_presence_config import Edm_Music_Genres, get_activities


class ChangeStatus(commands.Cog):
    """
    ステータスの変更を行うCog
    """
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        music = lambda: self._get_music_genre_text()
        ping = lambda: self._get_latency_text()

        self.activities = get_activities(music, ping)

        # ステータスの変更 関数を常時実行タスクとして実行、ループさせる
        self.task = bot.loop.create_task(self.change_presence())

    def cog_unload(self) -> None:
        """Cogがアンロードされた時"""

        # タスクを停止させる
        self.task.cancel()

    def _get_latency_text(self) -> str:
        """Botのレイテンシーを取得する"""
        latency = round(self.bot.latency * 1000)
        return f"Ping値は{latency}ms" if latency >= 0 else "Ping値 Error"

    def _get_music_genre_text(self) -> str:
        """曲のジャンルをランダムに選ぶ"""
        genre = random.choice(Edm_Music_Genres)
        return f"{genre}を再生中"

    async def change_presence(self) -> None:
        """
        実際にステータスの変更を開始する関数
        """
        await asyncio.sleep(5)
        await self.bot.wait_until_ready()

        index = 0

        # Botが起動していれば開始する
        while not self.bot.is_closed():
            try:
                activity_factory, content, sleep_time = self.activities[index]

                # 内容が関数ならそれを実行して文字列にする
                text = content() if callable(content) else content

                # ステータスを変更する
                await self.bot.change_presence(
                    activity=activity_factory(text)
                )

                # 待機する
                await asyncio.sleep(sleep_time)

                # 次の準備をする
                index = (index + 1) % len(self.activities)

            except asyncio.CancelledError:
                raise

            except HTTPException as e:
                print(f"[ChangeStatus] 通信エラー:\n{e}")
                await asyncio.sleep(60)

            except Exception as e:
                print(f"[ChangeStatus] エラー:\n{e}")
                await asyncio.sleep(30)


async def setup(bot: commands.Bot):
    """CogをBotに紐づけて起動する"""
    await bot.add_cog(ChangeStatus(bot))
