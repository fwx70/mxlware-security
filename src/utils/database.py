import aiosqlite
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger("discord_bot")

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
    
    async def init_db(self):
        """Initialize database tables"""
        self.conn = await aiosqlite.connect(self.db_path)
        
        # Anti-nuke logs
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS antinuke_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                action_type TEXT,
                user_id INTEGER,
                target_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        """)
        
        # Anti-self-bot logs
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS antiself_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                violation_type TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        """)
        
        # Guild settings
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                antinuke_enabled INTEGER DEFAULT 1,
                antiself_enabled INTEGER DEFAULT 1,
                log_channel_id INTEGER,
                admin_role_ids TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS guild_whitelist (
                guild_id INTEGER,
                user_id INTEGER,
                added_by INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (guild_id, user_id)
            )
        """)

        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS guild_whitelist_roles (
                guild_id INTEGER,
                role_id INTEGER,
                added_by INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (guild_id, role_id)
            )
        """)
        
        # User warnings
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS user_warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                reason TEXT,
                warned_by INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self.conn.commit()
        logger.info("Database tables initialized")
    
    async def log_antinuke_action(self, guild_id, action_type, user_id, target_id, details=None):
        """Log anti-nuke action"""
        await self.conn.execute("""
            INSERT INTO antinuke_logs (guild_id, action_type, user_id, target_id, details)
            VALUES (?, ?, ?, ?, ?)
        """, (guild_id, action_type, user_id, target_id, details))
        await self.conn.commit()
    
    async def log_antiself_action(self, guild_id, user_id, violation_type, details=None):
        """Log anti-self-bot action"""
        await self.conn.execute("""
            INSERT INTO antiself_logs (guild_id, user_id, violation_type, details)
            VALUES (?, ?, ?, ?)
        """, (guild_id, user_id, violation_type, details))
        await self.conn.commit()
    
    async def add_warning(self, guild_id, user_id, reason, warned_by):
        """Add warning to user"""
        await self.conn.execute("""
            INSERT INTO user_warnings (guild_id, user_id, reason, warned_by)
            VALUES (?, ?, ?, ?)
        """, (guild_id, user_id, reason, warned_by))
        await self.conn.commit()
    
    async def get_user_warnings(self, guild_id, user_id):
        """Get user warnings count"""
        async with self.conn.execute("""
            SELECT COUNT(*) FROM user_warnings WHERE guild_id = ? AND user_id = ?
        """, (guild_id, user_id)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0
    
    async def set_guild_log_channel(self, guild_id, channel_id):
        """Set the configured guild log channel."""
        await self.conn.execute("""
            INSERT INTO guild_settings (guild_id, log_channel_id)
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET log_channel_id = excluded.log_channel_id
        """, (guild_id, channel_id))
        await self.conn.commit()

    async def get_guild_log_channel(self, guild_id):
        """Get the configured guild log channel ID."""
        async with self.conn.execute("""
            SELECT log_channel_id FROM guild_settings WHERE guild_id = ?
        """, (guild_id,)) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else None

    async def add_whitelist_user(self, guild_id, user_id, added_by):
        """Add a user to the guild whitelist."""
        await self.conn.execute("""
            INSERT OR REPLACE INTO guild_whitelist (guild_id, user_id, added_by)
            VALUES (?, ?, ?)
        """, (guild_id, user_id, added_by))
        await self.conn.commit()

    async def remove_whitelist_user(self, guild_id, user_id):
        """Remove a user from the guild whitelist."""
        await self.conn.execute("""
            DELETE FROM guild_whitelist WHERE guild_id = ? AND user_id = ?
        """, (guild_id, user_id))
        await self.conn.commit()

    async def add_whitelist_role(self, guild_id, role_id, added_by):
        """Add a role to the guild whitelist."""
        await self.conn.execute("""
            INSERT OR REPLACE INTO guild_whitelist_roles (guild_id, role_id, added_by)
            VALUES (?, ?, ?)
        """, (guild_id, role_id, added_by))
        await self.conn.commit()

    async def remove_whitelist_role(self, guild_id, role_id):
        """Remove a role from the guild whitelist."""
        await self.conn.execute("""
            DELETE FROM guild_whitelist_roles WHERE guild_id = ? AND role_id = ?
        """, (guild_id, role_id))
        await self.conn.commit()

    async def list_whitelist_users(self, guild_id):
        """List cached whitelist users for a guild."""
        async with self.conn.execute("""
            SELECT user_id FROM guild_whitelist WHERE guild_id = ?
            ORDER BY created_at ASC
        """, (guild_id,)) as cursor:
            return [row[0] for row in await cursor.fetchall()]

    async def list_whitelist_roles(self, guild_id):
        """List cached whitelist roles for a guild."""
        async with self.conn.execute("""
            SELECT role_id FROM guild_whitelist_roles WHERE guild_id = ?
            ORDER BY created_at ASC
        """, (guild_id,)) as cursor:
            return [row[0] for row in await cursor.fetchall()]

    async def close(self):
        """Close database connection"""
        if self.conn:
            await self.conn.close()
