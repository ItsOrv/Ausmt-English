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
    
    # Add sample data for testing
    db.add_sample_data()
    logger.info("Sample data added to database.")
    
    # Create the Telegram client
    bot = TelegramClient('language_course_bot', Config.API_ID, Config.API_HASH)
    
    # Register handlers
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