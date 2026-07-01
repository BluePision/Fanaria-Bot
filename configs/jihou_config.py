from discord import Webhook, WebhookMessage
from discord.ext import commands
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

class JihouTime(Enum):
    """
    時報専用の時報の時間用のクラス
    """

    morning = "07:00"
    night = "22:45"
    midnight = "02:30"

    def __str__(self) -> str:
        return self.value

@dataclass
class JihouUser:
    """
    時報専用の時報ユーザー用のクラス  
    時報ユーザーの様々なデータを格納しています

    Args:
        id (int): UserID
        weight (float): 重み。値が大きければ大きいほど選ばれやすくなるようにする
        messages (dict[JihouTime, list[str]]): そのユーザーが話すことのできるメッセージ
    """

    id: int
    weight: float
    messages: Dict[JihouTime, List[str]] = field(default_factory=dict)

    def get_messages(
            self,
            time: str | JihouTime
    ) -> List[str]:
        if isinstance(time, str):
            try:
                time = JihouTime(time)

            except ValueError:
                try:
                    time = JihouTime[time]

                except KeyError:
                    return []

        return self.messages.get(time, [])


class Jihou:
    """
    時報のメインクラス  
    ランダムにユーザーを選択する機能がある
    """
    def __init__(
            self,
            bot: commands.Bot,
            webhookurl: str
    ):
        """
        Args:
            webhook (str): Discord WebhookURL。時報の送信に使われる。
        """
        self.webhook = Webhook.from_url(
            webhookurl,
            client=bot
        )

    def choice_user(self) -> JihouUser:
        return random.choices(
            JihouData,
            weights=[u.weight for u in JihouData],
            k=1
        )[0]

    async def send(
            self,
            content: str,
            username: str,
            avatar_url: str,
            *,
            wait: bool = False
    ) -> Optional[WebhookMessage]:
        if wait:
            return await self.webhook.send(
                content = content,
                username = username,
                avatar_url = avatar_url,
                wait=True
            )
        else:
            await self.webhook.send(
                content = content,
                username = username,
                avatar_url = avatar_url
            )
            return

JihouData = [
    JihouUser(
        id = 1102936594362671235,
        weight = 89.0,
        messages = {
            JihouTime.morning: [
                "おはよう", "おは", "よく寝た？", "おはようございます。\n寝起きにBANはいかがですか？\nあ、いや？じゃあTOならどう？", "起きて働け社畜精神の日本人諸君",
                "おはおは", "おはよ", "もう少し寝たい", "おっはー", "ﾋﾟﾋﾟﾋﾟﾋﾟﾋﾟﾋﾟﾋﾟﾋﾟﾋﾟﾋﾟﾋﾟ\n朝のアラームですよー", "起きやがれ日本人共ー！", "print(\"Hello World\")",
                "早起きは三文の徳と言います。\nまぁ7時に起きてるので全然早起きでは無いんですけど", "( ・∇・)", "ふぅ……おやすみ……\nあぁいやおはよう",
                "起きて日の光を浴びることで体内時計がリセットされたりといろいろないいことがあります\nいっつも眠い君たちは早く日光浴びて飯食え",
                "社会という名のレイドバトル開始です", "本日のログインボーナス: 睡眠不足", "朝だよ。意識、再起動して", "布団「行かないで」",
                "起きたくないんじゃないんです！\n布団が私を放してくれないんです！！！", "起きろよ！！！私が言えることじゃないけど！！！！！",
                "\\u304A\\u306F\\u3088\\u3046",
                "目覚まし時計　鳴り止め時計　Oh Yeah！\n目覚まし時計　止めろよ時計　Wow Wow\n目覚まし時計　起きろよボケ　Oh Yeah！\n目覚まし時計　目覚まし時計　Wow Wow Yeah！\n\n[【MV】睡魔/マサイ a.k.a マサ寝坊【目覚まし時計の歌（Full Ver.）】](https://youtu.be/CzVOUBxQs6c)"
            ],
            JihouTime.night: [
                "おやすみ", "おやす", "寝る。おやすみ", "zzz", "寝てくださーい(フライパンｶﾞﾝｶﾞﾝ)", "はよねろやーい(ドアぶち破り)", "ねないこだれだ", "おやすみんみんぜみ", "寝ろよ子供たち",
                "寝る。寝るから君たちも早く寝なさい", "早く寝てね。\n寝たくない？ずっと喋ってるとタイムアウトしてあげるよ？", "TO SLEEEEEEEEEEEP!!!!!!!!", "寝ろ", "おやすめ(命令系)",
                "どの年代もそうですが若いうちは特に早く寝たほうが良いですよ\n\n画面から目を離しておふとぅんぬくぬくしながら自然と眠気に身を任せるのです\n\nようはさっさと寝ろ",
                "寝るかタイムアウトか選ばせてやろう", "ねろねろびーむ！", "ベッドは裏切らない"
            ],
            JihouTime.midnight: [
                "起きてないで寝て下さい", "こんにちは、夜中の寝て下さいアラームですよ", "おっ、もしかして昼夜逆転？", "夜更かしは悪いことだけどなんかやりたくなっちゃうよね。\n\nはよ寝ろ",
                "いつまで起きてるんです？", "流石に起きてる子はいないよね？\nあ、いる？寝なよ", "流石に今まで起きてるのはおかしいよ君……\n昼夜逆転は身体に悪いよ",
                "太陽に見られたら怒られ……あぁ太陽いないわ"
            ]
        }
    ),
    JihouUser(
        id = 1448134124580896830,
        weight = 10.0,
        messages = {
            JihouTime.morning: [
                "おはよう", "おはよ～", "おはよ", "おは～"
            ],
            JihouTime.night: [
                "おやすみ", "おばん、おやすみ", "おやすみ～"
            ],
            JihouTime.midnight: [
                "いつまで起きてるの……", "もう寝なよ～……"
            ]
        }
    ),
    JihouUser(
        id = 1334120019210010644,
        weight = 1.0,
        messages = {
            JihouTime.morning: [
                "おはよう", "おはよ～", "おはよ", "もう少し寝たいな"
            ],
            JihouTime.night: [
                "おやすみ", "おやすみ～"
            ],
            JihouTime.midnight: [
                "いつまで起きてるの……"
            ]
        }
    )
]