import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! You are now connected to the notification bot.')

async def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text('Help!')

if __name__ == '__main__':
    app = ApplicationBuilder().token("7098919168:AAF_n7g1D49w1Lbs0_xBpSgwFmUrVf3Mmu8").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    app.run_polling()
