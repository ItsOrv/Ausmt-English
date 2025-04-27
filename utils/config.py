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
    ADMIN_ID_RAW = os.getenv('ADMIN_ID', '0')
    try:
        ADMIN_ID = int(ADMIN_ID_RAW)
        logger.info(f"ADMIN_ID loaded as: {ADMIN_ID} (type: {type(ADMIN_ID)})")
    except ValueError:
        logger.error(f"Failed to parse ADMIN_ID '{ADMIN_ID_RAW}' as integer, defaulting to 0")
        ADMIN_ID = 0
    
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
    NATIONAL_ID_COLUMN = os.getenv('NATIONAL_ID_COLUMN', 'G')  # Default to column G for national ID
    STUDENT_ID_COLUMN = os.getenv('STUDENT_ID_COLUMN', 'I')  # Default to column I for student ID
    
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
            if cls.ADMIN_ID == 0:
                logger.warning("ADMIN_ID is set to 0, which might indicate a problem")
            logger.info(f"Final ADMIN_ID validation: {cls.ADMIN_ID} (type: {type(cls.ADMIN_ID)})")
        except (ValueError, TypeError):
            logger.error("ADMIN_ID must be a valid integer (Telegram user ID)")
            return False
            
        return True 