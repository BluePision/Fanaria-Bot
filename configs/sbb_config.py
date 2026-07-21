"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from discord import Message


class BulletinBoardBots(Enum):
    \"""
    サーバー掲示板機能を持つBotを指定しやすくするEnumクラス

    Args:
        Disboard: DISBOARD#2760
        dissoku: ディス速#2894
        DCafe: DCafe#7305
        Dicoall: Dicoall#1838
        Discadia: Discadia#9430
    \"""

    Disboard = 302050872383242240
    dissoku = 761562078095867916
    DCafe = 850493201064132659
    Dicoall = 903541413298450462
    Discadia = 1222548162741538938

    def __init__(self, id: int):
        self.id = id

    def __str__(self) -> str:
        return str(self.id)

@dataclass
class ResponseMessageEmbedField:
    \"""
    サーバー掲示板機能を持つBotの返答のメッセージ内のEmbedにあるFieldの内容を設定するデータクラス
    \"""

    name: Optional[str] = None
    value: Optional[str] = None

@dataclass
class ResponseMessageEmbed:
    \"""
    サーバー掲示板機能を持つBotの返答のメッセージに入っているEmbedの内容を設定するデータクラス
    \"""

    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    fields: Optional[List[ResponseMessageEmbedField]] = None

@dataclass
class ResponseMessage:
    \"""
    サーバー掲示板機能を持つBotの返答のメッセージを設定するデータクラス
    \"""

    content: Optional[str] = None
    embed: Optional[ResponseMessageEmbed] = None

@dataclass
class BulletinBoardBotConfig:
    \"""
    サーバー掲示板機能を持つBotの特徴を設定するデータクラス

    Args:
        bot (BulletinBoardBots): サーバー掲示板Bot
        command_name (str): bump/upのコマンドの名前
        cool_time (int): bumpやupの成功後、次に使用できるようになるまでのクールタイム（分）
        success_message (ResponseMessage): 成功時のメッセージ
        fail_message (Optional[ResponseMessage]): 失敗時のメッセージ。ないBotもある
    \"""

    bot: BulletinBoardBots
    command_name: str
    cool_time: int
    success_message: ResponseMessage
    fail_message: Optional[ResponseMessage]

    def __str__(self) -> str:
        return str(self.bot.id)

class BulletinBoardFunctions:
    \"""サーバー掲示板Botの様々な判断をしやすくするためのヘルパー的なクラス\"""

    def _text_format(self, text: str, message: Message) -> str:
        metadata = message.interaction_metadata if message.interaction_metadata else None
        author = metadata.user if metadata and metadata.user else message.author

        return (
            text
            .replace("%UserMention%", author.mention)
            .replace("%ServerName%", message.guild.name)
        )

    def _is_match_message(
        self,
        config_message: ResponseMessage,
        message: Message
    ) -> bool:
        if (
            message.content and config_message.content
            and self._text_format(config_message.content, message) in message.content
        ):
            return True

        if not message.embeds:
            return False

        if not config_message.embed:
            return False

        embed = message.embeds[0]
        field = embed.fields[0] if embed.fields else None

        embed_title = embed.title or ""
        embed_description = embed.description or ""
        embed_url = embed.url or ""

        field_name = field.name if field else ""

        config_embed = config_message.embed
        config_field = config_embed.fields[0] if config_embed.fields else None

        config_title = config_embed.title or ""
        config_description = config_embed.description or ""
        config_url = config_embed.url or ""

        config_field_name = config_field.name if config_field else ""

        if (
            (config_title and self._text_format(config_title, message) in embed_title)
            or (config_description and self._text_format(config_description, message) in embed_description)
            or (config_url and config_url in embed_url)
            or (config_field_name and self._text_format(config_field_name, message) in field_name)
        ):
            return True

        return False

    def has_bulletin_board_bot(
        self,
        bot: BulletinBoardBots | int
    ) -> bool:
        if isinstance(bot, BulletinBoardBots):
            bot = bot.id

        for config in ServerBulletinBoardsData:
            if config.bot.id == bot:
                return True

        return False

    def get_bulletin_board_bot(
        self,
        bot: BulletinBoardBots | int
    ) -> BulletinBoardBotConfig:
        if isinstance(bot, BulletinBoardBots):
            bot = bot.id

        for config in ServerBulletinBoardsData:
            if config.bot.id == bot:
                return config

        raise ValueError(f"{bot} のIDを持つBotは設定されていません")

    def is_success_bulletin_board_message(
        self,
        bot: BulletinBoardBots | int,
        message: Message
    ) -> bool:
        \"""指定されたメッセージが設定されている成功メッセージかどうか判断する\"""
        config = self.get_bulletin_board_bot(bot)
        return self._is_match_message(config.success_message, message)

    def is_fail_bulletin_board_message(
        self,
        bot: BulletinBoardBots | int,
        message: Message
    ) -> bool:
        \"""指定されたメッセージが設定されている失敗メッセージかどうか判断する\"""
        config = self.get_bulletin_board_bot(bot)
        if not config.fail_message:
            raise ValueError(f"{bot} には失敗メッセージが設定されていません")

        return self._is_match_message(config.fail_message, message)


ServerBulletinBoardsData: List[BulletinBoardBotConfig] = [
    BulletinBoardBotConfig(
        bot = BulletinBoardBots.Disboard,
        command_name = "bump",
        cool_time = 120,
        success_message = ResponseMessage(
            embed = ResponseMessageEmbed(
                title = "DISBOARD: Discordサーバー掲示板",
                description = "表示順をアップしたよ :thumbsup:",
                url = "https://disboard.org"
            )
        )
    ),
    BulletinBoardBotConfig(
        bot = BulletinBoardBots.dissoku,
        command_name = "up",
        cool_time = 120,
        success_message = ResponseMessage(
            embed = ResponseMessageEmbed(
                title = "ディス速 | Discordサーバー・友達募集・ボット掲示板",
                description = "%UserMention%\ncommand: `/up`",
                url = "https://dissoku.net/ja"
            )
        ),
        fail_message = ResponseMessage(
            embed = ResponseMessageEmbed(
                title = "ディス速 | Discordサーバー・友達募集・ボット掲示板",
                description = "%UserMention%\ncommand: `/up`",
                url = "https://dissoku.net/ja",
                fields = [ResponseMessageEmbedField(
                    name = "失敗しました..."
                )]
            )
        )
    ),
    BulletinBoardBotConfig(
        bot = BulletinBoardBots.DCafe,
        command_name = "up",
        cool_time = 120,
        success_message = ResponseMessage(
            embed = ResponseMessageEmbed(
                title = "Discord Cafe | Discord掲示板",
                description = "サーバーの表示順位を上げました！",
                url = "https://discordcafe.app"
            )
        )
    ),
    BulletinBoardBotConfig(
        bot = BulletinBoardBots.Dicoall,
        command_name = "up",
        cool_time = 120,
        success_message = ResponseMessage(
            embed = ResponseMessageEmbed(
                title = "🎉 サーバーがリストの最上段に更新されました！",
                description = "サーバーリストのトップに正常に表示されています。"
            )
        )
    ),
    BulletinBoardBotConfig(
        bot = BulletinBoardBots.Discadia,
        command_name = "bump",
        cool_time = 120,
        success_message = ResponseMessage(
            content = "%ServerName% has been successfully bumped!"
        )
    )
]
"""