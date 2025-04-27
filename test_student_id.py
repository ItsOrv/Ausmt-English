#!/usr/bin/env python3
from utils.excel_handler import ExcelHandler

handler = ExcelHandler()

# Try looking up a student ID from the sample data
student_id = "9512345"  # This should exist in the sample data
exists, first_name, last_name = handler.check_student_id(student_id)

if exists:
    print(f"Found student: {first_name} {last_name} with ID {student_id}")
else:
    print(f"Student with ID {student_id} not found")

# Try with a non-existent student ID
student_id = "1234567"  # This shouldn't exist
exists, first_name, last_name = handler.check_student_id(student_id)

if exists:
    print(f"Found student: {first_name} {last_name} with ID {student_id}")
else:
    print(f"Student with ID {student_id} not found") 