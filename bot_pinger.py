"""
╔══════════════════════════════════════════════════╗
║         TELEGRAM БОТ-ПИНГЕР v1.0                 ║
║   Пинг сам себя или другого бота каждые 30 сек   ║
╚══════════════════════════════════════════════════╝
"""
import logging
import asyncio
import aiohttp
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os

BOT_TOKEN = os.environ.get("PINGER_BOT_TOKEN")
TARGET_URL = os.environ.get("TARGET_URL")
PING_INTERVAL = int(os.environ.get("PING_INTERVAL", 30))

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

ping_task = None
session = None

async def ping_target():
    global session
    try:
        async with session.get(TARGET_URL, timeout=10) as response:
            logger.info(f"✅ Пинг {TARGET_URL} - статус: {response.status}")
            return response.status
    except Exception as e:
        logger.error(f"❌ Ошибка пинга: {e}")
        return None

async def scheduled_pinger():
    while True:
        await ping_target()
        await asyncio.sleep(PING_INTERVAL)

async def start_pinger(update, context):
    global ping_task
    if ping_task and not ping_task.done():
        await update.message.reply_text("🔄 Пингер уже запущен!")
        return
    ping_task = asyncio.create_task(scheduled_pinger())
    await update.message.reply_text(f"✅ Пингер запущен!\n🎯 Цель: {TARGET_URL}\n⏱️ Интервал: {PING_INTERVAL} сек.")

async def stop_pinger(update, context):
    global ping_task
    if ping_task and not ping_task.done():
        ping_task.cancel()
        ping_task = None
        await update.message.reply_text("🛑 Пингер остановлен!")
    else:
        await update.message.reply_text("❌ Пингер не был запущен")

async def status(update, context):
    if ping_task and not ping_task.done():
        await update.message.reply_text(f"🟢 Пингер активен\n🎯 Цель: {TARGET_URL}\n⏱️ Интервал: {PING_INTERVAL} сек.")
    else:
        await update.message.reply_text("🔴 Пингер не активен")

async def ping_now(update, context):
    await update.message.reply_text("🔄 Выполняю пинг...")
    status_code = await ping_target()
    if status_code:
        await update.message.reply_text(f"✅ Пинг выполнен! HTTP статус: {status_code}")
    else:
        await update.message.reply_text("❌ Ошибка при пинге!")

async def start(update, context):
    await update.message.reply_text(
        f"🤖 *Бот-пингер v1.0*\n\n"
        f"🎯 Цель: `{TARGET_URL}`\n"
        f"⏱️ Интервал: {PING_INTERVAL} сек.\n\n"
        f"*Команды:*\n"
        f"`/start_pinger` — запустить пингер\n"
        f"`/stop_pinger` — остановить пингер\n"
        f"`/ping_now` — пинг сейчас\n"
        f"`/status` — статус пингера",
        parse_mode="Markdown"
    )

def main():
    global session
    if not BOT_TOKEN:
        logger.error("❌ Нет PINGER_BOT_TOKEN!")
        return
    if not TARGET_URL:
        logger.error("❌ Нет TARGET_URL!")
        return
    session = aiohttp.ClientSession()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("start_pinger", start_pinger))
    app.add_handler(CommandHandler("stop_pinger", stop_pinger))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("ping_now", ping_now))
    logger.info("✅ Бот-пингер запущен!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
