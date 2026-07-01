from discord import app_commands

from configs.main import OwnerGuildID

user_group = app_commands.Group(
    name = "user",
    description = "ユーザー関連のコマンド",
    guild_only = True
)