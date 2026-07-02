import discord
import os
import signal
import asyncio
from pathlib import Path
from discord import app_commands, AppCommandOptionType
from discord.app_commands.models import AppCommand, Argument, AppCommandGroup
from discord.ext import commands
from typing import Optional, List
from dotenv import load_dotenv

from cogs import BotLog, UpdateInfo
from configs.main import OwnerGuildID


BASE_DIR = Path(__file__).resolve().parent

load_dotenv()
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise RuntimeError("TOKEN が設定されていません。環境変数を確認してください。")

bot = commands.Bot(
    command_prefix=["f!", "fa!", "fanaria!"],
    intents=discord.Intents.all(),
    owner_ids=[
        1102936594362671235,
        1333027499302453273,
        377029059886055424
    ]
)

# フラグ: on_ready の一度だけ実行用
_ready_handled = False

botlog: Optional[BotLog] = None

update_info: Optional[UpdateInfo] = None

guild = discord.Object(id=OwnerGuildID)

async def graceful_shutdown():
    """終了時に実行する非同期クリーンアップ処理"""
    print("シャットダウン処理開始...")

    global botlog
    if botlog is not None:
        await botlog.send(embed=discord.Embed(
            title="ログアウトします",
            description="おやすみなさい",
            color=discord.Color.blue()
        ))

    # 全ての Cog をアンロード
    for ext_name in list(bot.extensions.keys()):
        try:
            await bot.unload_extension(ext_name)
            print(f"{ext_name} をアンロード")

        except Exception as e:
            print(f"{ext_name} のアンロードに失敗:\n{e}")

    # 必要ならここで状態保存や DB 切断などを行う
    # await save_state()
    # await db.close()

    try:
        await bot.close()
        print("Botからログアウトしました")

    except Exception as e:
        print(f"ログアウトに失敗しました:\n{e}")

def _schedule_shutdown():
    """イベントループ上で graceful_shutdown をスケジュールするヘルパー"""
    try:
        loop = asyncio.get_running_loop()

    except RuntimeError:
        loop = asyncio.get_event_loop()

    loop.create_task(graceful_shutdown())

# シグナルハンドラを登録
for sig in (signal.SIGINT, signal.SIGTERM):
    try:
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(sig, _schedule_shutdown)

    except (NotImplementedError, RuntimeError):
        signal.signal(sig, lambda *_: _schedule_shutdown())


CORE_BOTLOG_MODULE = "cogs.cog_process.botlog"

async def load_core_botlog():
    """最初に BotLog をロードして初期化する（失敗しても続行）"""
    if CORE_BOTLOG_MODULE in bot.extensions:
        print(f"{CORE_BOTLOG_MODULE} は既にロード済みです")
        return

    try:
        await bot.load_extension(CORE_BOTLOG_MODULE)
        print(f"{CORE_BOTLOG_MODULE} を先にロードしました")

        # BotLogのCogを取得
        global botlog
        botlog = bot.get_cog("BotLog")

        if botlog is None:
            print("BotLog Cog が見つかりません")
            return

        # 初期化
        try:
            await botlog.initialize()
            print("BotLog を初期化しました")

        except Exception as e:
            print(f"BotLog の初期化に失敗: {e}")

    except Exception as e:
        print(f"{CORE_BOTLOG_MODULE} のロードに失敗: {e}")

async def load_cogs(base_path: str = "cogs") -> int:
    """Cogsをロードし、ロードされたCogsの数を返す"""
    base = BASE_DIR / base_path
    if not base.exists():
        print(f"{base_path} が見つかりません。")
        return

    loaded = 0

    for py in base.rglob("*.py"):
        if py.name.startswith("_"):
            continue
        # cogs/foo/bar.py -> cogs.foo.bar
        module_path = ".".join(py.with_suffix("").parts)
        # Windows の場合パスにドライブ名が入ることがあるので cogs 以降を切り出す
        if "cogs." in module_path:
            module_path = module_path[module_path.index("cogs."):]
        else:
            # 期待外の場所ならスキップ
            continue

        if module_path == CORE_BOTLOG_MODULE:
            loaded += 1
            continue

        if module_path in bot.extensions:
            print(f"既にロード済み: {module_path} をスキップ")
            continue

        try:
            await bot.load_extension(module_path)
            loaded += 1
            print(f"{module_path} をロード")

        except Exception as e:
            print(f"{module_path} のロードに失敗: {e}")

    return loaded

def count_commands(commands: list[AppCommand]) -> int:
    def count_options(
        options: list[Argument | AppCommandGroup]
    ) -> int:
        count = 0

        for option in options:
            if isinstance(option, Argument):
                continue

            if option.type is AppCommandOptionType.subcommand:
                print(f"+1 subcommand: {option.name}")
                count += 1

            elif option.type is AppCommandOptionType.subcommand_group:
                print(f"subcommand_group: {option.name}")
                count += count_options(option.options)

        return count

    count = 0

    for command in commands:
        print(f"+command: {command.name}")

        if not command.options:
            print(f"+1 command: {command.name}")
            count += 1
            continue

        if all(isinstance(opt, Argument) for opt in command.options):
            print(f"+1 command: {command.name}")
            count += 1
            continue

        count += count_options(command.options)

    return count

@bot.event
async def on_ready():
    """起動時の処理"""
    global _ready_handled, botlog, update_info

    if _ready_handled:
        print(f"{bot.user} に再接続")

        if botlog is not None:
            await botlog.send(embed=discord.Embed(
                title="再接続しました",
                color=discord.Color.blue()
            ))
        return

    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Activity(type=discord.ActivityType.playing, name="起動準備中")
    )

    _ready_handled = True

    bot.tree.clear_commands(guild=None)
    bot.tree.clear_commands(guild=guild)

    print(f"{bot.user} としてログイン")

    # Cogs をロード
    await load_core_botlog()
    loaded = await load_cogs()
    print("全てのCogをロードしました")
    if botlog is not None:
        await botlog.send(embed=discord.Embed(
            title="ログインしました",
            description=f"{str(bot.user)} です\nおはようございます！\n\n{loaded}件のCogsがロードされました",
            color=discord.Color.blue()
        ))

    # アプリコマンドを同期
    try:
        await bot.tree.sync()
        synced = await bot.tree.sync(guild=guild)
        command_count = count_commands(synced)

        print(f"同期されたコマンドの数: {command_count}")
        if botlog is not None:
            await botlog.send(embed=discord.Embed(
                description=f"{command_count}個のアプリコマンドが同期されました",
                color=discord.Color.blue()
            ))

    except Exception as e:
        print(f"コマンドの同期に失敗しました: {e}")

    update_info = UpdateInfo(bot)

    await update_info.initialize()

    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.CustomActivity(name="起動しました")
    )

async def send_command_error(interaction: discord.Interaction, error_message: str):
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(error_message, ephemeral=True)
        else:
            await interaction.followup.send(error_message, ephemeral=True)

    except Exception:
        print(f"エラーメッセージの送信に失敗しました\nerror_message: {error_message}")

    return

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        if isinstance(error, app_commands.CommandOnCooldown):
            await send_command_error(interaction, f"クールダウン中です。あと {error.retry_after:.1f} 秒待ってください。")
            return

        await send_command_error(interaction, "このコマンドを実行する権限がありません。必要な権限を持っているか確認してください。")
        return

if __name__ == "__main__":
    try:
        bot.run(TOKEN)

    except KeyboardInterrupt:
        print("KeyboardInterrupt: シャットダウンを開始")
        _schedule_shutdown()
        try:
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(1))

        except Exception:
            pass
