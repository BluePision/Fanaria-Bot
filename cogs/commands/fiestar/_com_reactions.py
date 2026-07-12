import math
from discord import app_commands, Interaction, Message, InteractionMessage, TextChannel, AllowedMentions, ui, components, ButtonStyle, SelectOption, Member, User, Embed, Color, utils
from discord.ext import commands
from typing import Optional, List
import traceback
import re

from ._group import fiestar_group
from ._process_db_connect import fiestar_database

from configs.main import OwnerGuildID, FiestarChannelID
from configs.fiestar_config import emoji_map


class ReactionList:
    def __init__(self, bot: commands.Bot, user: User):
        self.bot: commands.Bot = bot
        self.user: User = user

        self.fiestar_channel: TextChannel = None

        self.message_ids = []
        self.messages: List[Message] = [] # 全メッセージのキャッシュ用

        self.response_message: InteractionMessage = None
        self.page = 0
        self.now_reaction: str = ""

    def get_message_ids(self, reaction: str) -> List[int] | List:
        """データベースからメッセージIDのリストを受け取る"""
        self.message_ids = fiestar_database.get_reactions(self.user.id, reaction)
        return self.message_ids

    async def get_channel(self) -> Optional[TextChannel]:
        """キャッシュとAPIを使ってチャンネルを返す"""
        channel = self.bot.get_channel(FiestarChannelID)
        if isinstance(channel, TextChannel):
            self.fiestar_channel = channel
            return channel

        try:
            channel = await self.bot.fetch_channel(FiestarChannelID)
            self.fiestar_channel = channel
            return channel

        except Exception:
            return None

    async def get_message(self, message_id: int) -> Optional[Message]:
        """メッセージを取得する"""
        message = utils.get(
            self.bot.cached_messages,
            id=message_id
        )
        if message is None:
            try:
                message = await self.fiestar_channel.fetch_message(message_id)

            except Exception:
                message = None

        return message

    async def get_ten_messages(self) -> List[Message]:
        """
        現在のページで表示するべきメッセージのリスト10件を返す

        もしself.messages（これまでのキャッシュ）にあるならそこから10件を取って返す
        """
        start = self.page * 10
        end = start + 10

        messages = []

        for message_id in self.message_ids[start:end]:
            message = utils.get(self.messages, id=message_id)

            if message is None:
                message = await self.get_message(message_id)
                if message is not None:
                    self.messages.append(message)

            if message is not None:
                messages.append(message)

        return messages

    def get_page_count(self) -> int:
        """10件ごとに区切った最大ページ数を返す"""
        if not self.message_ids:
            return 1

        return math.ceil(len(self.message_ids) / 10)

    async def create_view(self) -> ui.LayoutView:
        view = ui.LayoutView(timeout=300)
        container = ui.Container(accent_color=Color.blue())

        container.add_item(ui.TextDisplay(
            f"# Fiestar {self.now_reaction} リアクション履歴"
        ))
        container.add_item(ui.ActionRow(self.EmojiSelect(self)))
        container.add_item(ui.Separator())

        messages = await self.get_ten_messages()
        if messages:
            for message in messages:

                content = re.sub(
                    r"<a?:[A-Za-z0-9_]+:\d+>|:[A-Za-z0-9_]+:",
                    "[emoji]",
                    message.content
                )

                content = (
                    f"{content.splitlines()[0]} …以下略"
                    if "\n" in content
                    else (
                        f"{content[:25]} …以下略"
                        if len(content) > 30
                        else content
                        if content.strip()
                        else "(No Text)"
                    )
                )

                container.add_item(ui.Section(
                    ui.TextDisplay(
                        f"-# - MessageID`{message.id}`\n"
                        f"## > {content}"
                    ),
                    accessory=ui.Button(
                        label="メッセージ先",
                        url=message.jump_url,
                        style=ButtonStyle.link
                    )
                ))

        elif self.now_reaction == "":
            container.add_item(ui.TextDisplay(
                "リアクションを選択してください"
            ))

        else:
            container.add_item(ui.TextDisplay(
                "表示できるメッセージはありません"
            ))

        container.add_item(ui.Separator(spacing=components.SeparatorSpacing.large))

        buttons = ui.ActionRow()

        buttons.add_item(self.FirstPageButton(self))
        buttons.add_item(self.PreviousPageButton(self))
        buttons.add_item(self.NowPage(self))
        buttons.add_item(self.NextPageButton(self))
        buttons.add_item(self.LastPageButton(self))

        container.add_item(buttons)

        view.add_item(container)

        return view

    class EmojiSelect(ui.Select):
        def __init__(self, parent_class: "ReactionList"):
            self.parent_class = parent_class

            options = [
                SelectOption(label=f"{display} - {value}", value=value)
                for display, value in emoji_map.items()
            ]

            super().__init__(
                placeholder="リアクションを選択",
                options=options
            )

        async def callback(self, interaction: Interaction):
            reaction = self.values[0]
            self.parent_class.now_reaction = reaction
            self.parent_class.get_message_ids(reaction)

            self.parent_class.page = 0
            await interaction.response.edit_message(
                view=await self.parent_class.create_view()
            )

    class FirstPageButton(ui.Button): # 一番最初へ
        def __init__(self, parent_class: "ReactionList"):
            self.parent_class = parent_class

            super().__init__(
                label="<<<",
                style=ButtonStyle.primary,
                disabled=self.parent_class.page == 0
            )

        async def callback(self, interaction: Interaction):
            self.parent_class.page = 0
            await interaction.response.edit_message(
                view=await self.parent_class.create_view()
            )

    class PreviousPageButton(ui.Button): # 一つ前へ
        def __init__(self, parent_class: "ReactionList"):
            self.parent_class = parent_class

            super().__init__(
                label="<",
                style=ButtonStyle.primary,
                disabled=self.parent_class.page == 0
            )

        async def callback(self, interaction: Interaction):
            self.parent_class.page -= 1
            await interaction.response.edit_message(
                view=await self.parent_class.create_view()
            )

    class NowPage(ui.Button):
        def __init__(self, parent_class: "ReactionList"):
            self.parent_class = parent_class

            super().__init__(
                label=f"{self.parent_class.page + 1}/{self.parent_class.get_page_count()}",
                style=ButtonStyle.secondary,
                disabled=True
            )

    class NextPageButton(ui.Button):
        def __init__(self, parent_class: "ReactionList"):
            self.parent_class = parent_class

            super().__init__(
                label=">",
                style=ButtonStyle.primary,
                disabled=self.parent_class.page >= self.parent_class.get_page_count() - 1
            )

        async def callback(self, interaction: Interaction):
            self.parent_class.page += 1
            await interaction.response.edit_message(
                view=await self.parent_class.create_view()
            )

    class LastPageButton(ui.Button):
        def __init__(self, parent_class: "ReactionList"):
            self.parent_class = parent_class

            super().__init__(
                label=">>>",
                style=ButtonStyle.primary,
                disabled=self.parent_class.page >= self.parent_class.get_page_count() - 1
            )

        async def callback(self, interaction: Interaction):
            self.parent_class.page = self.parent_class.get_page_count() - 1
            await interaction.response.edit_message(
                view=await self.parent_class.create_view()
            )

@fiestar_group.command(
    name="reactions",
    description="リアクション一覧を表示する"
)
@app_commands.guild_only()
async def reactions(interaction: Interaction):

    view = ReactionList(
        interaction.client,
        interaction.user
    )

    await view.get_channel()

    await interaction.response.send_message(
        view=await view.create_view(),
        ephemeral=True,
        allowed_mentions=AllowedMentions.none()
    )

    view.response_message = await interaction.original_response()
