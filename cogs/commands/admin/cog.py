from .moderation import _group, _com_ban, _com_kick, _com_timeout

from discord import Object
from discord.ext import commands

from ._group import admin_group
from configs.main import OwnerGuildID

guild = Object(id=OwnerGuildID)

class AdminCommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.tree.add_command(
            admin_group,
            guild=guild
        )

    async def cog_unload(self):
        self.bot.tree.remove_command(
            admin_group.name,
            guild=guild
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommandsCog(bot))
