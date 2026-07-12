import discord
from discord.ext import commands
import asyncio
from functools import wraps
from typing import Optional

from configs.main import OwnerGuildID, FiestarChannelID
from configs.fiestar_config import emoji_map
from database.fiestar_db import FiestarDB


def is_true_channel(func):
    @wraps(func)
    async def wrapper(self, obj, *args, **kwargs):
        if isinstance(obj, discord.Message):
            if not obj.guild:
                return

            guild_id = obj.guild.id
            channel_id = obj.channel.id

        elif isinstance(obj, discord.RawReactionActionEvent):
            if not obj.guild_id:
                return

            guild_id = obj.guild_id
            channel_id = obj.channel_id

        else:
            return

        if guild_id != OwnerGuildID:
            return

        if channel_id != FiestarChannelID:
            return

        return await func(self, obj, *args, **kwargs)

    return wrapper

class Fiestar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.database = FiestarDB()

    def cog_unload(self):
        self.database.close()

    async def get_channel(self) -> Optional[discord.TextChannel]:
        """キャッシュとAPIを使ってチャンネルを返す"""

        channel = self.bot.get_channel(FiestarChannelID)
        if isinstance(channel, discord.TextChannel):
            self.channel = channel
            return channel

        try:
            channel = await self.bot.fetch_channel(FiestarChannelID)
            self.channel = channel
            return channel

        except Exception:
            return None

    async def get_user(self, user_id: int) -> discord.User:
        user = self.bot.get_user(user_id)
        if not user:
            user = await self.bot.fetch_user(user_id)

        return user

    # メッセージ
    @commands.Cog.listener("on_message")
    @is_true_channel
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        await message.add_reaction("👍")
        await asyncio.sleep(0.1)
        await message.add_reaction("⭐")
        await asyncio.sleep(0.1)
        await message.add_reaction("❤️")
        await asyncio.sleep(0.1)
        await message.add_reaction("🔁")
        await asyncio.sleep(0.1)
        await message.add_reaction("🔖")
        await asyncio.sleep(0.1)

        await message.create_thread(
            name=f"{message.author.name} [{message.author.id}] の投稿のコメント欄",
            auto_archive_duration=1440
        )

    # リアクション部分
    @commands.Cog.listener("on_raw_reaction_add")
    @is_true_channel
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        channel = await self.get_channel()
        if channel is None:
            return

        user = await self.get_user(payload.user_id)

        if user.bot:
            return

        emoji = str(payload.emoji)

        reaction_type = emoji_map.get(emoji)
        if reaction_type is None:
            return

        if not self.database.has_reaction(
            payload.user_id,
            reaction_type,
            payload.message_id
        ):
            self.database.add_reaction(
                payload.user_id,
                reaction_type,
                payload.message_id
            )

        if reaction_type == "repost":
            message = discord.utils.get(
                self.bot.cached_messages,
                id=payload.message_id
            )
            if message is None:
                try:
                    message = await channel.fetch_message(payload.message_id)

                except discord.NotFound:
                    return

            main_embed = discord.Embed(
                description=message.content,
                color=user.accent_color or discord.Color.blue(),
                timestamp=message.created_at,
                url=message.jump_url
            )
            main_embed.set_footer(
                text=f"{user.display_name} | {payload.user_id} さんがリポストしました",
                icon_url=user.display_avatar.url
            )

            embeds = [main_embed]
            main_image_url = False

            if message.attachments:
                for attachment in message.attachments:
                    if attachment.content_type and attachment.content_type.startswith("image"):

                        if not main_image_url:
                            main_embed.set_image(url=attachment.url)
                            main_image_url = True
                            continue

                        image_embed = discord.Embed(url=message.jump_url)
                        image_embed.set_image(url=attachment.url)
                        embeds.append(image_embed)

            await message.reply(embeds=embeds, mention_author=False)

    @commands.Cog.listener("on_raw_reaction_remove")
    @is_true_channel
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        channel = await self.get_channel()
        if channel is None:
            return

        user = await self.get_user(payload.user_id)

        if user.bot:
            return

        emoji = str(payload.emoji)

        reaction_type = emoji_map.get(emoji)
        if reaction_type is None:
            return

        self.database.remove_reaction(
            payload.user_id,
            reaction_type,
            payload.message_id
        )

        if reaction_type == "repost":
            message = discord.utils.get(
                self.bot.cached_messages,
                id=payload.message_id
            )
            if message is None:
                try:
                    message = await channel.fetch_message(payload.message_id)

                except discord.NotFound:
                    return

            replies = [
                msg async for msg in channel.history(limit=100)
                if msg.reference and msg.reference.message_id == message.id
            ]

            for reply in replies:
                if reply.embeds:
                    embed = reply.embeds[0]
                    footer = embed.footer.text if embed.footer else ""
                    if f"{payload.user_id} さんがリポストしました" in footer or f"{payload.user_id} さんがリツイートしました" in footer:
                        await reply.delete()
                        break

    @commands.Cog.listener("on_message_delete")
    @is_true_channel
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return

        thread = message.thread

        if thread is None:
            try:
                thread = await self.bot.fetch_channel(message.id)

            except discord.NotFound:
                thread = None

            except discord.HTTPException as e:
                print(f"スレッド削除失敗: {e}")

        if thread is not None:
            await thread.delete(
                reason="元投稿が削除されたため"
            )

        self.database.remove_message(message.id)

async def setup(bot: commands.Bot):
    await bot.add_cog(Fiestar(bot))
