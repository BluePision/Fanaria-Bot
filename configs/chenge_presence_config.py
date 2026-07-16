import random
from dataclasses import dataclass, field
from typing import Optional
from discord import CustomActivity, Game, Activity, ActivityType
from discord.ext import commands


Edm_Music_Genres = [
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

def get_activities(music, ping) -> list[tuple]:
    return [
        # 1周
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
        # 2周
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
        # 3周
        (lambda text: CustomActivity(name=text), "物置を探索中", 10.0),
        (lambda text: CustomActivity(name=text), "ゲジが現れたためカタストロム中", 30.0),
        (lambda text: CustomActivity(name=text), music, 20.0),
        (lambda text: CustomActivity(name=text), ping, 5.0),
        (lambda text: CustomActivity(name=text), ping, 5.0),
        (lambda text: CustomActivity(name=text), "敗者に相応しいエンディングを見せてやる(虫コロリ)", 30.0),
        (lambda text: CustomActivity(name=text), music, 20.0),
        (lambda text: CustomActivity(name=text), "ゆーやを呼び出し中", 10.0),
        (lambda text: CustomActivity(name=text), "おれおを胴上げ中", 30.0),
        (lambda text: CustomActivity(name=text), music, 20.0),
        (lambda text: CustomActivity(name=text), music, 20.0),
        (lambda text: CustomActivity(name=text), "ｶﾒｪﾝﾗｲﾀﾞｧｰ! ｸﾞﾗﾝﾄﾞｼﾞｵｳ!!!", 20.0),
        (lambda text: CustomActivity(name=text), "正確には明確なキャラクターは存在しないんだよね", 30.0),
        (lambda text: CustomActivity(name=text), music, 20.0),
    ]


# 殆ど諦め中 むずい
"""
@dataclass
class PresenceActivity:
    \"""
    1つのアクティビティを定義するクラス

    Args:
        activity (CustomActivity): アクティビティそのもの
        sleep_time (float): 待機時間・そのアクティビティを表示する時間
        text (Optional[str]): 実際のテキスト
    \"""

    activity: CustomActivity
    sleep_time: float
    text: Optional[str]

@dataclass
class Activities:
    \"""

    Args:
        activity_list (list[PresenceActivity]): アクティビティのリスト
        weight (float): 重み。値が大きければ大きいほど選ばれやすくなるようにする
    \"""

    activity_list: list[PresenceActivity]
    weight: float

class ChengeActivity:
    \"""
    もしかしたら作るかもしれないクラス

    思いついたら作る
    \"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.music = lambda: self._get_music_genre_text()
        self.ping = lambda: self._get_latency_text()

    def _get_latency_text(self) -> str:
        latency = round(self.bot.latency * 1000)
        return f"Ping値は{latency}ms" if latency >= 0 else "Ping値 Error"

    def _get_music_genre_text(self) -> str:
        genre = random.choice(Edm_Music_Genres)
        return f"{genre}を再生中"

ActivitiesList = [
    Activities(
        activity_list=[
            PresenceActivity(activity=lambda: CustomActivity(name="キャッシュを確認中"), sleep_time=10.0, text="キャッシュを確認中"),
            PresenceActivity(activity=lambda: CustomActivity(name=ChengeActivity.ping), sleep_time=5.0),
            PresenceActivity(activity=lambda: Activity(type=ActivityType.custom), sleep_time=5.0)
        ],
        weight=50.0
    )
]
"""
