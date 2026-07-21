import asyncio
import random
from discord import CustomActivity, Game, HTTPException
from discord.ext import commands

from configs.change_presence_config import Edm_Music_Genres, get_activities


class ChangeStatus(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        music = lambda: self._get_music_genre_text()
        ping = lambda: self._get_latency_text()

        self.activities = get_activities(music, ping)

        self.task = bot.loop.create_task(self.change_presence())

    def cog_unload(self) -> None:
        self.task.cancel()

    def _get_latency_text(self) -> str:
        latency = round(self.bot.latency * 1000)
        return f"Ping値は{latency}ms" if latency >= 0 else "Ping値 Error"

    def _get_music_genre_text(self) -> str:
        genre = random.choice(Edm_Music_Genres)
        return f"{genre}を再生中"

    async def change_presence(self) -> None:
        await asyncio.sleep(5)
        await self.bot.wait_until_ready()

        index = 0

        while not self.bot.is_closed():
            try:
                activity_factory, content, sleep_time = self.activities[index]

                text = content() if callable(content) else content

                await self.bot.change_presence(
                    activity=activity_factory(text)
                )

                await asyncio.sleep(sleep_time)

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
    await bot.add_cog(ChangeStatus(bot))
