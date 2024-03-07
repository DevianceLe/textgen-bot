#Deviance's TextGEN Bot 0.8
#It remembers!

# Variables for customization
YOUR_BOT_TOKEN = '-Pass the token to the left hand side-'
DATABASE_NAME = 'message_history.db'
API_URL = "http://127.0.0.1:5000/v1/chat/completions"
HEADERS = {"Content-Type": "application/json"}

#These Settings Are Temporary Until I Allow You To Change It Within The Discord Room
BOT_PREFIX = "!"  # Change if you prefer a different prefix

#These Settings It Pulls From the API
CHARACTER_NAME = "Jesus"  # Change the character name here from the textgen ui
PRESET_NAME = "mine"  # Change the preset name here
CHAT_MODE = "chat"  # Change the chat mode here 


#Let's Begin!

#Import me baby!
import discord
from discord.ext import commands
import aiohttp
import asyncio
import sqlite3
import shutil
import os

def clear_console():
    # Clear the console based on the operating system
    os.system('cls' if os.name == 'nt' else 'clear')

clear_console()
def generate_banner():
    banner = """
===========================================
* Deviance's Textgen Chat Bot for Discord *
*                            -Version 0.8 *
*                                         *
===========================================
* Greets to Sang (WWelna), Tex Santos     *
===========================================    
    """
    print(banner)

if __name__ == "__main__":
    generate_banner()


print("=Initializing DB=")
# SQLite connection
conn = sqlite3.connect(DATABASE_NAME)
cursor = conn.cursor()

# Create the messages table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        channel_id INTEGER,
        user_id INTEGER,
        nickname TEXT,
        content TEXT
    )
''')
conn.commit()

# Create a bot instance with intents
message_queue = asyncio.Queue()
intents = discord.Intents.all()
intents.messages = True
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

# Function to check if the author is the owner of the channel
# Don't need skids
def is_channel_owner(ctx):
    return ctx.author == ctx.guild.owner

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'=Logged in as {bot.user.name} ({bot.user.id})=')
    print("=Let The Fun Begin=")
    # Start processing the message queue
    bot.loop.create_task(process_queue())

# Event: Message is received
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    async with message.channel.typing():
        user_message = message.content
        user_nickname = message.author.display_name
        user_id = message.author.id
        channel_id = message.channel.id
        save_message(channel_id, user_id, get_member_nickname(message.author, message.guild), f"{user_nickname}: {user_message}")
        mentioned_user_ids = [mention.id for mention in message.mentions]
        for mentioned_user_id in mentioned_user_ids:
            mentioned_user = message.guild.get_member(mentioned_user_id)
            if mentioned_user:
                mentioned_user_message = f"{get_member_nickname(message.author, message.guild)} mentioned you: {user_message}"
                save_message(channel_id, mentioned_user_id, get_member_nickname(mentioned_user, message.guild), mentioned_user_message)

                # Save the mentioned user message to SQLite
                save_message(channel_id, mentioned_user_id, get_member_nickname(mentioned_user, message.guild), mentioned_user_message)

        data = {
            "mode": CHAT_MODE,  # Use the chat mode variable
            "character": CHARACTER_NAME, #Use the variable
            "messages": get_user_history(channel_id, user_id), 
            "Preset": PRESET_NAME,  # Use the preset name variable
        }

        # Enqueue the message for processing
        await message_queue.put((message, data))

    await bot.process_commands(message)

# Command: Clear all messages from the channel database (only for the channel owner)
@bot.command(name='clearall')
@commands.check(is_channel_owner)
async def clear_all_messages(ctx):
    channel_id = ctx.channel.id
    clear_messages(channel_id)
    await ctx.send("All messages have been cleared from the channel database.")

# Command: Clear user's messages from the channel database
@bot.command(name='clearme')
async def clear_user_messages(ctx):
    user_id = ctx.author.id
    channel_id = ctx.channel.id
    clear_messages(channel_id, user_id)
    await ctx.send("Your messages have been cleared from the channel database.")

# Function to save a message to SQLite
def save_message(channel_id, user_id, nickname, content):
    cursor.execute('''
        INSERT INTO messages (channel_id, user_id, nickname, content)
        VALUES (?, ?, ?, ?)
    ''', (channel_id, user_id, nickname, content))
    conn.commit()

# Function to clear messages from SQLite
def clear_messages(channel_id, user_id=None):
    if user_id:
        cursor.execute('''
            DELETE FROM messages
            WHERE channel_id = ? AND user_id = ?
        ''', (channel_id, user_id))
    else:
        cursor.execute('''
            DELETE FROM messages
            WHERE channel_id = ?
        ''', (channel_id,))
    conn.commit()

# Function to get member nickname
def get_member_nickname(member, guild):
    return member.nick if member.nick else member.name

# Function to get user history from SQLite
def get_user_history(channel_id, user_id):
    cursor.execute('''
        SELECT content FROM messages
        WHERE channel_id = ? AND user_id = ?
    ''', (channel_id, user_id))
    return [{"role": "user", "content": row[0]} for row in cursor.fetchall()]

# Function to process the message queue
async def process_queue():
    while True:
        try:
            if not message_queue.empty():
                # Dequeue the message
                message, data = await asyncio.wait_for(message_queue.get(), timeout=400)  # Increase the timeout value if needed

                # Process the message
                await process_message(message, data)
            else:
                await asyncio.sleep(5)  # Adjust the sleep duration as needed
        except asyncio.TimeoutError:
            while not message_queue.empty():
                _ = await message_queue.get()

# Function to process a single message
async def process_message(message, data):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, headers=HEADERS, json=data) as response:
                response.raise_for_status()
                assistant_message = (await response.json())['choices'][0]['message']['content']

        assistant_nickname = CHARACTER_NAME  # Use the character name variable

        # Debugging
        user_nickname = message.author.display_name
        print("")
        print_equals_to_end()
        print(f"User: {user_nickname} ({get_member_nickname(message.author, message.guild)}): {message.content}")
        print_equals_to_end()
        print(f"Response: {assistant_nickname}: {assistant_message}")
        print_equals_to_end()
        print("")
             
        # Split the assistant's message into chunks of 2000 characters
        for chunk in [assistant_message[i:i + 2000] for i in range(0, len(assistant_message), 2000)]:
            # Respond to the Discord channel with each chunk
            await message.channel.send(chunk)

    except aiohttp.ClientError:
        await message.channel.send("Sorry, there was an error processing your request.")


def clear_console():
    # Clear the console based on the operating system
    os.system('cls' if os.name == 'nt' else 'clear')

def print_equals_to_end():
    # Get the width of the console screen
    console_width = shutil.get_terminal_size().columns

    # Print "=" characters until the end of the console screen
    print("=" * console_width)


# Replace with your bot token
print("=Attempting to connect to discord=")
bot.run(YOUR_BOT_TOKEN)
