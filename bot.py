# bot.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackContext
from telegram.error import TelegramError, NetworkError, Forbidden, BadRequest
import os
import logging
import asyncio
from dotenv import load_dotenv
from typing import Optional

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://roadtop-miniapp.onrender.com")


async def start(update: Update, _: CallbackContext) -> None:
    """Handle the /start command."""
    try:
        web_app_info = WebAppInfo(url=WEB_APP_URL)
        keyboard = [[InlineKeyboardButton("📍 Открыть RoadTop", web_app=web_app_info)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🌟 **RoadTop** — топовые места в пути.\n\n"
            "📍 Введи адрес — построим маршрут\n"
            "🎯 Добавляй лучшие кофейни, барберы, обеды\n\n"
            "Нажми кнопку ниже!",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        logger.info(f"Start command used by user: {update.effective_user.id}")
    except (TelegramError, NetworkError, BadRequest) as telegram_err:
        logger.error(f"Error in start command: {telegram_err}")
        await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")
    except Forbidden:
        logger.warning(f"Bot blocked by user: {update.effective_user.id}")
    except Exception as unexpected_err:
        logger.error(f"Unexpected error in start command: {unexpected_err}")


async def help_command(update: Update, _: CallbackContext) -> None:
    """Handle the /help command."""
    try:
        await update.message.reply_text(
            "📌 RoadTop — твой личный гид.\n\n"
            "🔹 Вводи 'откуда' и 'куда'\n"
            "🔹 Смотри маршрут по карте\n"
            "🔹 Находи топ-места в пути\n\n"
            "Всё работает через mini app!"
        )
        logger.info(f"Help command used by user: {update.effective_user.id}")
    except (TelegramError, NetworkError, BadRequest) as telegram_err:
        logger.error(f"Error in help command: {telegram_err}")
        await update.message.reply_text("❌ Произошла ошибка при показе справки.")
    except Forbidden:
        logger.warning(f"Bot blocked by user: {update.effective_user.id}")
    except Exception as unexpected_err:
        logger.error(f"Unexpected error in help command: {unexpected_err}")


async def error_handler(update: Optional[Update], context: CallbackContext) -> None:
    """Handle errors in the bot."""
    try:
        # Log the error with more details from context
        error_message = f"Error occurred: {context.error}"
        if update:
            error_message += f" in update: {update.update_id}"
        logger.error(error_message)

        # Log the full traceback if available
        if hasattr(context, 'error') and context.error:
            logger.exception("Exception details:", exc_info=context.error)

        # Send error message to user if possible
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text("❌ Произошла ошибка. Попробуйте позже.")
            except (TelegramError, NetworkError, BadRequest, Forbidden) as send_err:
                logger.error(f"Failed to send error message: {send_err}")
    except Exception as handler_err:
        logger.error(f"Error in error_handler: {handler_err}")


def main() -> None:
    """Run the Telegram bot with proper error handling."""
    if not TOKEN:
        logger.error("TELEGRAM_TOKEN not found in environment variables")
        return

    if not WEB_APP_URL or WEB_APP_URL == "https://roadtop-miniapp.onrender.com":
        logger.warning("Using default Web App URL. Consider setting WEB_APP_URL in .env file")

    try:
        # Create application
        application = Application.builder().token(TOKEN).build()

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))

        # Add error handler
        application.add_error_handler(error_handler)

        logger.info("Starting bot...")

        # Start polling with proper error handling
        async def run_polling():
            try:
                await application.initialize()
                await application.start()
                await application.updater.start_polling(
                    drop_pending_updates=True,
                    allowed_updates=Update.ALL_TYPES
                )
                logger.info("Bot is now running. Press Ctrl+C to stop.")

                # Keep the application running
                await asyncio.Event().wait()

            except (KeyboardInterrupt, SystemExit):
                logger.info("Bot stopped by user")
            except Exception as polling_err:
                logger.error(f"Unexpected error in polling: {polling_err}")
            finally:
                if application.updater:
                    await application.updater.stop()
                await application.stop()
                await application.shutdown()

        # Run the bot
        asyncio.run(run_polling())

    except Exception as startup_err:
        logger.error(f"Failed to start bot: {startup_err}")


if __name__ == "__main__":
    main()
