import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Config:
    """Configuration class to manage environment variables."""
    
    # Telegram API credentials
    API_ID = os.getenv('API_ID')
    API_HASH = os.getenv('API_HASH')
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Admin Telegram ID
    ADMIN_ID = int(os.getenv('ADMIN_ID', 0))
    
    # Payment information
    CARD_NUMBER = os.getenv('CARD_NUMBER', '6219-xxxx-xxxx-xxxx')
    CARD_OWNER = os.getenv('CARD_OWNER', 'نام صاحب حساب')
    
    # Excel file path
    EXCEL_PATH = os.getenv('EXCEL_PATH', 'data/students.xlsx')
    
    # Excel column mappings
    EMAIL_COLUMN = os.getenv('EMAIL_COLUMN', 'A')
    FIRST_NAME_COLUMN = os.getenv('FIRST_NAME_COLUMN', 'C')
    LAST_NAME_COLUMN = os.getenv('LAST_NAME_COLUMN', 'E')
    FATHER_NAME_COLUMN = os.getenv('FATHER_NAME_COLUMN', 'G')
    FACULTY_COLUMN = os.getenv('FACULTY_COLUMN', 'I')
    MAJOR_COLUMN = os.getenv('MAJOR_COLUMN', 'K')
    EDUCATION_LEVEL_COLUMN = os.getenv('EDUCATION_LEVEL_COLUMN', 'N')
    PHONE_COLUMN = os.getenv('PHONE_COLUMN', 'Y')
    
    @classmethod
    def validate_config(cls):
        """Validate that all required environment variables are set."""
        required_vars = ['API_ID', 'API_HASH', 'BOT_TOKEN', 'ADMIN_ID']
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            logger.error("Please create a .env file with these variables or set them in the environment.")
            return False
        
        # Check if ADMIN_ID is a valid integer
        try:
            int(cls.ADMIN_ID)
        except ValueError:
            logger.error("ADMIN_ID must be a valid integer (Telegram user ID)")
            return False
            
        return True 