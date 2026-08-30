import discord
from discord.ext import commands
import logging

logger = logging.getLogger("discord_bot")

class UtilityCog(commands.Cog):
    """Utility commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="ping", help="Check bot latency")
    async def ping(self, ctx):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latency: {latency}ms",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="userinfo", help="Get user information")
    async def userinfo(self, ctx, member: discord.Member = None):
        """Get user information"""
        member = member or ctx.author
        
        embed = discord.Embed(
            title=f"User Info: {member}",
            color=member.color,
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="ID", value=member.id, inline=False)
        embed.add_field(name="Created", value=discord.utils.format_dt(member.created_at), inline=False)
        embed.add_field(name="Joined", value=discord.utils.format_dt(member.joined_at), inline=False)
        embed.add_field(name="Top Role", value=member.top_role.mention, inline=False)
        embed.add_field(name="Status", value=str(member.status).title(), inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="serverinfo", help="Get server information")
    async def serverinfo(self, ctx):
        """Get server information"""
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"Server Info: {guild.name}",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="ID", value=guild.id, inline=False)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=False)
        embed.add_field(name="Members", value=f"{guild.member_count}", inline=False)
        embed.add_field(name="Channels", value=f"{len(guild.channels)}", inline=False)
        embed.add_field(name="Roles", value=f"{len(guild.roles)}", inline=False)
        embed.add_field(name="Created", value=discord.utils.format_dt(guild.created_at), inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="avatar", help="Get user avatar")
    async def avatar(self, ctx, member: discord.Member = None):
        """Get user avatar"""
        member = member or ctx.author
        
        embed = discord.Embed(
            title=f"Avatar: {member}",
            color=member.color,
            timestamp=discord.utils.utcnow()
        )
        embed.set_image(url=member.avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="role", help="Get role information")
    async def role(self, ctx, role: discord.Role):
        """Get role information"""
        embed = discord.Embed(
            title=f"Role Info: {role.name}",
            color=role.color,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="ID", value=role.id, inline=False)
        embed.add_field(name="Color", value=str(role.color), inline=False)
        embed.add_field(name="Members", value=len(role.members), inline=False)
        embed.add_field(name="Created", value=discord.utils.format_dt(role.created_at), inline=False)
        embed.add_field(name="Mentionable", value=role.mentionable, inline=False)
        
        await ctx.send(embed=embed)
    
async def setup(bot):
    await bot.add_cog(UtilityCog(bot))
