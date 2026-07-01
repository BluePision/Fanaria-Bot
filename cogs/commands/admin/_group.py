from discord import app_commands, Permissions

from configs.main import OwnerGuildID

admin_group = app_commands.Group(
    name = "admin",
    description = "管理者用のコマンド",
    default_permissions = Permissions(administrator=True),
    guild_only = True
)