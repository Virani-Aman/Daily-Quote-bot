import discord
import requests
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
from pytz import timezone

# Load bot token and IDs from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Fetch bot token
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # Fetch channel ID as an integer
MENTION_ROLE_ID = int(os.getenv("MENTION_ROLE_ID"))  # Fetch mention role ID as an integer

# Set up bot intents
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()
IST = timezone("Asia/Kolkata")  # Define IST timezone
tree = bot.tree  # Create bot command tree for slash commands

# Function to fetch a random quote
def get_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random")
        if response.status_code == 200:
            data = response.json()
            return f'\"{data[0]["q"]}\" - {data[0]["a"]}'
        return "Could not fetch a quote at this time."
    except Exception as e:
        return f"Error fetching quote: {e}"

# Function to send the daily quote
async def send_daily_quote():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        quote = get_quote()
        mention = f"<@&{MENTION_ROLE_ID}>"  # Use @& for roles
        await channel.send(f"{quote}\n{mention}")

# Slash command to generate a quote manually
@tree.command(name="quote", description="Get a random quote")
async def quote(interaction: discord.Interaction):
    quote = get_quote()
    await interaction.response.send_message(quote)

# Bot event when it starts
@bot.event
async def on_ready():
    await bot.wait_until_ready()
    try:
        await tree.sync()  # Sync commands with Discord
        print("Slash commands synced successfully!")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print(f'Logged in as {bot.user}')
    scheduler.add_job(
        lambda: bot.loop.create_task(send_daily_quote()),
        "cron",
        hour=8, minute=59,
        timezone=IST  # Set timezone to IST
    )    
    scheduler.start()

# Run the bot
bot.run(BOT_TOKEN)
