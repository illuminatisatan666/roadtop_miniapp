# bot.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📍 Открыть RoadTop", web_app={"url": os.getenv("WEB_APP_URL", "https://roadtop.onrender.com")})]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🌟 **RoadTop** — топовые места в пути.\n\n"
        "📍 Введи адрес — построим маршрут\n"
        "🎯 Добавляй лучшие кофейни, барберы, обеды\n\n"
        "Нажми кнопку ниже!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 RoadTop — твой личный гид.\n\n"
        "🔹 Вводи 'откуда' и 'куда'\n"
        "🔹 Смотри маршрут по карте\n"
        "🔹 Находи топ-места в пути\n\n"
        "Всё работает через mini app!"
    )

def run_bot():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.run_polling()