import discord
import requests
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
from pytz import timezone

# Load bot token and IDs from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Fetch bot token
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # Fetch channel ID as an integer
MENTION_ROLE_ID = os.getenv("MENTION_ROLE_ID")  # Get role ID as a string

if MENTION_ROLE_ID is None:
    raise ValueError("❌ ERROR: MENTION_ROLE_ID environment variable is missing!")

MENTION_ROLE_ID = int(MENTION_ROLE_ID)  # Convert to integer

# Set up bot intents
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()
IST = timezone("Asia/Kolkata")  # Define IST timezone
tree = bot.tree  # Create bot command tree for slash commands

# Default time for daily quotes (9:00 AM IST)
default_hour = 9
default_minute = 0

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

# Slash command to get a random quote
@tree.command(name="quote", description="Get a random motivational quote")
async def quote(interaction: discord.Interaction):
    quote = get_quote()
    await interaction.response.send_message(quote)

# Slash command to manually get the daily quote
@tree.command(name="dailyquotes", description="Manually get the daily quote")
async def daily_quotes(interaction: discord.Interaction):
    quote = get_quote()
    await interaction.response.send_message(quote)

# Slash command to enable/disable daily quotes
@tree.command(name="reminder", description="Enable or disable daily quotes")
async def reminder(interaction: discord.Interaction, status: bool):
    global scheduler
    if status:
        scheduler.start()
        await interaction.response.send_message("✅ Daily quotes **enabled**!")
    else:
        scheduler.shutdown()
        await interaction.response.send_message("❌ Daily quotes **disabled**!")

# Slash command to set custom time for daily quotes
@tree.command(name="setremindertime", description="Set a custom time for daily quotes (IST)")
async def set_reminder_time(interaction: discord.Interaction, hour: int, minute: int):
    global default_hour, default_minute, scheduler

    if 0 <= hour <= 23 and 0 <= minute <= 59:
        default_hour = hour
        default_minute = minute
        scheduler.remove_all_jobs()
        scheduler.add_job(
            lambda: bot.loop.create_task(send_daily_quote()),
            "cron",
            hour=default_hour,
            minute=default_minute,
            timezone=IST
        )
        scheduler.start()
        await interaction.response.send_message(f"✅ Daily quote time set to **{hour:02d}:{minute:02d} IST**")
    else:
        await interaction.response.send_message("⚠️ Invalid time! Please enter an hour between 0-23 and minutes between 0-59.")

# Slash command for help
@tree.command(name="help", description="Show help for Daily Quotes bot")
async def help_command(interaction: discord.Interaction):
    help_text = (
        "**📌 Daily Quotes Bot Commands:**\n\n"
        "✅ **To get a random motivational quote:**\n"
        "`/quote`\n\n"
        "✅ **To send a quote to a friend:**\n"
        "`/sendquote @username`\n\n"
        "✅ **To enable or disable daily quotes:**\n"
        "`/reminder true` *(Enables daily quotes at the set time)*\n"
        "`/reminder false` *(Disables daily quotes)*\n\n"
        "✅ **To manually get the daily quote:**\n"
        "`/dailyquotes`\n\n"
        "✅ **To set a custom time for daily quotes (IST):**\n"
        "`/setremindertime <hour> <minute>`\n"
        "_Example: `/setremindertime 9 30` → Daily quote at 9:30 AM IST_\n\n"
        "✅ **To view this help message again:**\n"
        "`/help`"
    )
    await interaction.response.send_message(help_text)

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

    # Schedule the daily quote at the default time
    scheduler.add_job(
        lambda: bot.loop.create_task(send_daily_quote()),
        "cron",
        hour=default_hour,
        minute=default_minute,
        timezone=IST
    )
    scheduler.start()

# Run the bot
bot.run(BOT_TOKEN)
