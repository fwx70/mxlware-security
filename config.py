import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", ",")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# Anti-Nuke Settings
ANTINUKE_ENABLED = True
MAX_ROLE_DELETIONS_PER_MINUTE = 3
MAX_CHANNEL_DELETIONS_PER_MINUTE = 5
MAX_BANS_PER_MINUTE = 10
MAX_KICKS_PER_MINUTE = 10
MASS_ACTION_THRESHOLD = 3  # Minimum actions to trigger anti-nuke

# Anti-Self-Bot Settings
ANTISELF_ENABLED = True
DETECT_BOT_ACTIVITY_PATTERNS = True
BLOCK_SUSPICIOUS_PATTERNS = True

# Database
DATABASE_PATH = "data/bot.db"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/bot.log"

# Features
ENABLE_MUSIC = False
ENABLE_ECONOMY = False
ENABLE_XP = False
