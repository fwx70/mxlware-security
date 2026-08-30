import discord
from discord.ext import tasks
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("discord_bot")

class AntiNukeProtection:
    """Advanced anti-nuke protection system"""
    
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        
        # Track actions per minute
        self.action_tracker = defaultdict(lambda: {"roles": [], "channels": [], "bans": [], "kicks": []})
        
        # Setup event listeners
        self.bot.add_listener(self.on_guild_role_delete, "on_guild_role_delete")
        self.bot.add_listener(self.on_guild_channel_delete, "on_guild_channel_delete")
        self.bot.add_listener(self.on_member_remove, "on_member_remove")
        
        # Start cleanup task
        self.cleanup_old_actions.start()
    
    def add_action(self, guild_id, action_type, user_id, target_id):
        """Track an action"""
        timestamp = datetime.utcnow()
        self.action_tracker[guild_id][action_type].append({
            "user_id": user_id,
            "target_id": target_id,
            "timestamp": timestamp
        })
    
    def get_recent_actions(self, guild_id, action_type, minutes=1):
        """Get actions from last N minutes"""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        actions = [
            a for a in self.action_tracker[guild_id][action_type]
            if a["timestamp"] > cutoff
        ]
        return actions
    
    async def on_guild_role_delete(self, role):
        """Monitor role deletions"""
        try:
            guild = role.guild
            async for entry in guild.audit_logs(action=discord.AuditLogAction.role_delete, limit=1):
                user = entry.user
                target = entry.target
                
                self.add_action(guild.id, "roles", user.id, target.id)
                
                recent_deletions = self.get_recent_actions(guild.id, "roles", minutes=1)
                
                await self.db.log_antinuke_action(
                    guild.id, "role_delete", user.id, target.id,
                    f"Total deletions in 1min: {len(recent_deletions)}"
                )
                
                # Check if this exceeds threshold
                import config
                if len(recent_deletions) >= config.MAX_ROLE_DELETIONS_PER_MINUTE:
                    await self.handle_nuke_attempt(guild, user, "Role Deletion Spam", f"{len(recent_deletions)} roles deleted in 1 minute")
        
        except Exception as e:
            logger.error(f"Error in role deletion handler: {e}")
    
    async def on_guild_channel_delete(self, channel):
        """Monitor channel deletions"""
        try:
            guild = channel.guild
            async for entry in guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1):
                user = entry.user
                target = entry.target
                
                self.add_action(guild.id, "channels", user.id, target.id)
                
                recent_deletions = self.get_recent_actions(guild.id, "channels", minutes=1)
                
                await self.db.log_antinuke_action(
                    guild.id, "channel_delete", user.id, target.id,
                    f"Total deletions in 1min: {len(recent_deletions)}"
                )
                
                import config
                if len(recent_deletions) >= config.MAX_CHANNEL_DELETIONS_PER_MINUTE:
                    await self.handle_nuke_attempt(guild, user, "Channel Deletion Spam", f"{len(recent_deletions)} channels deleted in 1 minute")
        
        except Exception as e:
            logger.error(f"Error in channel deletion handler: {e}")
    
    async def on_member_remove(self, member):
        """Monitor member removals (kicks/bans)"""
        try:
            guild = member.guild
            
            # Check audit log
            async for entry in guild.audit_logs(limit=5):
                if entry.target.id != member.id:
                    continue
                
                if entry.action == discord.AuditLogAction.kick:
                    user = entry.user
                    self.add_action(guild.id, "kicks", user.id, member.id)
                    recent_kicks = self.get_recent_actions(guild.id, "kicks", minutes=1)
                    
                    await self.db.log_antinuke_action(
                        guild.id, "kick", user.id, member.id,
                        f"Total kicks in 1min: {len(recent_kicks)}"
                    )
                    
                    import config
                    if len(recent_kicks) >= config.MAX_KICKS_PER_MINUTE:
                        await self.handle_nuke_attempt(guild, user, "Kick Spam", f"{len(recent_kicks)} members kicked in 1 minute")
                
                elif entry.action == discord.AuditLogAction.ban:
                    user = entry.user
                    self.add_action(guild.id, "bans", user.id, member.id)
                    recent_bans = self.get_recent_actions(guild.id, "bans", minutes=1)
                    
                    await self.db.log_antinuke_action(
                        guild.id, "ban", user.id, member.id,
                        f"Total bans in 1min: {len(recent_bans)}"
                    )
                    
                    import config
                    if len(recent_bans) >= config.MAX_BANS_PER_MINUTE:
                        await self.handle_nuke_attempt(guild, user, "Ban Spam", f"{len(recent_bans)} members banned in 1 minute")
                
                break
        
        except Exception as e:
            logger.error(f"Error in member removal handler: {e}")
    
    async def handle_nuke_attempt(self, guild, user, reason, details):
        """Handle detected nuke attempt"""
        logger.warning(f"🚨 NUKE ATTEMPT DETECTED in {guild.name}: {user} - {reason}")
        
        embed = discord.Embed(
            title="🚨 NUKE ATTEMPT DETECTED",
            description=f"A nuke attempt was detected and action has been taken",
            color=discord.Color.red()
        )
        embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Details", value=details, inline=False)
        embed.add_field(name="Guild", value=f"{guild.name} ({guild.id})", inline=False)
        embed.timestamp = discord.utils.utcnow()
        
        # Try to remove user's permissions
        try:
            await user.send(embed=discord.Embed(
                title="⚠️ Suspicious Activity Detected",
                description=f"Your account has been flagged for suspicious activity in {guild.name}. A moderator will review this shortly.",
                color=discord.Color.orange()
            ))
        except:
            pass

        try:
            log_channel_id = await self.db.get_guild_log_channel(guild.id)
            if log_channel_id:
                log_channel = guild.get_channel(log_channel_id)
                if log_channel is not None and isinstance(log_channel, discord.TextChannel):
                    await log_channel.send(embed=embed)
                    return

            for channel in guild.text_channels:
                if "bot-logs" in channel.name or "modlog" in channel.name or "admin-log" in channel.name:
                    await channel.send(embed=embed)
                    break
        except:
            pass
    
    @tasks.loop(minutes=1)
    async def cleanup_old_actions(self):
        """Clean up old action tracking data"""
        cutoff = datetime.utcnow() - timedelta(minutes=2)
        
        for guild_id in list(self.action_tracker.keys()):
            for action_type in self.action_tracker[guild_id]:
                self.action_tracker[guild_id][action_type] = [
                    a for a in self.action_tracker[guild_id][action_type]
                    if a["timestamp"] > cutoff
                ]
