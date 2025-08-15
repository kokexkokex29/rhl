#!/usr/bin/env python3
"""
Discord Football Club Management Bot - Main Entry Point
Handles bot startup and keep-alive web server
"""

import asyncio
import threading
import os
import logging
from bot import FootballBot
from web_server import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_web_server():
    """Run Flask web server in a separate thread"""
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        logger.error(f"Web server error: {e}")

def main():
    """Main function to start bot and web server"""
    # Get Discord bot token from environment
    bot_token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not bot_token:
        logger.error("DISCORD_BOT_TOKEN environment variable is required!")
        return
    
    # Start web server in background thread
    logger.info("Starting keep-alive web server...")
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    # Initialize and run the Discord bot
    logger.info("Starting Discord bot...")
    bot = FootballBot()
    
    try:
        bot.run(bot_token)
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        logger.info("Bot shutting down...")

if __name__ == "__main__":
    main()
