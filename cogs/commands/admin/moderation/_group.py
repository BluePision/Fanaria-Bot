from discord import app_commands

from configs.main import OwnerGuildID
from .._group import admin_group

moderation_group = app_commands.Group(
    name = "moderation",
    description = "モデレーション関連のコマンド",
    parent = admin_group,
    guild_only = True
)