#!/usr/bin/env python3
from utils.config import Config
from utils.excel_handler import ExcelHandler

print("Excel path:", Config.EXCEL_PATH)
print("Column mappings:")
print(f"  Email: {Config.EMAIL_COLUMN}")
print(f"  First Name: {Config.FIRST_NAME_COLUMN}")
print(f"  Last Name: {Config.LAST_NAME_COLUMN}")
print(f"  Father Name: {Config.FATHER_NAME_COLUMN}")
print(f"  Faculty: {Config.FACULTY_COLUMN}")
print(f"  Major: {Config.MAJOR_COLUMN}")
print(f"  Education Level: {Config.EDUCATION_LEVEL_COLUMN}")
print(f"  Phone: {Config.PHONE_COLUMN}")

try:
    print("\nInitializing Excel handler...")
    handler = ExcelHandler()
    print("Column indices:", handler.column_indices)
    print("Excel handler initialized successfully!")
except Exception as e:
    print(f"Error initializing Excel handler: {e}") 