import logging
import asyncio
import os
from telethon import TelegramClient, events
from dotenv import load_dotenv

# Local imports
from database import Database
from utils.config import Config
from handlers.start import register_start_handlers
from handlers.registration import register_registration_handlers
from handlers.admin import register_admin_handlers
from handlers.admin_utils import process_admin_message

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure data directories exist
os.makedirs('data/receipts', exist_ok=True)

async def main():
    """
    Main function to start the bot.
    """
    # Load environment variables
    load_dotenv()
    
    # Validate configuration
    if not Config.validate_config():
        logger.error("Invalid configuration. Please check your .env file.")
        return
    
    # Initialize database
    db = Database()
    
    # Create the Telegram client
    bot = TelegramClient('language_course_bot', Config.API_ID, Config.API_HASH)
    
    # Register global message handler for admin text input
    @bot.on(events.NewMessage(func=lambda e: e.text and not e.text.startswith('/')))
    async def handle_text_messages(event):
        """Handler for text messages that could be part of admin workflows."""
        # Try to process as admin message first
        processed = await process_admin_message(event)
        if processed:
            return
        
        # If not processed as admin message, can add other text message handlers here
        # or just ignore the message
    
    # Register feature-specific handlers
    await register_start_handlers(bot)
    await register_registration_handlers(bot)
    await register_admin_handlers(bot)
    
    logger.info("Starting the bot...")
    
    # Start the bot
    await bot.start(bot_token=Config.BOT_TOKEN)
    logger.info("Bot started. Press Ctrl+C to stop.")
    
    # Run the bot until disconnected
    await bot.run_until_disconnected()
    
    # Close database connection
    db.close()

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main()) 