from dotenv import load_dotenv
import os
import logging
import json
from typing import Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ApplicationBuilder,
)

# --- Configuration ---

# Load environment variables from the .env file
load_dotenv()

# Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ANNA_TELEGRAM_CHAT_ID = os.getenv('ANNA_TELEGRAM_CHAT_ID') 
WEBHOOK_URL = os.getenv('WEBHOOK_URL') 
PORT = int(os.getenv('PORT', '5000'))
WEBHOOK_PATH = os.getenv('WEBHOOK_PATH', '/telegram-webhook')
WEBHOOK_SECRET_TOKEN = os.getenv('WEBHOOK_SECRET_TOKEN') 

# --- Logging Configuration ---

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
    handlers=[
        logging.FileHandler('bot.log'),  # Log to a file named 'bot.log'
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger(__name__)

# --- Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message and options when the command /start is issued."""
    keyboard = [
        [InlineKeyboardButton("Get Updates", callback_data='get_updates')],
        [InlineKeyboardButton("Learn More", callback_data='learn_more')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Welcome! I am Anna Ena\'s notification bot. How can I help you?',
        reply_markup=reply_markup
    )
    logger.info("Executed /start command")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the command /help is issued."""
    await update.message.reply_text(
        'I can provide updates and information about Anna Ena\'s English courses. Use /start to see available options.'
    )
    logger.info("Executed /help command")

# --- Callback Query Handler ---

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles button presses."""
    query = update.callback_query
    await query.answer()

    if query.data == 'get_updates':
        await query.edit_message_text(
            text="You'll receive updates about new courses and enrollment opportunities."
        )
        logger.info("User selected 'Get Updates'")
    elif query.data == 'learn_more':
        await query.edit_message_text(
            text="Visit [Anna Ena's Website](https://www.annaena.com) to learn more about her English courses.",
            parse_mode='Markdown'
        )
        logger.info("User selected 'Learn More'")

# --- Webhook Handler ---

async def webhook_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming webhook requests from Gravity Forms."""
    try:
        logger.debug(f"Received update: {update.to_dict()}")  # Log the full update object

        message = update.message

        if message is None or message.text is None:
            logger.error("Received update without message text.")
            return

        # Assuming Gravity Forms sends data as JSON string in the message text
        try:
            data = json.loads(message.text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return

        # Extracting relevant data; field names depend on Gravity Forms configuration
        form_name = data.get('form_name', 'Unknown Form')
        entry_id = data.get('entry_id', 'Unknown Entry ID')
        # Add more fields as necessary

        # Construct the notification message
        notification_message = f"📬 *New Form Submission!*\n\n"
        notification_message += f"*Form:* {form_name}\n"
        notification_message += f"*Entry ID:* {entry_id}\n"
        # Add more details from the data as desired

        # Send the notification to Anna
        await context.bot.send_message(
            chat_id=ANNA_TELEGRAM_CHAT_ID,
            text=notification_message,
            parse_mode='Markdown'
        )

        # Optionally, acknowledge receipt to the sender
        await message.reply_text("Thank you for your submission!")

        logger.info("Processed a webhook request successfully")

    except Exception as e:
        logger.exception(f"Error processing webhook: {e}")

# --- Error Handler ---

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a user-friendly message."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    if update and isinstance(update, Update) and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="An unexpected error occurred. The administrators have been notified."
            )
            logger.info("Notified user of an unexpected error")
        except Exception as e:
            logger.error(f"Failed to send error message to user: {e}")

# --- Main Function ---

def main() -> None:
    """Start the bot."""

    # Ensure that the necessary environment variables are set
    missing_vars = []
    if TELEGRAM_BOT_TOKEN is None:
        missing_vars.append('TELEGRAM_BOT_TOKEN')
    if ANNA_TELEGRAM_CHAT_ID is None:
        missing_vars.append('ANNA_TELEGRAM_CHAT_ID')
    if WEBHOOK_URL is None:
        missing_vars.append('WEBHOOK_URL')
    if missing_vars:
        logger.critical(f"Missing required environment variables: {', '.join(missing_vars)}")
        exit(1)

    # Build the application
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, webhook_handler))
    application.add_error_handler(error_handler)

    # Set up webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_PATH,
        webhook_url=f"{WEBHOOK_URL}{WEBHOOK_PATH}",
        secret_token=WEBHOOK_SECRET_TOKEN  # Optional; can be None
    )

    # Uncomment for testing with polling mode
    # application.run_polling()

if __name__ == '__main__':
    main()
