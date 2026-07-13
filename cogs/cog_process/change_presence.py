import asyncio
import random
from discord import CustomActivity, Game, HTTPException
from discord.ext import commands

class ChangeStatus(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        music = lambda: self._get_music_genre_text()
        ping = lambda: self._get_latency_text()

        self.edm_music_genres = [
            "Hardcore",
            "Happy Hardcore",
            "UK Hardcore",
            "Frenchcore",
            "Speedcore",
            "Terrorcore",
            "Gabber",
            "Hardstyle",
            "Rawstyle",
            "Euphoric Hardstyle",
            "Xtra Raw",
            "Uptempo Hardcore",

            "Dubstep",
            "Brostep",
            "Riddim",
            "Melodic Dubstep",
            "Colour Bass",
            "Tearout",
            "Deathstep",
            "Briddim",

            "Drum'n'Bass",
            "Liquid Drum'n'Bass",
            "Neurofunk",
            "Jump Up",
            "Jungle",
            "Atmospheric Drum'n'Bass",

            "Future Bass",
            "Kawaii Future Bass",
            "Future House",
            "Future Bounce",

            "House",
            "Deep House",
            "Progressive House",
            "Electro House",
            "Big Room House",
            "Bass House",
            "Tech House",
            "Tropical House",

            "Trance",
            "Uplifting Trance",
            "Progressive Trance",
            "Psytrance",
            "Goa Trance",
            "Tech Trance",

            "Techno",
            "Melodic Techno",
            "Hard Techno",
            "Acid Techno",
            "Minimal Techno",

            "Electro",
            "Complextro",
            "Glitch Hop",
            "Moombahton",
            "Trap",
            "Hybrid Trap",
            "Phonk",
            "Wave",
            "Future Garage",
            "UK Garage",
            "Breakbeat",
            "IDM",
            "Chiptune",

            "Breakcore",
            "Mashcore",
            "Crossbreed",
            "Schranz",
            "Flashcore",
            "Extratone",
        ]

        """
            # この14行が1周みたいなもん

            (lambda text: CustomActivity(name=text), "", 10.0),
            (lambda text: CustomActivity(name=text), "", 30.0),
            (lambda text: CustomActivity(name=text), music, 20.0),
            (lambda text: CustomActivity(name=text), ping, 5.0),
            (lambda text: CustomActivity(name=text), ping, 5.0),
            (lambda text: CustomActivity(name=text), "", 30.0),
            (lambda text: CustomActivity(name=text), music, 20.0),
            (lambda text: CustomActivity(name=text), "", 10.0),
            (lambda text: CustomActivity(name=text), "", 30.0),
            (lambda text: CustomActivity(name=text), music, 20.0),
            (lambda text: CustomActivity(name=text), music, 20.0),
            (lambda text: CustomActivity(name=text), "", 20.0),
            (lambda text: CustomActivity(name=text), "", 30.0),
            (lambda text: CustomActivity(name=text), music, 20.0),
        """
        self.activities = [
            (lambda text: CustomActivity(name=text), "キャッシュを確認中", 10.0),
            (lambda text: CustomActivity(name=text), "プログラミングを勉強中", 30.0),
            (lambda text: CustomActivity(name=text), music, 20.0),
            (lambda text: CustomActivity(name=text), ping, 5.0),
            (lambda text: CustomActivity(name=text), ping, 5.0),
            (lambda text: CustomActivity(name=text), "雑談中", 30.0),
            (lambda text: CustomActivity(name=text), music, 20.0),
            (lambda text: CustomActivity(name=text), "てぃを叩き起こし中", 10.0),
            (lambda text: CustomActivity(name=text), "アプリを開発中", 30.0),
            (lambda text: CustomActivity(name=text), music, 20.0),
            (lambda text: CustomActivity(name=text), music, 20.0),
            (lambda text: CustomActivity(name=text), "画面の前の君の顔を視聴中", 20.0),
            (lambda text: CustomActivity(name=text), "おれおを飲食中", 30.0),
            (lambda text: CustomActivity(name=text), music, 20.0),
            # 1周
            (lambda text: CustomActivity(name=text), "仮想環境でテストが面倒な為本番環境でテスト中", 10.0),
            (lambda text: CustomActivity(name=text), "エズにかまちょ中", 30.0),
            (lambda text: CustomActivity(name=text), music, 20.0),
            (lambda text: CustomActivity(name=text), ping, 5.0),
            (lambda text: CustomActivity(name=text), ping, 5.0),
            (lambda text: CustomActivity(name=text), "DIY中", 30.0),
            (lambda text: CustomActivity(name=text), music, 20.0),
            (lambda text: CustomActivity(name=text), "軽く休憩中", 10.0),
            (lambda text: CustomActivity(name=text), "雑談中", 30.0),
            (lambda text: CustomActivity(name=text), music, 20.0),
            (lambda text: CustomActivity(name=text), music, 20.0),
            (lambda text: CustomActivity(name=text), "調理中", 20.0),
            (lambda text: CustomActivity(name=text), "焦げすぎて滅", 30.0),
            (lambda text: CustomActivity(name=text), music, 20.0),
            # 2周
        ]

        self.task = bot.loop.create_task(self.change_presence())

    def cog_unload(self) -> None:
        self.task.cancel()

    def _get_latency_text(self) -> str:
        latency = round(self.bot.latency * 1000)
        return f"Ping値は{latency}ms" if latency >= 0 else "Ping値 Error"

    def _get_music_genre_text(self) -> str:
        genre = random.choice(self.edm_music_genres)
        return f"{genre}を再生中"

    async def change_presence(self) -> None:
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