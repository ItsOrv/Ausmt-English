"""
Utility functions for admin handlers.
"""
from telethon import events
import logging
from utils.keyboards import KeyboardManager
from utils.config import Config
from database import Database

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database instance
db = Database()

# Dictionary to store admin state
admin_state = {}

async def is_admin(event):
    """Check if the sender is an admin."""
    sender = await event.get_sender()
    return str(sender.id) == str(Config.ADMIN_ID)

async def admin_required(event):
    """Check if sender is admin, send error if not."""
    if not await is_admin(event):
        await event.answer("⛔ شما دسترسی به این بخش را ندارید.", alert=True)
        return False
    return True

async def edit_or_respond(event, text, buttons=None):
    """Edit the message if possible, otherwise respond with a new message."""
    try:
        await event.edit(text, buttons=buttons)
    except Exception as e:
        logger.warning(f"Couldn't edit message: {e}")
        await event.respond(text, buttons=buttons)

def clear_admin_state(admin_id):
    """Clear admin state."""
    if admin_id in admin_state:
        del admin_state[admin_id]
        logger.info(f"Cleared admin state for {admin_id}")

# Process text messages from admin based on current state
async def process_admin_message(event):
    """Process text messages from admin based on current state."""
    sender = await event.get_sender()
    
    # If not admin, ignore
    if not await is_admin(event):
        return False
    
    # Import here to avoid circular imports
    from handlers.admin_courses import process_course_message
    from handlers.admin_teachers import process_teacher_message
    from handlers.admin_terms import process_term_message
    from handlers.admin_faq import process_faq_message
    from handlers.admin_broadcast import admin_message_handler
    
    # Try processing the message with each module
    handlers = [
        process_course_message,
        process_teacher_message,
        process_term_message,
        process_faq_message,
        admin_message_handler
    ]
    
    for handler in handlers:
        try:
            result = await handler(event)
            if result:
                return True
        except Exception as e:
            logger.error(f"Error in admin message handler: {e}")
    
    return False 