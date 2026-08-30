# Quick Start Guide

## One-Command Auto-Setup (Recommended)

Complete setup of the bot with anti-nuke and anti-self-bot protections in one command:

```bash
python autosetup.py
```

This will:
- Install all dependencies
- Create required directories (data, logs)
- Initialize the database with protection tables
- Setup configuration files
- Enable Anti-Nuke Protection
- Enable Anti-Self-Bot Protection
- Verify all components are ready

Then run:
```bash
python main.py
```

## Manual Setup (Alternative)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Bot Token
```bash
cp .env.example .env
# Edit .env and add your Discord bot token
nano .env  # or open in your editor
```

Get your token from: https://discord.com/developers/applications

### 3. Run Setup Script
```bash
python setup.py
```

### 4. Start the Bot
```bash
python main.py
```

You should see:
```
Bot logged in as BotName#1234 (ID: 123456789)
Connected to X guild(s)
```

## Protection Systems

### Anti-Nuke Protection
- Monitors guild roles, channels, members, and bans
- Tracks suspicious mass deletion patterns
- Configurable thresholds in `config.py`
- Logs to: `logs/protection_antinuke.log`

### Anti-Self-Bot Protection
- Detects self-bot patterns and malicious activity
- Blocks suspicious automation patterns
- Monitors message patterns for API abuse
- Logs to: `logs/protection_antiself.log`

Both protection systems log to the main bot log: `logs/bot.log`

## Common Commands

### For Admins
- `!help` - Show all commands
- `!warn @user reason` - Warn a user
- `!kick @user reason` - Kick a user
- `!ban @user reason` - Ban a user
- `!mute @user reason` - Mute a user
- `!unmute @user` - Unmute a user
- `!purge 10` - Delete last 10 messages

### For Everyone
- `!ping` - Check bot latency
- `!userinfo @user` - Get user info
- `!serverinfo` - Get server info
- `!joke` - Random joke
- `!8ball question?` - Ask magic 8-ball
- `!dice` - Roll a dice
- `!flip` - Flip a coin

### For Bot Owner
- `!stats` - Show bot statistics
- `!antinuke enable/disable` - Toggle anti-nuke
- `!antiself enable/disable` - Toggle anti-self-bot
- `!reload moderator` - Reload a command category

## Troubleshooting

### "Token is invalid"
- Go to Discord Developer Portal
- Regenerate the bot token
- Update .env file

### "Bot shows as offline"
- Check internet connection
- Verify token is correct
- Check Discord API status

### "Command not working"
- Make sure bot has Send Messages permission
- Check command prefix is `!`
- Verify you have required permissions

### "Anti-nuke not detecting actions"
- Ensure bot has Audit Log read permissions
- Check ANTINUKE_ENABLED is True in config.py
- Verify thresholds in config.py

## Adding Your Own Commands

Create a new file in `src/cogs/` (example: `src/cogs/mycog.py`):

```python
import discord
from discord.ext import commands

class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="mycommand")
    async def my_command(self, ctx, *, args):
        """My custom command"""
        await ctx.send("Hello!")

async def setup(bot):
    await bot.add_cog(MyCog(bot))
```

Reload with: `!reload mycog`

## Useful Links

- Discord.py Docs: https://discordpy.readthedocs.io/
- Discord Developer Portal: https://discord.com/developers/applications
- Discord Permissions: https://discordapi.com/permissions
- Bot Inviter: Add your bot to servers with permission link

## Next Steps

1. Customize bot status in config.py
2. Adjust anti-nuke thresholds for your server
3. Add more commands based on your needs
4. Join Discord support servers for help
5. Keep discord.py library updated: `pip install --upgrade discord.py`

## Important Notes

⚠️ **Never share your bot token**
- Always keep .env file private
- Add .env to .gitignore (already done)
- Regenerate token if accidentally exposed

✅ **Bot Permissions Checklist**
- [ ] Manage Messages
- [ ] Manage Roles
- [ ] Manage Channels
- [ ] Kick Members
- [ ] Ban Members
- [ ] Embed Links
- [ ] Send Messages
- [ ] View Channels

---

**Having issues?** Check `logs/bot.log` for detailed error messages.
