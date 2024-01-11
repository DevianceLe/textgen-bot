#Telegram Textgen UI Bot 0.4

import logging
import requests
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from queue import Queue
import threading
import time
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

url = "http://127.0.0.1:5000/v1/chat/completions"
headers = {"Content-Type": "application/json"}
history = []

response_queue = Queue()
queue_lock = threading.Lock()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
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
        "character": "Jesus",
        "messages": history,
        "Preset": "Divine Intellect",
    }

    response = requests.post(url, headers=headers, json=data, verify=False)
    assistant_message = response.json()["choices"][0]["message"]["content"]
    assistant_nickname = "Jesus"  # Replace with the assistant's nickname if available

    logger.info(f"User: {user_nickname}: {user_message}")
    logger.info(f"Assistant: {assistant_nickname}: {assistant_message}")

    with queue_lock:
        response_queue.put(assistant_message)

    for chunk in [assistant_message[i : i + 4096] for i in range(0, len(assistant_message), 4096)]:
        await update.message.reply_text(chunk)


def process_queue():
    """Process the response queue and print the count in the console."""
    while True:
        with queue_lock:
            queue_size = response_queue.qsize()
        logger.info(f"Response queue size: {queue_size}")
        time.sleep(5)

        # You can add additional logic to handle the queue content if needed
        # For example, sending the responses to a different service, saving to a file, etc.
        # For now, we are just logging the size of the queue.


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("tokengohere").build()

    # on non-command i.e message - process the message through an external API
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_message))

    # Start the queue processing thread
    queue_thread = threading.Thread(target=process_queue, daemon=True)
    queue_thread.start()

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
