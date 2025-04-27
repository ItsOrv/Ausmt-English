"""
This file serves as an entry point for the admin functionality.
The admin functionality has been modularized into separate files:
- admin_core.py - Core admin functionality
- admin_utils.py - Utility functions for admin
- admin_broadcast.py - Broadcasting functionality
- admin_teachers.py - Teacher management
- admin_courses.py - Course management
- admin_terms.py - Term management
- admin_faq.py - FAQ management
- admin_payments.py - Payment management
"""

from handlers.admin_core import (
    admin_handler,
    back_to_admin_menu_handler,
    cancel_admin_handler,
    register_admin_handlers
)

# Re-export key components for backwards compatibility
__all__ = [
    'admin_handler', 
    'back_to_admin_menu_handler',
    'cancel_admin_handler',
    'register_admin_handlers'
]

# The main registration function register_admin_handlers in admin_core.py
# will register all handlers from the modular admin components.