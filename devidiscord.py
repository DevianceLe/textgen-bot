#Discord Textgen UI Bot 0.4

import discord
from discord.ext import commands
import aiohttp
import asyncio

# Define intents
intents = discord.Intents.all()
intents.messages = True  # Enable the message intent

# Create a bot instance with intents
bot = commands.Bot(command_prefix='!', intents=intents)

url = "http://127.0.0.1:5000/v1/chat/completions"
headers = {
    "Content-Type": "application/json"
}
history = []
message_queue = asyncio.Queue()  # Use asyncio.Queue for asynchronous processing
queue_counter = 0  # Variable to keep track of the number of messages in the queue

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

    # Start processing the message queue
    bot.loop.create_task(process_queue())

# Event: Message is received
@bot.event
async def on_message(message):
    # Ignore messages from the bot itself to prevent an infinite loop
    if message.author == bot.user:
        return

    # Start typing in the channel to simulate the bot is typing
    async with message.channel.typing():
        # Process the user's message
        user_message = message.content
        user_nickname = message.author.display_name  # Get the Discord nickname
        history.append({"role": "user", "content": f"{user_nickname}: {user_message}"})

        data = {
            "mode": "chat",
            "character": "Name goes here",
            "messages": history,
            "Preset": "Preset goes here"
        }

        # Enqueue the message for processing
        await message_queue.put((message, data))
        global queue_counter
        queue_counter += 1
        print(f"Message added to queue. Queue size: {queue_counter}")

# Function to process the message queue
async def process_queue():
    global queue_counter
    while True:
        if not message_queue.empty():
            print("Processing message queue...")
            # Dequeue the message
            message, data = await message_queue.get()

            # Process the message
            await process_message(message, data)
            queue_counter -= 1
            print(f"Message processed. Queue size: {queue_counter}")
        else:
            print("Message queue is empty. Waiting for messages...")
            await asyncio.sleep(5)  # Adjust the sleep duration as needed

# Function to process a single message
async def process_message(message, data):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
                assistant_message = (await response.json())['choices'][0]['message']['content']

        assistant_nickname = "Namegoeshere"  # Replace with the assistant's nickname if available

        # Debugging
        user_nickname = message.author.display_name
        print(f"User: {user_nickname}: {message.content}")
        print(f"Assistant: {assistant_nickname}: {assistant_message}")

        # Split the assistant's message into chunks of 2000 characters
        for chunk in [assistant_message[i:i + 2000] for i in range(0, len(assistant_message), 2000)]:
            # Respond to the Discord channel with each chunk
            await message.channel.send(chunk)

    except aiohttp.ClientError as e:
        print(f"Error communicating with the API: {e}")
        await message.channel.send("Sorry, there was an error processing your request.")

# Run the bot
bot.run('Token')  # Replace with your bot token
