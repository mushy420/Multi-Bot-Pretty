
import discord
from discord.ext import commands
import asyncio
import logging
import coloredlogs
import os
import datetime
from dotenv import load_dotenv
import commands as cmd_module
import config

# Set up logging
logger = logging.getLogger('bot')
coloredlogs.install(
    level=config.LOG_LEVEL,
    logger=logger,
    fmt=config.LOG_FORMAT
)

# Load environment variables
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

# Create the bot instance
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=config.PREFIX, intents=intents)

# Add start time attribute for uptime command
bot.start_time = datetime.datetime.now()

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    logger.info(f'Logged in as {bot.user.name} ({bot.user.id})')
    logger.info(f'Prefix: {config.PREFIX}')
    
    # Set status
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=config.ACTIVITY))
    
    # Add cogs
    await bot.add_cog(cmd_module.Moderation(bot))
    await bot.add_cog(cmd_module.Information(bot))
    await bot.add_cog(cmd_module.Config(bot))
    await bot.add_cog(cmd_module.ErrorHandler(bot))
    
    logger.info('Bot is ready!')

@bot.event
async def on_guild_join(guild):
    """Called when the bot joins a new guild"""
    logger.info(f'Joined new guild: {guild.name} (ID: {guild.id})')
    
    # Try to find a suitable channel to send a welcome message
    target_channel = None
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            target_channel = channel
            break
    
    if target_channel:
        embed = discord.Embed(
            title="Thanks for adding me!",
            description=f"Hi, I'm a moderation and security bot. Use `{config.PREFIX}help` to see my commands.",
            color=config.COLORS["main"]
        )
        embed.add_field(name="Prefix", value=f"`{config.PREFIX}`")
        embed.add_field(name="Support", value="Contact the bot developer for support.")
        embed.set_footer(text="Made with ❤️")
        
        try:
            await target_channel.send(embed=embed)
        except:
            pass

@bot.event
async def on_guild_remove(guild):
    """Called when the bot leaves a guild"""
    logger.info(f'Left guild: {guild.name} (ID: {guild.id})')

async def main():
    """Main entry point for the bot"""
    try:
        if not TOKEN:
            logger.error("No bot token found in .env file. Please add your token.")
            return
        
        await bot.start(TOKEN)
    except discord.errors.LoginFailure:
        logger.error("Invalid bot token. Please check your .env file.")
    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=e)

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
