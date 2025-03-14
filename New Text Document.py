import discord
import requests
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Replace with your bot token and channel ID
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Replace with your actual bot token
CHANNEL_ID = YOUR_CHANNEL_ID  # Replace with the actual channel ID
MENTION_USER_ID = 1347770766674104392  # Replace with the actual user ID to tag

# Set up bot intents
intents = discord.Intents.default()
intents.messages = True  # Enable message-related events

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=intents)
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

# Bot event when it starts
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    scheduler.add_job(lambda: bot.loop.create_task(send_daily_quote()), "cron", hour=9, minute=0)  # Sends the quote at 9 AM daily
    scheduler.start()

# Run the bot
bot.run(BOT_TOKEN)
