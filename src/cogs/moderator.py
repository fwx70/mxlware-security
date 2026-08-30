import discord
from discord.ext import commands
import logging

logger = logging.getLogger("discord_bot")

class ModeratorCog(commands.Cog):
    """Moderation commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="warn", help="Warn a user")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Warn a user"""
        if member == ctx.author:
            await ctx.send("❌ You cannot warn yourself")
            return
        
        if member.top_role >= ctx.author.top_role:
            await ctx.send("❌ You cannot warn someone with equal or higher role")
            return
        
        await self.bot.db.add_warning(ctx.guild.id, member.id, reason, ctx.author.id)
        warns = await self.bot.db.get_user_warnings(ctx.guild.id, member.id)
        
        embed = discord.Embed(
            title="⚠️ User Warned",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Total Warnings", value=str(warns), inline=False)
        embed.add_field(name="Warned by", value=ctx.author.mention, inline=False)
        
        await ctx.send(embed=embed)
        
        try:
            await member.send(embed=discord.Embed(
                title="⚠️ You have been warned",
                description=f"You were warned in {ctx.guild.name}",
                color=discord.Color.orange()
            ).add_field(name="Reason", value=reason))
        except:
            pass
    
    @commands.command(name="kick", help="Kick a member")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Kick a member"""
        if member == ctx.author:
            await ctx.send("❌ You cannot kick yourself")
            return
        
        if member.top_role >= ctx.author.top_role:
            await ctx.send("❌ You cannot kick someone with equal or higher role")
            return
        
        await member.kick(reason=reason)
        
        embed = discord.Embed(
            title="👢 Member Kicked",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Kicked by", value=ctx.author.mention, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="ban", help="Ban a member")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Ban a member"""
        if member == ctx.author:
            await ctx.send("❌ You cannot ban yourself")
            return
        
        if member.top_role >= ctx.author.top_role:
            await ctx.send("❌ You cannot ban someone with equal or higher role")
            return
        
        await member.ban(reason=reason)
        
        embed = discord.Embed(
            title="🔨 Member Banned",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Banned by", value=ctx.author.mention, inline=False)
        
        await ctx.send(embed=embed)

        log_channel_id = await self.bot.db.get_guild_log_channel(ctx.guild.id)
        if log_channel_id:
            log_channel = ctx.guild.get_channel(log_channel_id)
            if log_channel is not None:
                await log_channel.send(embed=embed)
    
    @commands.command(name="mute", help="Mute a member")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Mute a member"""
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted", color=discord.Color.greyple())
            
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False, speak=False)
        
        await member.add_roles(muted_role, reason=reason)
        
        embed = discord.Embed(
            title="🔇 Member Muted",
            color=discord.Color.greyple(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Muted by", value=ctx.author.mention, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="unmute", help="Unmute a member")
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        """Unmute a member"""
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        
        if not muted_role or muted_role not in member.roles:
            await ctx.send("❌ Member is not muted")
            return
        
        await member.remove_roles(muted_role)
        await ctx.send(f"✅ {member.mention} has been unmuted")
    
    @commands.command(name="purge", help="Delete multiple messages")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int = 10):
        """Delete multiple messages"""
        if amount < 1 or amount > 100:
            await ctx.send("❌ Amount must be between 1 and 100")
            return
        
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"✅ Deleted {len(deleted) - 1} messages", delete_after=5)

async def setup(bot):
    await bot.add_cog(ModeratorCog(bot))
