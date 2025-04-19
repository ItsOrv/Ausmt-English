import os
import pandas as pd
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

class ExcelHandler:
    def __init__(self):
        """Initialize Excel handler with path from environment variables."""
        self.excel_path = os.getenv('EXCEL_PATH', 'data/students.xlsx')
        self._validate_excel_file()
    
    def _validate_excel_file(self):
        """Validate that the Excel file exists, if not create a sample one."""
        if not os.path.exists(self.excel_path):
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.excel_path), exist_ok=True)
            
            # Create sample Excel file
            df = pd.DataFrame({
                'student_id': ['9512345', '9623456', '9734567', '9845678', '9956789'],
                'first_name': ['محمد', 'علی', 'فاطمه', 'زهرا', 'امیر'],
                'last_name': ['احمدی', 'محمدی', 'حسینی', 'رضایی', 'کریمی'],
                'major': ['مهندسی کامپیوتر', 'مهندسی برق', 'مهندسی عمران', 'علوم کامپیوتر', 'پزشکی'],
                'entry_year': [1395, 1396, 1397, 1398, 1399]
            })
            
            df.to_excel(self.excel_path, index=False)
            logger.info(f"Created sample Excel file at {self.excel_path}")
    
    def check_student_id(self, student_id):
        """
        Check if a student ID exists in the Excel file.
        
        Args:
            student_id (str): Student ID to check
            
        Returns:
            tuple: (exists, first_name, last_name) or (False, None, None) if not found
        """
        try:
            df = pd.read_excel(self.excel_path)
            
            # Convert student_id to string to ensure proper comparison
            df['student_id'] = df['student_id'].astype(str)
            student_id = str(student_id)
            
            # Find the student
            student = df[df['student_id'] == student_id]
            
            if not student.empty:
                first_name = student['first_name'].iloc[0]
                last_name = student['last_name'].iloc[0]
                return True, first_name, last_name
            else:
                return False, None, None
                
        except Exception as e:
            logger.error(f"Error checking student ID: {e}")
            return False, None, None 