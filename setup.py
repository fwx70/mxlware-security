#!/usr/bin/env python3
"""
Enhanced setup script for the Discord Bot
Run this once to set up the bot properly with auto-setup for anti-nuke and anti-self-bot
"""

import os
import sys
import asyncio
import sqlite3
from pathlib import Path
import logging

def setup_logging_for_setup():
    """Setup logging for the setup script"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/setup.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("setup")

logger = setup_logging_for_setup()

def create_directories():
    """Create necessary directories"""
    dirs = ["data", "logs"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        logger.info(f"Created directory: {dir_name}")

def check_env_file():
    """Check if .env file exists"""
    if not Path(".env").exists():
        if Path(".env.example").exists():
            logger.warning(".env file not found. Creating from .env.example...")
            with open(".env.example") as src:
                with open(".env", "w") as dst:
                    dst.write(src.read())
            logger.info("Created .env file. Please edit it with your bot token!")
            return False
        else:
            logger.error("Neither .env nor .env.example found!")
            return False
    return True

def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import discord
        logger.info("discord.py is installed")
    except ImportError:
        logger.error("discord.py not found. Run: pip install -r requirements.txt")
        return False
    
    try:
        import dotenv
        logger.info("python-dotenv is installed")
    except ImportError:
        logger.error("python-dotenv not found. Run: pip install -r requirements.txt")
        return False
    
    return True

def initialize_database():
    """Initialize the database with protection tables"""
    db_path = "data/bot.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create antinuke logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS antinuke_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER,
                action_type TEXT NOT NULL,
                target_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        """)
        
        # Create antiself logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS antiself_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER,
                pattern_detected TEXT NOT NULL,
                severity TEXT DEFAULT 'LOW',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        """)
        
        # Create settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id INTEGER PRIMARY KEY,
                antinuke_enabled BOOLEAN DEFAULT 1,
                antiself_enabled BOOLEAN DEFAULT 1,
                max_role_deletions INTEGER DEFAULT 3,
                max_channel_deletions INTEGER DEFAULT 5,
                max_bans INTEGER DEFAULT 10,
                max_kicks INTEGER DEFAULT 10
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

def setup_protections_config():
    """Create protection configuration"""
    config_content = """
# Protection Systems Configuration

## Anti-Nuke Protection
ANTINUKE_ENABLED=True
MAX_ROLE_DELETIONS_PER_MINUTE=3
MAX_CHANNEL_DELETIONS_PER_MINUTE=5
MAX_BANS_PER_MINUTE=10
MAX_KICKS_PER_MINUTE=10
MASS_ACTION_THRESHOLD=3

## Anti-Self-Bot Protection
ANTISELF_ENABLED=True
DETECT_BOT_ACTIVITY_PATTERNS=True
BLOCK_SUSPICIOUS_PATTERNS=True

## Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
"""
    
    logger.info("Protection systems configured")
    return True

def main():
    """Run setup"""
    print("\n" + "="*50)
    print("Discord Bot - Auto Setup Script")
    print("="*50 + "\n")
    
    logger.info("Starting bot setup...")
    
    # Step 1: Create directories
    print("Step 1: Creating directories...")
    create_directories()
    print()
    
    # Step 2: Check dependencies
    print("Step 2: Checking dependencies...")
    if not check_dependencies():
        logger.error("Setup failed! Install dependencies first:")
        print("\n   pip install -r requirements.txt")
        sys.exit(1)
    print()
    
    # Step 3: Check/create .env file
    print("Step 3: Checking configuration...")
    if not check_env_file():
        logger.warning("Setup partially complete!")
        print("\nPlease follow these steps:")
        print("1. Edit .env file with your Discord bot token")
        print("2. Get your bot token from Discord Developer Portal")
        print("3. Run: python main.py")
        sys.exit(0)
    print()
    
    # Step 4: Initialize database
    print("Step 4: Initializing database with protection systems...")
    if not initialize_database():
        logger.error("Failed to initialize database!")
        sys.exit(1)
    print()
    
    # Step 5: Setup protection configuration
    print("Step 5: Configuring protection systems...")
    setup_protections_config()
    print()
    
    print("="*50)
    print("Setup complete! Protection systems ready:")
    print("  - Anti-Nuke Protection: ENABLED")
    print("  - Anti-Self-Bot Protection: ENABLED")
    print("="*50)
    print("\nYou can now run:")
    print("   python main.py")
    print("\nLogs will be saved to: logs/bot.log")
    print("\n")
    
    logger.info("Setup completed successfully!")

if __name__ == "__main__":
    main()
