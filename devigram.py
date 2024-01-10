#Textgen Telegram Bot

import logging
import requests
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging for debugging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

#OpenAI Equiv API we are accessing
url = "http://127.0.0.1:5000/v1/chat/completions"
headers = {"Content-Type": "application/json"}
history = []


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued. Makes sure it's talking pretty much"""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )



async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process the user's message through an external API."""
    user_message = update.message.text
    user_nickname = update.message.from_user.username

    history.append({"role": "user", "content": f"{user_nickname}: {user_message}"})

    data = {
        "mode": "chat",
        "character": "Character goes here",
        "messages": history,
        "Preset": "Preset goes here",
    }
    response = requests.post(url, headers=headers, json=data, verify=False)
    assistant_message = response.json()["choices"][0]["message"]["content"]
    assistant_nickname = "Namegoeshere"  # Replace with the assistant's nickname if available
    logger.info(f"User: {user_nickname}: {user_message}")
    logger.info(f"Assistant: {assistant_nickname}: {assistant_message}")

    for chunk in [assistant_message[i : i + 4096] for i in range(0, len(assistant_message), 4096)]:
        await update.message.reply_text(chunk)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("Bot token goes here").build()

    # on non-command i.e message - process the message through an external API
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
