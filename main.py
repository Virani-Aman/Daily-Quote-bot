import discord
import requests
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
MENTION_USER_ID = int(os.getenv("MENTION_USER_ID"))

# Set up bot intents
intents = discord.Intents.default()
intents.messages = True  # Enable message-related events

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Use discord.app_commands to create slash commands
tree = bot.tree
scheduler = AsyncIOScheduler()

# Function to fetch a random quote from the API
def get_quote():
    try:
        response = requests.get("https://api.quotable.io/random")
        if response.status_code == 200:
            data = response.json()
            return f'\"{data["content"]}\" - {data["author"]}'
        return "Could not fetch a quote at this time."
    except Exception as e:
        return f"Error fetching quote: {e}"

# Function to send the daily quote
async def send_daily_quote():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        quote = get_quote()
        mention = f"<@{MENTION_USER_ID}>"  # Mention the user
        await channel.send(f"{quote}\n{mention}")

# Slash command to generate a quote manually
@tree.command(name="quote", description="Get a random inspirational quote")
async def quote_command(interaction: discord.Interaction):
    quote = get_quote()
    mention = f"<@{interaction.user.id}>"  # Mention the user who used the command
    await interaction.response.send_message(f"{quote}\n{mention}")

# Bot event when it starts
@bot.event
async def on_ready():
    await bot.wait_until_ready()  # Wait until bot is ready before registering commands
    await tree.sync()  # Sync slash commands with Discord
    print(f'Logged in as {bot.user}')
    
    # Schedule daily quote at 9 AM
    scheduler.add_job(lambda: bot.loop.create_task(send_daily_quote()), "cron", hour=9, minute=0)
    scheduler.start()

# Run the bot
bot.run(BOT_TOKEN)
