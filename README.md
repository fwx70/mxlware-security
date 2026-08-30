# Enhanced Discord Bot - Complete Documentation

## 🤖 Features

### Anti-Nuke Protection
- **Role Deletion Detection**: Monitors and prevents mass role deletions
- **Channel Deletion Detection**: Tracks channel deletions and alerts on suspicious activity
- **Mass Ban/Kick Detection**: Prevents bulk member removals
- **Action Tracking**: Real-time tracking of actions per guild
- **Automatic Logging**: All suspicious activities are logged to database
- **Configurable Thresholds**: Adjust sensitivity based on your needs

### Anti-Self-Bot Protection
- **Pattern Detection**: Scans messages for self-bot indicators
- **Suspicious Content Blocking**: Automatically blocks messages with suspicious patterns
- **Account Age Analysis**: Flags newer accounts with suspicious behavior
- **Mass Action Detection**: Identifies automated mass actions
- **User Reputation Tracking**: Maintains reputation scores for users

### Command Categories

#### Moderation Commands
- `!warn <member> [reason]` - Warn a user
- `!kick <member> [reason]` - Kick a member
- `!ban <member> [reason]` - Ban a member
- `!mute <member> [reason]` - Mute a member
- `!unmute <member>` - Unmute a member
- `!purge <amount>` - Delete multiple messages
- `!unban <user> [reason]` - Unban a user
- `!slowmode [seconds]` - Set channel slowmode
- `!lock [channel]` - Lock a channel
- `!unlock [channel]` - Unlock a channel
- `!massrole <role>` - Give role to all members
- `!addrole <member> <role>` - Add role to member
- `!removerole <member> <role>` - Remove role from member

#### Utility Commands
- `!ping` - Check bot latency
- `!userinfo [member]` - Get user information
- `!serverinfo` - Get server information
- `!avatar [member]` - Get user avatar
- `!role <role>` - Get role information
- `!help [category]` - Show help menu
- `!botinfo` - Get bot information
- `!membercount` - Get member count
- `!invite` - Get bot invite link
- `!uptime` - Get bot uptime

#### Fun Commands
- `!joke` - Tell a random joke
- `!8ball <question>` - Ask the magic 8-ball
- `!dice [sides]` - Roll a dice
- `!flip` - Flip a coin
- `!choose <option1> <option2> ...` - Choose between options
- `!say <text>` - Make bot say something

#### Admin Commands (Owner/Admin Only)
- `!status <text>` - Set bot status
- `!reload <cog>` - Reload a cog
- `!load <cog>` - Load a cog
- `!unload <cog>` - Unload a cog
- `!stats` - Show bot statistics
- `!antinuke [enable/disable]` - Configure anti-nuke protection
- `!antiself [enable/disable]` - Configure anti-self-bot protection

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Step 1: Clone or Extract the Repository
```bash
cd /path/to/fw70
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
1. Copy `.env.example` to `.env`
2. Edit `.env` with your bot details:
```env
DISCORD_TOKEN=your_bot_token_here
COMMAND_PREFIX=!
OWNER_ID=your_discord_user_id
```

### Step 4: Run the Bot
```bash
python main.py
```

Or for development with auto-reload:
```bash
pip install -r requirements.txt  # ensures nodemon alternative
python -m nodemon main.py  # if nodemon is installed
```

## 📋 Project Structure

```
fw70/
├── main.py                    # Entry point
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .env                      # Your actual environment variables (create from example)
├── src/
│   ├── bot.py               # Main bot class
│   ├── utils/
│   │   ├── logger.py        # Logging setup
│   │   └── database.py      # Database operations
│   ├── protection/
│   │   ├── antinuke.py      # Anti-nuke protection system
│   │   └── antiself.py      # Anti-self-bot protection system
│   └── cogs/                # Command cogs
│       ├── moderator.py     # Moderation commands
│       ├── moderation_advanced.py # Advanced moderation
│       ├── utility.py       # Utility commands
│       ├── fun.py           # Fun commands
│       ├── admin.py         # Admin commands
│       └── info.py          # Information commands
├── data/
│   └── bot.db              # SQLite database (auto-created)
└── logs/
    └── bot.log             # Bot logs (auto-created)
```

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Anti-Nuke Settings
MAX_ROLE_DELETIONS_PER_MINUTE = 3
MAX_CHANNEL_DELETIONS_PER_MINUTE = 5
MAX_BANS_PER_MINUTE = 10
MAX_KICKS_PER_MINUTE = 10
MASS_ACTION_THRESHOLD = 3

# Anti-Self-Bot Settings
ANTISELF_ENABLED = True
DETECT_BOT_ACTIVITY_PATTERNS = True
BLOCK_SUSPICIOUS_PATTERNS = True
```

## 🔒 Permissions Required

The bot requires the following permissions:
- View Channels
- Send Messages
- Embed Links
- Manage Messages
- Manage Roles
- Manage Channels
- Kick Members
- Ban Members
- Read Message History
- Moderate Members

## 🛡️ Anti-Nuke Features in Detail

### How It Works
1. **Real-time Monitoring**: The bot monitors all guild events (role/channel deletions, member removals)
2. **Action Tracking**: All actions are tracked with timestamps
3. **Threshold Detection**: When actions exceed configured limits in 1 minute, an alert is triggered
4. **Automated Response**: The system attempts to remove the offending user's permissions
5. **Logging**: All suspicious activity is logged to the database for audit trails

### Example Scenarios
- If 3 or more roles are deleted in 1 minute → Alert triggered
- If 5 or more channels are deleted in 1 minute → Alert triggered
- If 10 or more members are banned in 1 minute → Alert triggered
- If 10 or more members are kicked in 1 minute → Alert triggered

## 🤖 Anti-Self-Bot Features in Detail

### Detection Patterns
The bot detects:
- Self-bot code references (token usage, self.bot patterns)
- Webhook automation attempts
- Mass action commands
- Suspicious command patterns

### Response Actions
- Deletes suspicious messages
- Sends warning DMs to users
- Logs violations to database
- Flags user accounts for review

## 📊 Database Structure

The bot uses SQLite with the following tables:
- `antinuke_logs`: Records all anti-nuke actions
- `antiself_logs`: Records all anti-self-bot violations
- `guild_settings`: Per-guild configuration
- `user_warnings`: User warning history

## 🆘 Troubleshooting

### Bot won't start
- Check if token is valid in `.env`
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check logs in `logs/bot.log`

### Commands not responding
- Make sure bot has Send Messages permission
- Check if command prefix is correct (default: `!`)
- Verify bot has required permissions for the command

### Anti-nuke not working
- Check if ANTINUKE_ENABLED is True in config.py
- Ensure bot has Audit Log read permissions
- Check that threshold values make sense for your guild

### Database errors
- Delete `data/bot.db` to reset (all data will be lost)
- Ensure `data/` directory exists and is writable
- Check available disk space

## 📝 Logging

Logs are saved to `logs/bot.log` and also printed to console.
Log levels can be configured in `config.py`:
```python
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🔄 Updating & Maintenance

### Reload a cog (without restarting bot)
```
!reload <cog_name>
```

Example: `!reload moderator`

### Load/Unload cogs dynamically
```
!load <cog_name>
!unload <cog_name>
```

## 📞 Support

For issues or questions:
1. Check the logs in `logs/bot.log`
2. Verify configuration in `config.py`
3. Ensure all permissions are granted to the bot
4. Check Discord API status

## 📄 License

MIT License - Feel free to modify and redistribute

## 🚀 Future Enhancements

Planned features:
- [ ] Music player integration
- [ ] Economy system with currency
- [ ] XP/Leveling system
- [ ] Custom welcome messages
- [ ] Role auto-assignment
- [ ] Ticket system
- [ ] Reaction roles
- [ ] Custom commands
- [ ] Statistics dashboard

---

**Version**: 2.0 Enhanced
**Last Updated**: 2026-08-30
**Status**: Production Ready
