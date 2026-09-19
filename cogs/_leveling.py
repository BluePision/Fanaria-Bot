import discord
from discord.ext import commands, tasks
from functools import wraps
from typing import Optional

from configs.main import OwnerGuildID


def is_true_channel(func):
    @wraps(func)
    async def wrapper(self, obj, *args, **kwargs):
        if isinstance(obj, discord.Message):
            if not obj.guild:
                return

            guild_id = obj.guild.id

        elif isinstance(obj, discord.RawReactionActionEvent):
            if not obj.guild_id:
                return

            guild_id = obj.guild_id

        else:
            return

        if guild_id != OwnerGuildID:
            return

        return await func(self, obj, *args, **kwargs)

    return wrapper

class LevelingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # メッセージ
    @commands.Cog.listener("on_message")
    @is_true_channel
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

    @commands.Cog.listener("on_message_delete")
    @is_true_channel
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return

async def setup(bot: commands.Bot):
    await bot.add_cog(LevelingCog(bot))
