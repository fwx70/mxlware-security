import discord
from discord.ext import tasks
from collections import defaultdict
from datetime import datetime, timedelta
import logging
import re

logger = logging.getLogger("discord_bot")

class AntiSelfBotProtection:
    """Detect and prevent self-bot activity"""
    
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        
        # Track patterns per user
        self.user_patterns = defaultdict(lambda: {"messages": [], "api_calls": []})
        self.suspicious_patterns = [
            r"(?i)(self\.?bot|token|webhook|api_key)",  # Self-bot references
            r"(?i)(client\.run|token =)",  # Token usage
            r"(?i)(webhook\..*send|execute|script)",  # Webhook automation
            r"(?i)(mass\s*(message|delete|ban|kick))",  # Mass actions
        ]
        
        # Setup event listeners
        self.bot.add_listener(self.on_message_for_selfbot_check, "on_message")
        
        # Start monitoring task
        self.monitor_patterns.start()
    
    async def on_message_for_selfbot_check(self, message):
        """Check messages for self-bot patterns"""
        # Don't check bot's own messages
        if message.author.bot:
            return
        
        # Don't check messages in DMs
        if not message.guild:
            return
        
        import config
        if not config.DETECT_BOT_ACTIVITY_PATTERNS:
            return
        
        try:
            # Check for suspicious patterns
            content_lower = message.content.lower()
            
            for pattern in self.suspicious_patterns:
                if re.search(pattern, message.content):
                    await self.db.log_antiself_action(
                        message.guild.id,
                        message.author.id,
                        "suspicious_pattern",
                        f"Pattern matched: {pattern}"
                    )
                    
                    logger.warning(f"Suspicious pattern detected from {message.author} in {message.guild}")
                    
                    if config.BLOCK_SUSPICIOUS_PATTERNS:
                        try:
                            await message.delete()
                            await message.author.send(
                                embed=discord.Embed(
                                    title="⚠️ Message Blocked",
                                    description="Your message contained suspicious content and was removed by anti-self-bot protection.",
                                    color=discord.Color.orange()
                                )
                            )
                        except:
                            pass
                    break
            
            # Track message for pattern analysis
            self.user_patterns[message.author.id]["messages"].append({
                "timestamp": datetime.utcnow(),
                "content": message.content[:100],  # Store first 100 chars only
                "guild_id": message.guild.id
            })
        
        except Exception as e:
            logger.error(f"Error in self-bot check: {e}")
    
    async def detect_mass_actions(self, user_id, guild_id, action_type):
        """Detect mass actions by user"""
        patterns = self.user_patterns[user_id]["api_calls"]
        cutoff = datetime.utcnow() - timedelta(seconds=30)
        
        recent = [p for p in patterns if p["timestamp"] > cutoff]
        
        if len(recent) > 10:  # More than 10 actions in 30 seconds
            await self.db.log_antiself_action(
                guild_id,
                user_id,
                "mass_actions",
                f"Detected {len(recent)} {action_type}s in 30 seconds"
            )
            
            logger.warning(f"Mass {action_type} attempt detected from {user_id} in guild {guild_id}")
            return True
        
        return False
    
    async def check_user_reputation(self, user):
        """Analyze user behavior for self-bot indicators"""
        import config
        
        indicators = []
        
        # Check account age
        account_age = datetime.utcnow() - user.created_at
        if account_age < timedelta(days=7):
            indicators.append("New account")
        
        # Check for bot indicators in profile
        if "bot" in user.name.lower() or "self" in user.name.lower():
            indicators.append("Suspicious username")
        
        return indicators
    
    @tasks.loop(minutes=5)
    async def monitor_patterns(self):
        """Monitor and analyze user patterns"""
        cutoff = datetime.utcnow() - timedelta(hours=1)
        
        # Clean up old data
        for user_id in list(self.user_patterns.keys()):
            messages = self.user_patterns[user_id]["messages"]
            self.user_patterns[user_id]["messages"] = [
                m for m in messages if m["timestamp"] > cutoff
            ]
