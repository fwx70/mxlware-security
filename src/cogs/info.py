import discord
from discord.ext import commands
import logging

logger = logging.getLogger("discord_bot")

class InfoCog(commands.Cog):
    """Information and utility commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="botinfo", help="Get bot information")
    async def botinfo(self, ctx):
        """Get bot information"""
        embed = discord.Embed(
            title="🤖 Bot Information",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.add_field(name="Bot Name", value=self.bot.user.name, inline=False)
        embed.add_field(name="Bot ID", value=self.bot.user.id, inline=False)
        embed.add_field(name="Prefix", value="`!`", inline=False)
        embed.add_field(name="Version", value="2.0 - Enhanced", inline=False)
        embed.add_field(name="Features", value="Anti-nuke Protection\nAnti-Self-Bot Detection\nModeration Tools\nUtility Commands", inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="membercount", help="Get member count")
    async def membercount(self, ctx):
        """Get member count"""
        total = len(ctx.guild.members)
        humans = len([m for m in ctx.guild.members if not m.bot])
        bots = len([m for m in ctx.guild.members if m.bot])
        
        embed = discord.Embed(
            title="👥 Member Count",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Total Members", value=total, inline=False)
        embed.add_field(name="Humans", value=humans, inline=False)
        embed.add_field(name="Bots", value=bots, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="invite", help="Get bot invite link")
    async def invite(self, ctx):
        """Get bot invite link"""
        permissions = discord.Permissions(
            administrator=True,
            manage_guild=True,
            manage_roles=True,
            manage_channels=True,
            kick_members=True,
            ban_members=True,
            manage_messages=True,
            embed_links=True,
            read_messages=True,
            send_messages=True
        )
        
        url = discord.utils.oauth_url(self.bot.user.id, permissions=permissions)
        
        embed = discord.Embed(
            title="🔗 Bot Invite Link",
            description=f"[Click here to invite the bot]({url})",
            color=discord.Color.blurple()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="uptime", help="Get bot uptime")
    async def uptime(self, ctx):
        """Get bot uptime"""
        from datetime import datetime
        uptime_seconds = (datetime.utcnow() - self.bot.user.created_at).total_seconds()
        
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        embed = discord.Embed(
            title="⏱️ Bot Uptime",
            description=f"{days}d {hours}h {minutes}m",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(InfoCog(bot))
