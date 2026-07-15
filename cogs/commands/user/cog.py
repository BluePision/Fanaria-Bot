from ._sub_commands import cmd_avater, cmd_banner

from discord import Object
from discord.ext import commands

from ._group import user_group
from configs.main import OwnerGuildID

guild = Object(id=OwnerGuildID)

class UserCommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        self.bot.tree.add_command(
            user_group,
            guild=guild
        )

    async def cog_unload(self):
        self.bot.tree.remove_command(
            user_group.name,
            guild=guild
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(UserCommandsCog(bot))
