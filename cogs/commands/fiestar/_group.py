from discord import app_commands

from configs.main import OwnerGuildID

fiestar_group = app_commands.Group(
    name = "fiestar",
    description = "Fiestar関連のコマンド",
    guild_only = True
)