import discord
from discord.ext import commands, tasks
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from src.utils.logger import setup_logging, get_protection_logger
from src.utils.database import Database
from src.protection.antinuke import AntiNukeProtection
from src.protection.antiself import AntiSelfBotProtection

# Setup logging
logger = setup_logging()
antinuke_logger = get_protection_logger("AntiNuke")
antiself_logger = get_protection_logger("AntiSelfBot")

class EnhancedDiscordBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.moderation = True
        
        super().__init__(
            command_prefix=config.COMMAND_PREFIX,
            intents=intents,
            *args,
            **kwargs
        )
        
        self.db = None
        self.antinuke = None
        self.antiself = None
        
    async def setup_hook(self):
        """Initialize bot systems"""
        logger.info("="*60)
        logger.info("Setting up bot systems...")
        logger.info("="*60)
        
        # Initialize database
        logger.info("Initializing database...")
        self.db = Database(config.DATABASE_PATH)
        await self.db.init_db()
        logger.info("Database initialized successfully")
        
        # Initialize protection systems
        logger.info("Initializing protection systems...")
        if config.ANTINUKE_ENABLED:
            self.antinuke = AntiNukeProtection(self, self.db)
            antinuke_logger.info("Anti-Nuke Protection System initialized")
            antinuke_logger.info(f"  - Max Role Deletions/min: {config.MAX_ROLE_DELETIONS_PER_MINUTE}")
            antinuke_logger.info(f"  - Max Channel Deletions/min: {config.MAX_CHANNEL_DELETIONS_PER_MINUTE}")
            antinuke_logger.info(f"  - Max Bans/min: {config.MAX_BANS_PER_MINUTE}")
            antinuke_logger.info(f"  - Max Kicks/min: {config.MAX_KICKS_PER_MINUTE}")
            logger.info("Anti-nuke protection enabled")
        else:
            logger.warning("Anti-nuke protection DISABLED in config")
        
        if config.ANTISELF_ENABLED:
            self.antiself = AntiSelfBotProtection(self, self.db)
            antiself_logger.info("Anti-Self-Bot Protection System initialized")
            antiself_logger.info(f"  - Pattern Detection: {config.DETECT_BOT_ACTIVITY_PATTERNS}")
            antiself_logger.info(f"  - Block Suspicious Patterns: {config.BLOCK_SUSPICIOUS_PATTERNS}")
            logger.info("Anti-self-bot protection enabled")
        else:
            logger.warning("Anti-self-bot protection DISABLED in config")
        
        logger.info("="*60)
        
        # Load cogs
        await self.load_cogs()
        
    async def load_cogs(self):
        """Load all command cogs"""
        logger.info("Loading command cogs...")
        cogs_path = Path(__file__).parent / "cogs"
        loaded_count = 0
        failed_count = 0
        
        for cog_file in cogs_path.glob("*.py"):
            if cog_file.name.startswith("_"):
                continue
            cog_name = f"src.cogs.{cog_file.stem}"
            try:
                await self.load_extension(cog_name)
                logger.info(f"Loaded cog: {cog_name}")
                loaded_count += 1
            except Exception as e:
                logger.error(f"Failed to load cog {cog_name}: {e}")
                failed_count += 1
        
        logger.info(f"Cog loading complete: {loaded_count} loaded, {failed_count} failed")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info("="*60)
        logger.info(f"Bot logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guild(s)")
        logger.info("="*60)
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{config.COMMAND_PREFIX}help | Anti-nuke Active"
            )
        )
        
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"You lack the required permissions: {error.missing_permissions}")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"I lack the required permissions: {error.missing_permissions}")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing required argument: {error.param}")
        else:
            logger.error(f"Command error: {error}")
            await ctx.send(f"An error occurred: {str(error)[:100]}")

async def main():
    """Run the bot"""
    if not config.DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not set in .env file")
        sys.exit(1)
    
    bot = EnhancedDiscordBot()
    
    async with bot:
        await bot.start(config.DISCORD_TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
