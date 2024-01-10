#Discord Textgen UI Bot 0.3

import discord
from discord.ext import commands
import requests
import asyncio

# Define intents
intents = discord.Intents.all()
intents.messages = True  # Enable the message intent

# Create a bot instance with intents
bot = commands.Bot(command_prefix='!', intents=intents)

# API URL for OpenAI Equiv
url = "http://127.0.0.1:5000/v1/chat/completions"
headers = {
    "Content-Type": "application/json"
}
history = []

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

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
            "character": "Character goes here!",
            "messages": history,
            "Preset": "Preset goes here"
        }

        # Make a request to the external API
        response = requests.post(url, headers=headers, json=data, verify=False)
        assistant_message = response.json()['choices'][0]['message']['content']
        assistant_nickname = "Jesus"  # Replace with the assistant's nickname if available

        # Debugging
        print(f"User: {user_nickname}: {user_message}")
        print(f"Assistant: {assistant_nickname}: {assistant_message}")

        # Split the assistant's message into chunks of 2000 characters
        for chunk in [assistant_message[i:i+2000] for i in range(0, len(assistant_message), 2000)]:
            # Respond to the Discord channel with each chunk
            await message.channel.send(chunk)

        # Process other commands (if any)
        await bot.process_commands(message)

# Run the bot
bot.run('token goes here')  # Replace with your bot token
