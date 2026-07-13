from . import _com_avater, _com_banner

from discord import Object
from discord.ext import commands

from ._group import tool_group
from configs.main import OwnerGuildID

guild = Object(id=OwnerGuildID)

class ToolCommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.tree.add_command(
            tool_group,
            guild=guild
        )

    async def cog_unload(self):
        self.bot.tree.remove_command(
            tool_group.name,
            guild=guild
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(ToolCommandsCog(bot))
