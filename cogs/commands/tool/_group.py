from discord import app_commands, Permissions

from configs.main import OwnerGuildID

tool_group = app_commands.Group(
    name = "tool",
    description = "おふざけツールコマンド",
    guild_only = True
)