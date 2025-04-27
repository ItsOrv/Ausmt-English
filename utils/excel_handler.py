import os
import pandas as pd
import logging
from dotenv import load_dotenv
from utils.config import Config
import openpyxl
from openpyxl.utils import column_index_from_string

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExcelHandler:
    def __init__(self):
        """Initialize Excel handler with path from environment variables."""
        self.excel_path = Config.EXCEL_PATH
        # Store column indices (convert from Excel column letters to numeric indices)
        self.column_indices = {
            'email': column_index_from_string(Config.EMAIL_COLUMN) - 1,
            'first_name': column_index_from_string(Config.FIRST_NAME_COLUMN) - 1,
            'last_name': column_index_from_string(Config.LAST_NAME_COLUMN) - 1,
            'father_name': column_index_from_string(Config.FATHER_NAME_COLUMN) - 1,
            'faculty': column_index_from_string(Config.FACULTY_COLUMN) - 1,
            'major': column_index_from_string(Config.MAJOR_COLUMN) - 1,
            'education_level': column_index_from_string(Config.EDUCATION_LEVEL_COLUMN) - 1,
            'phone': column_index_from_string(Config.PHONE_COLUMN) - 1,
            # Add columns for national ID and student ID
            'national_id': column_index_from_string(Config.NATIONAL_ID_COLUMN) - 1 if hasattr(Config, 'NATIONAL_ID_COLUMN') else column_index_from_string('G') - 1,
            'student_id': column_index_from_string(Config.STUDENT_ID_COLUMN) - 1 if hasattr(Config, 'STUDENT_ID_COLUMN') else column_index_from_string('I') - 1
        }
        self._validate_excel_file()
    
    def _validate_excel_file(self):
        """Validate that the Excel file exists."""
        if not os.path.exists(self.excel_path):
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.excel_path), exist_ok=True)
            logger.error(f"Excel file not found at {self.excel_path}. Please add a valid student data file.")
            # We won't create a sample file as we now have a real data file
    
    def check_student_id(self, student_id):
        """
        Check if a student ID or national ID exists in the Excel file.
        Searches for matches in both national_id (column G) and student_id (column I) columns.
        
        Args:
            student_id (str): Student ID or national ID to check
            
        Returns:
            tuple: (exists, first_name, last_name) or (False, None, None) if not found
        """
        try:
            # Load the Excel file
            wb = openpyxl.load_workbook(self.excel_path)
            ws = wb.active
            
            # Convert student_id to string to ensure proper comparison
            student_id = str(student_id)
            
            logger.info(f"Looking for student ID or national ID: {student_id}")
            
            # Find the student
            found = False
            first_name = None
            last_name = None
            
            # We'll search in both national_id (column G) and student_id (column I) 
            for row in ws.iter_rows(min_row=2, max_col=ws.max_column, max_row=ws.max_row):
                # Check national ID
                national_id_value = str(row[self.column_indices['national_id']].value).strip() if row[self.column_indices['national_id']].value is not None else ""
                
                # Check student ID
                student_id_value = str(row[self.column_indices['student_id']].value).strip() if row[self.column_indices['student_id']].value is not None else ""
                
                # Compare with input (which could be national ID or student ID)
                if national_id_value == student_id or student_id_value == student_id:
                    logger.info(f"Match found for ID: {student_id}")
                    
                    # Get name and last name from the columns specified in config
                    first_name = row[self.column_indices['first_name']].value
                    last_name = row[self.column_indices['last_name']].value
                    
                    # Handle case where name might be None
                    if first_name is None:
                        first_name = "نام نامشخص"
                    if last_name is None:
                        last_name = "نام خانوادگی نامشخص"
                        
                    logger.info(f"Found student: {first_name} {last_name}")
                    found = True
                    break
            
            return found, first_name, last_name
                
        except Exception as e:
            logger.error(f"Error checking student ID: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False, None, None 