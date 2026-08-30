import discord
from discord.ext import commands
import logging

logger = logging.getLogger("discord_bot")

class AdminCog(commands.Cog):
    """Admin and owner-only commands"""
    
    def __init__(self, bot):
        self.bot = bot

    async def get_or_create_log_channel(self, guild):
        """Ensure the guild has a dedicated bot log channel available."""
        channel_id = await self.bot.db.get_guild_log_channel(guild.id)
        if channel_id:
            channel = guild.get_channel(channel_id)
            if channel is not None and isinstance(channel, discord.TextChannel):
                return channel

        channel = discord.utils.get(guild.text_channels, name="bot-logs")
        if channel is not None:
            await self.bot.db.set_guild_log_channel(guild.id, channel.id)
            return channel

        channel = await guild.create_text_channel(
            "bot-logs",
            reason="Create the bot's moderation and anti-nuke log channel"
        )
        await self.bot.db.set_guild_log_channel(guild.id, channel.id)
        return channel

    @commands.command(name="setup", help="Create the bot log channel and enable tracking")
    @commands.has_permissions(administrator=True)
    async def setup_command(self, ctx):
        """Create or reuse the guild log channel for moderator and anti-nuke events."""
        log_channel = await self.get_or_create_log_channel(ctx.guild)

        embed = discord.Embed(
            title="✅ Bot Setup Complete",
            description="This channel will receive ban and anti-nuke alerts.",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Log Channel", value=log_channel.mention, inline=False)

        await log_channel.send(embed=embed)
        await ctx.send(f"✅ Setup complete. Logs will be sent to {log_channel.mention}")
    
    @commands.command(name="status", help="Set bot status")
    @commands.is_owner()
    async def status(self, ctx, *, text):
        """Set bot status"""
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=text
            )
        )
        await ctx.send(f"✅ Status updated to: {text}")
    
    @commands.command(name="reload", help="Reload a cog")
    @commands.is_owner()
    async def reload(self, ctx, cog_name: str):
        """Reload a cog"""
        try:
            await self.bot.reload_extension(f"src.cogs.{cog_name}")
            await ctx.send(f"✅ Reloaded cog: {cog_name}")
        except Exception as e:
            await ctx.send(f"❌ Error reloading cog: {e}")
    
    @commands.command(name="load", help="Load a cog")
    @commands.is_owner()
    async def load(self, ctx, cog_name: str):
        """Load a cog"""
        try:
            await self.bot.load_extension(f"src.cogs.{cog_name}")
            await ctx.send(f"✅ Loaded cog: {cog_name}")
        except Exception as e:
            await ctx.send(f"❌ Error loading cog: {e}")
    
    @commands.command(name="unload", help="Unload a cog")
    @commands.is_owner()
    async def unload(self, ctx, cog_name: str):
        """Unload a cog"""
        try:
            await self.bot.unload_extension(f"src.cogs.{cog_name}")
            await ctx.send(f"✅ Unloaded cog: {cog_name}")
        except Exception as e:
            await ctx.send(f"❌ Error unloading cog: {e}")
    
    @commands.command(name="stats", help="Show bot statistics")
    @commands.is_owner()
    async def stats(self, ctx):
        """Show bot statistics"""
        embed = discord.Embed(
            title="📊 Bot Statistics",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Guilds", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(list(self.bot.get_all_members())), inline=True)
        embed.add_field(name="Cogs Loaded", value=len(self.bot.cogs), inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="antinuke", help="Configure anti-nuke protection")
    @commands.has_permissions(administrator=True)
    async def antinuke(self, ctx, action: str = None):
        """Configure anti-nuke protection"""
        if not action:
            status = "✅ Enabled" if self.bot.antinuke else "❌ Disabled"
            await ctx.send(f"Anti-nuke protection is currently: {status}")
            return
        
        if action.lower() == "enable":
            if not self.bot.antinuke:
                import config
                from src.protection.antinuke import AntiNukeProtection
                self.bot.antinuke = AntiNukeProtection(self.bot, self.bot.db)
                await ctx.send("✅ Anti-nuke protection enabled")
            else:
                await ctx.send("⚠️ Anti-nuke protection is already enabled")
        
        elif action.lower() == "disable":
            if self.bot.antinuke:
                self.bot.antinuke = None
                await ctx.send("✅ Anti-nuke protection disabled")
            else:
                await ctx.send("⚠️ Anti-nuke protection is already disabled")
    
    @commands.command(name="antiself", help="Configure anti-self-bot protection")
    @commands.has_permissions(administrator=True)
    async def antiself(self, ctx, action: str = None):
        """Configure anti-self-bot protection"""
        if not action:
            status = "✅ Enabled" if self.bot.antiself else "❌ Disabled"
            await ctx.send(f"Anti-self-bot protection is currently: {status}")
            return
        
        if action.lower() == "enable":
            if not self.bot.antiself:
                import config
                from src.protection.antiself import AntiSelfBotProtection
                self.bot.antiself = AntiSelfBotProtection(self.bot, self.bot.db)
                await ctx.send("✅ Anti-self-bot protection enabled")
            else:
                await ctx.send("⚠️ Anti-self-bot protection is already enabled")
        
        elif action.lower() == "disable":
            if self.bot.antiself:
                self.bot.antiself = None
                await ctx.send("✅ Anti-self-bot protection disabled")
            else:
                await ctx.send("⚠️ Anti-self-bot protection is already disabled")

async def setup(bot):
    await bot.add_cog(AdminCog(bot))
