import discord
import os
import signal
import asyncio
from pathlib import Path
from discord.ext import commands
from discord.app_commands import AppCommandContext
from typing import Optional
from dotenv import load_dotenv

import traceback

from cogs import BotLog
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

print(discord.__version__)
print(type(bot.tree.allowed_contexts))
print(bot.tree.allowed_contexts)

# フラグ: on_ready の一度だけ実行用
_ready_handled = False

botlog: Optional[BotLog] = None

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

@bot.event
async def on_ready():
    """起動時の処理"""
    global _ready_handled, botlog

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
    print("before sync:", bot.tree.get_commands())
    try:
        synced = await bot.tree.sync()
        synced = await bot.tree.sync(guild=guild)
        print("after sync:", synced)
        print(f"同期されたコマンドの数: {len(synced)}")
        if botlog is not None:
            await botlog.send(embed=discord.Embed(
                description=f"{len(synced)}個のアプリコマンドが同期されました",
                color=discord.Color.blue()
            ))

    except Exception as e:
        print(f"コマンドの同期に失敗しました: {e}")
        traceback.print_exc()

    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.CustomActivity(name="起動しました")
    )

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
