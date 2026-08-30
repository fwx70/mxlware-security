# Bot Features & Capabilities

## 🛡️ Protection Systems

### Anti-Nuke Protection
Prevents server sabotage by detecting and responding to mass destructive actions.

**What it monitors:**
- Role deletions (configurable threshold)
- Channel deletions (configurable threshold)
- Member bans (configurable threshold)
- Member kicks (configurable threshold)

**How it responds:**
- Logs all suspicious activity to database
- Alerts server moderators
- Tracks offending user
- Automatically documents for audit trails

**Configuration (in config.py):**
```python
MAX_ROLE_DELETIONS_PER_MINUTE = 3
MAX_CHANNEL_DELETIONS_PER_MINUTE = 5
MAX_BANS_PER_MINUTE = 10
MAX_KICKS_PER_MINUTE = 10
```

**Real-world scenario:**
```
User attempts to delete 5 roles in 30 seconds
→ Bot detects threshold exceeded
→ Action logged to database
→ Server admins notified
→ User flagged for review
```

### Anti-Self-Bot Protection
Identifies and blocks automated self-bot activity and suspicious patterns.

**What it detects:**
- Self-bot code references
- Token usage patterns
- Webhook automation attempts
- Mass action commands
- Suspicious message content
- New account suspicious behavior

**How it responds:**
- Deletes suspicious messages
- Sends user warning via DM
- Logs violation to database
- Flags account for review
- Maintains user reputation scores

**Blocked patterns:**
- Message containing "token"
- Message containing "self.bot"
- Message containing "webhook"
- Message containing "mass delete/ban/kick"

---

## 📋 Command Categories

### 1️⃣ Moderation Commands

**Warn System**
```
!warn @user [reason]
```
- Tracks user warnings in database
- Sends warning notification to user
- Shows total warning count
- Logged for audit purposes

**Member Management**
```
!kick @user [reason]
!ban @user [reason]
!unban <user> [reason]
!mute @user [reason]
!unmute @user
```
- Full reason logging
- Audit log integration
- DM notification to affected user
- Prevents action against equal/higher role users

**Message Management**
```
!purge <amount>
```
- Bulk delete up to 100 messages
- Only deletes messages up to 2 weeks old
- Confirmation of deletion count

**Channel Management**
```
!slowmode [seconds]
!lock [channel]
!unlock [channel]
```
- Slowmode from 0-21600 seconds
- Lock/unlock channels for maintenance
- Works on specific or current channel

**Role Management**
```
!addrole @user @role
!removerole @user @role
!massrole @role
```
- Safe role assignment
- Prevents role abuse
- Add roles to single or multiple users

---

### 2️⃣ Utility Commands

**Information Retrieval**
```
!ping               # Bot latency in ms
!userinfo [@user]   # Detailed user stats
!serverinfo         # Guild statistics
!avatar [@user]     # User avatar (full size)
!role <role>        # Role details
!botinfo            # Bot information
```

**Server Statistics**
```
!membercount        # Show member breakdown
                    - Total members
                    - Human users count
                    - Bot count
```

**Utility**
```
!help [category]    # Show all commands or category-specific
!invite             # Bot invite link with permissions
!uptime             # Bot uptime since last start
```

---

### 3️⃣ Fun Commands

**Entertainment**
```
!joke              # Random joke from joke database
!8ball <question>  # Ask magic 8-ball (yes/no/maybe answers)
!dice [sides]      # Roll N-sided dice (default 6)
!flip              # Flip a coin (Heads/Tails)
!choose <opt1> <opt2> ...  # Choose randomly between options
!say <text>        # Bot repeats text (deletes command)
```

**Features:**
- Colorful embeds for responses
- Multiple outcome options
- Fun user interaction
- Timestamps on responses

---

### 4️⃣ Admin Commands (Owner/Admin Only)

**Bot Management**
```
!status <text>     # Change bot playing status
!reload <cog>      # Reload command module (no restart)
!load <cog>        # Load disabled command module
!unload <cog>      # Unload command module
!stats             # Show bot statistics
```

**Protection Management**
```
!antinuke [enable/disable]    # Toggle anti-nuke system
!antiself [enable/disable]    # Toggle anti-self-bot system
```

**Available Cogs:**
- `moderator` - Basic moderation
- `moderation_advanced` - Advanced moderation
- `utility` - Utility commands
- `fun` - Entertainment commands
- `admin` - Admin commands
- `info` - Information commands

---

### 5️⃣ Information Commands

**Bot Info**
```
!botinfo           # Bot name, ID, version, features
!membercount       # Guild member statistics
!invite            # OAuth2 invite link generator
```

---

## 🗄️ Database Features

### Automatic Tracking

**Anti-Nuke Logs Table:**
- Guild ID
- Action type (role_delete, channel_delete, kick, ban)
- User ID (who performed action)
- Target ID (what was affected)
- Timestamp
- Detailed description

**Anti-Self-Bot Logs Table:**
- Guild ID
- User ID
- Violation type
- Timestamp
- Details

**User Warnings Table:**
- Guild ID
- User ID
- Warning reason
- Warned by (moderator ID)
- Timestamp

**Guild Settings Table:**
- Guild ID
- Protection status toggles
- Log channel ID
- Admin role IDs
- Creation timestamp

### Query Examples

```python
# Get user warning count
warnings = await bot.db.get_user_warnings(guild_id, user_id)

# Log an anti-nuke action
await bot.db.log_antinuke_action(
    guild_id, 
    "role_delete", 
    user_id, 
    target_id,
    "Deleted 3 roles in 1 minute"
)

# Log anti-self-bot violation
await bot.db.log_antiself_action(
    guild_id,
    user_id,
    "suspicious_pattern",
    "Matched self-bot token pattern"
)

# Add warning
await bot.db.add_warning(
    guild_id,
    user_id,
    "Spam in general chat",
    moderator_id
)
```

---

## ⚙️ Customization

### Modifying Thresholds

Edit `config.py`:

```python
# More sensitive (faster triggers)
MAX_ROLE_DELETIONS_PER_MINUTE = 2
MAX_CHANNEL_DELETIONS_PER_MINUTE = 3
MAX_BANS_PER_MINUTE = 5
MAX_KICKS_PER_MINUTE = 5

# Less sensitive (fewer false positives)
MAX_ROLE_DELETIONS_PER_MINUTE = 5
MAX_CHANNEL_DELETIONS_PER_MINUTE = 8
MAX_BANS_PER_MINUTE = 20
MAX_KICKS_PER_MINUTE = 20
```

### Adding Custom Patterns

Edit `src/protection/antiself.py`:

```python
self.suspicious_patterns = [
    r"(?i)(self\.?bot|token|webhook|api_key)",
    r"(?i)(client\.run|token =)",
    r"YOUR_CUSTOM_PATTERN",  # Add here
]
```

### Creating Custom Cogs

1. Create `src/cogs/mycog.py`:

```python
from discord.ext import commands

class MyCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def mycommand(self, ctx):
        await ctx.send("Hello!")

async def setup(bot):
    await bot.add_cog(MyCommands(bot))
```

2. Reload: `!reload mycog`

---

## 📊 Monitoring & Logging

### Log Levels

Set in `config.py`:
```python
LOG_LEVEL = "DEBUG"      # Most verbose
LOG_LEVEL = "INFO"       # Standard
LOG_LEVEL = "WARNING"    # Only warnings/errors
LOG_LEVEL = "ERROR"      # Only errors
```

### Log Output

Logs are saved to `logs/bot.log` and console:

```
2026-08-30 10:15:23 - discord_bot - INFO - Bot logged in as BotName#1234 (ID: 123456789)
2026-08-30 10:15:24 - discord_bot - INFO - Connected to 5 guild(s)
2026-08-30 10:15:45 - discord_bot - WARNING - 🚨 NUKE ATTEMPT DETECTED in MyServer: User#1234 - Role Deletion Spam
```

### Audit Trail

All moderation actions are logged:
- Who performed the action
- What action was taken
- Who/what was affected
- Timestamp
- Reason (if provided)

---

## 🔐 Security Features

### Permission Checks
- Prevents actions against equal/higher role users
- Requires proper permissions for each command
- Validates user authority

### Input Validation
- Command argument validation
- Rate limiting on mass actions
- Safe string handling

### Token Safety
- Detects token patterns in messages
- Automatically deletes suspicious messages
- Never logs raw tokens
- Regeneration support in config

---

## 🚀 Performance

### Action Tracking
- Real-time in-memory tracking
- Automatic cleanup of old data
- Efficient time-based filtering
- Minimal CPU/Memory overhead

### Database
- SQLite for fast local storage
- Asynchronous queries
- Connection pooling
- Automatic backups (suggested)

### Scalability
- Handles multiple guilds
- Supports thousands of events
- Efficient caching
- Configurable thresholds

---

## 📈 Statistics

Monitor bot health:

```
!stats

Shows:
- Number of guilds
- Total users seen
- Loaded command modules
- Current latency (ping)
```

---

## 🤝 Integration Points

### Discord Events Monitored
- Guild role deletions
- Guild channel deletions
- Member removals (kick/ban)
- Message creation (for self-bot detection)
- Ready event (startup)
- Command execution

### Extensible Architecture
- Plugin-based cog system
- Custom event handlers
- Database abstraction
- Configuration-driven features

---

**For detailed command help, run `!help` in Discord**
