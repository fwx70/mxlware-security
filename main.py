#!/usr/bin/env python3
"""
Enhanced Discord Bot with Anti-Nuke and Anti-Self-Bot Protection
Main entry point for the bot
"""

from src.bot import main
import sys

if __name__ == "__main__":
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot shutdown by user")
        sys.exit(0)
    except Exception as se:
        print(f"Fatal error: {se}")
        sys.exit(1)
