#!/usr/bin/env python3
from utils.excel_handler import ExcelHandler

handler = ExcelHandler()

# Try looking up a real student email from the data file
student_emails = [
    "worldn12@gmail.com",  # First email in the file
    "mahakazizi27@gmail.com",  # Second email
    "elaheesmailikh2024@gmail.com"  # Third email
]

print("Testing student lookup by email:")
for email in student_emails:
    print(f"\nLooking up student with email: {email}")
    exists, first_name, last_name = handler.check_student_id(email)
    
    if exists:
        print(f"✅ Found student: {first_name} {last_name}")
    else:
        print(f"❌ Student not found")

# Try with a non-existent email
non_existent_email = "nonexistent@example.com"
print(f"\nLooking up non-existent email: {non_existent_email}")
exists, first_name, last_name = handler.check_student_id(non_existent_email)

if exists:
    print(f"Found student: {first_name} {last_name}")
else:
    print("❌ Student not found (expected result)") 