import discord
from discord.ext import commands
import logging

logger = logging.getLogger("discord_bot")

class ModerationAdvancedCog(commands.Cog):
    """Advanced moderation commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="unban", help="Unban a user")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User, *, reason="No reason provided"):
        """Unban a user"""
        try:
            await ctx.guild.unban(user, reason=reason)
            
            embed = discord.Embed(
                title="✅ User Unbanned",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Unbanned by", value=ctx.author.mention, inline=False)
            
            await ctx.send(embed=embed)

            log_channel_id = await self.bot.db.get_guild_log_channel(ctx.guild.id)
            if log_channel_id:
                log_channel = ctx.guild.get_channel(log_channel_id)
                if log_channel is not None:
                    await log_channel.send(embed=embed)
        except discord.NotFound:
            await ctx.send("❌ User is not banned")
    
    @commands.command(name="slowmode", help="Set channel slowmode")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        """Set channel slowmode"""
        if seconds < 0 or seconds > 21600:
            await ctx.send("❌ Slowmode must be between 0 and 21600 seconds")
            return
        
        await ctx.channel.edit(slowmode_delay=seconds)
        
        if seconds == 0:
            await ctx.send(f"✅ Slowmode disabled")
        else:
            await ctx.send(f"✅ Slowmode set to {seconds} seconds")
    
    @commands.command(name="lock", help="Lock a channel")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        """Lock a channel"""
        channel = channel or ctx.channel
        
        await channel.set_permissions(
            ctx.guild.default_role,
            send_messages=False
        )
        
        await ctx.send(f"✅ Channel {channel.mention} has been locked")
    
    @commands.command(name="unlock", help="Unlock a channel")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        """Unlock a channel"""
        channel = channel or ctx.channel
        
        await channel.set_permissions(
            ctx.guild.default_role,
            send_messages=None
        )
        
        await ctx.send(f"✅ Channel {channel.mention} has been unlocked")
    
    @commands.command(name="massrole", help="Give a role to multiple members")
    @commands.has_permissions(manage_roles=True)
    async def massrole(self, ctx, role: discord.Role, *, mention: str = "@everyone"):
        """Give a role to multiple members"""
        count = 0
        
        for member in ctx.guild.members:
            if role not in member.roles:
                try:
                    await member.add_roles(role)
                    count += 1
                except:
                    pass
        
        await ctx.send(f"✅ Added {role.mention} to {count} members")
    
    @commands.command(name="addrole", help="Add a role to a member")
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, role: discord.Role):
        """Add a role to a member"""
        if role >= ctx.author.top_role:
            await ctx.send("❌ You cannot add a role higher than your own")
            return
        
        await member.add_roles(role)
        await ctx.send(f"✅ Added {role.mention} to {member.mention}")
    
    @commands.command(name="removerole", help="Remove a role from a member")
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, member: discord.Member, role: discord.Role):
        """Remove a role from a member"""
        if role >= ctx.author.top_role:
            await ctx.send("❌ You cannot remove a role higher than your own")
            return
        
        await member.remove_roles(role)
        await ctx.send(f"✅ Removed {role.mention} from {member.mention}")

async def setup(bot):
    await bot.add_cog(ModerationAdvancedCog(bot))
