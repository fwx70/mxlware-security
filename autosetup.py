#!/usr/bin/env python3
"""
One-command auto-setup for Discord Bot with Anti-Nuke and Anti-Self-Bot protection
Run: python autosetup.py
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        if result.returncode == 0:
            print(f"✓ {description} - COMPLETED")
            return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} - FAILED")
        return False
    return True

def main():
    """Run complete auto-setup"""
    print("\n" + "="*60)
    print("Discord Bot - Complete Auto-Setup")
    print("="*60)
    print("\nThis will setup everything needed to run the bot:")
    print("  1. Install dependencies")
    print("  2. Create directories")
    print("  3. Initialize database with protection systems")
    print("  4. Setup configuration")
    print("  5. Enable Anti-Nuke Protection")
    print("  6. Enable Anti-Self-Bot Protection")
    
    # Check if .env exists
    if not Path(".env").exists():
        print("\n" + "!"*60)
        print("WARNING: .env file not found!")
        print("!"*60)
        response = input("\nDo you want to create .env from .env.example? (y/n): ").strip().lower()
        if response == 'y':
            if Path(".env.example").exists():
                with open(".env.example") as src:
                    with open(".env", "w") as dst:
                        dst.write(src.read())
                print("Created .env - Please edit it with your Discord bot token")
            else:
                print("Creating default .env file...")
                with open(".env", "w") as f:
                    f.write("DISCORD_TOKEN=YOUR_BOT_TOKEN_HERE\n")
                    f.write("COMMAND_PREFIX=!\n")
                    f.write("OWNER_ID=0\n")
                print("Created .env - Please edit it with your Discord bot token")
        else:
            print("Skipping .env setup")
    
    # Step 1: Install dependencies
    if not run_command(
        "pip install -q -r requirements.txt",
        "Installing dependencies"
    ):
        print("\nFailed to install dependencies!")
        sys.exit(1)
    
    # Step 2: Run setup script
    if not run_command(
        f"{sys.executable} setup.py",
        "Running bot setup"
    ):
        print("\nSetup script failed!")
        sys.exit(1)
    
    # Step 3: Verify setup
    print("\n" + "="*60)
    print("Verifying setup...")
    print("="*60)
    
    checks = [
        ("logs directory", Path("logs").exists()),
        ("data directory", Path("data").exists()),
        ("database file", Path("data/bot.db").exists()),
        (".env file", Path(".env").exists()),
    ]
    
    all_good = True
    for check_name, check_result in checks:
        status = "✓" if check_result else "✗"
        print(f"{status} {check_name}")
        if not check_result:
            all_good = False
    
    print("\n" + "="*60)
    if all_good:
        print("SETUP COMPLETE!")
        print("="*60)
        print("\nYour bot is ready with:")
        print("  ✓ Anti-Nuke Protection (enabled)")
        print("  ✓ Anti-Self-Bot Protection (enabled)")
        print("  ✓ Database initialized")
        print("  ✓ Logging configured")
        print("\nYou can now start the bot with:")
        print("  python main.py")
        print("\nLogs will be saved to: logs/bot.log")
        print("\nProtection system logs:")
        print("  - Anti-Nuke: logs/protection_antinuke.log")
        print("  - Anti-Self-Bot: logs/protection_antiself.log")
    else:
        print("SETUP INCOMPLETE!")
        print("="*60)
        print("\nSome checks failed. Please review the output above.")
        sys.exit(1)
    
    print()

if __name__ == "__main__":
    main()
