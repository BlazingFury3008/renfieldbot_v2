import os
import logging
import asyncio
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands, Interaction

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
LOG_HOME = os.getenv("LOG_HOME")
DISCORD_LOG = os.path.join(LOG_HOME, "discord.log") if LOG_HOME else "discord.log"

# Set up logging
logging.basicConfig(
    filename=DISCORD_LOG,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Set up bot intents
intents = discord.Intents.default()
intents.members = True  # Can Read Members
intents.message_content = True  # Can Read Messages
intents.dm_messages = True  # Can Send/Receive DMs Messages

# Bot description and instance
description = "GVLarp Discord Bot, Renfield 2.0"
bot = commands.Bot(command_prefix=".", description=description, intents=intents)

@bot.event
async def on_ready():
    try:
        # Sync global commands
        await bot.tree.sync()
        logger.info(f"Synced {len(bot.tree.get_commands())} global commands")

        # If you want to sync for a specific guild (fast updates)
        GUILD_ID = os.getenv("DISCORD_GUILD_ID")
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            await bot.tree.sync(guild=guild)
            logger.info(f"Synced commands for guild: {GUILD_ID}")

        print(f"Logged in as {bot.user} - Ready!")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}", exc_info=True)
        
    
# Does not work? Unsure why
@bot.tree.command(name="sync", description="Sync Commands")
async def sync(interaction: Interaction):
    await interaction.response.defer(thinking=True)
    try:
        await bot.tree.sync()
        await interaction.followup.send("Commands successfully synchronized!")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}", exc_info=True)
        await interaction.followup.send(f"Failed to sync commands. Check logs for details.")
    

async def main():
    try:
        logger.info("Loading bot...")

        async with bot:
            # Load cogs before running the bot
            await bot.load_extension("cogs.voting")
            logger.info("Loaded cog: cogs.voting")
            await bot.load_extension("cogs.diceroller")
            logger.info("Loaded cog: cogs.diceroller")
            await bot.load_extension("cogs.ghoul")
            logger.info("Loaded cog: cogs.ghoul")
            await bot.load_extension("cogs.events")
            logger.info("Loaded cog: cogs.events")

            # Start bot
            await bot.start(TOKEN)

    except Exception as e:
        logger.error(f"Bot encountered an error: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
