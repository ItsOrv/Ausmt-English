from telethon import events
import logging
from utils.keyboards import KeyboardManager
from utils.config import Config
from handlers.admin_utils import admin_state, db, logger, is_admin, edit_or_respond, clear_admin_state

# Imports para los otros módulos admin
import handlers.admin_broadcast as admin_broadcast
import handlers.admin_teachers as admin_teachers
import handlers.admin_courses as admin_courses
import handlers.admin_terms as admin_terms
import handlers.admin_faq as admin_faq
import handlers.admin_payments as admin_payments

async def admin_handler(event):
    """Handler principal para el comando admin."""
    sender = await event.get_sender()
    sender_id = sender.id
    
    # Debug logging
    logger.info(f"Admin command received from {sender_id}, ADMIN_ID={Config.ADMIN_ID}, Type: {type(sender_id)} vs {type(Config.ADMIN_ID)}")
    
    # Check if sender is admin
    if str(sender_id) == str(Config.ADMIN_ID):
        admin_message = """🔐 **پنل مدیریت**

به پنل مدیریت ربات ثبت‌نام دوره‌های زبان خوش آمدید.
لطفا از منوی زیر گزینه مورد نظر خود را انتخاب کنید:"""
        
        await event.respond(admin_message, buttons=KeyboardManager.admin_menu())
    else:
        logger.warning(f"Unauthorized admin access attempt from user {sender_id}")
        await event.respond("شما مجوز دسترسی به پنل ادمین را ندارید.")

async def back_to_admin_menu_handler(event):
    """Handler to go back to the admin menu.
    Primary handler for returning to the admin menu from any submenu.
    """
    sender = await event.get_sender()
    sender_id = sender.id
    
    # Check if sender is admin
    if await is_admin(event):
        logger.info(f"Admin {sender_id} returning to admin menu")
        
        # Clear any admin state if it exists
        clear_admin_state(sender_id)
        
        admin_message = """🔐 **پنل مدیریت**

به پنل مدیریت ربات ثبت‌نام دوره‌های زبان خوش آمدید.
لطفا از منوی زیر گزینه مورد نظر خود را انتخاب کنید:"""
        
        await edit_or_respond(event, admin_message, buttons=KeyboardManager.admin_menu())
    else:
        await event.answer("⛔ شما دسترسی به این بخش را ندارید.", alert=True)

async def exit_admin_panel_handler(event):
    """Handler for exiting admin panel back to main menu."""
    sender = await event.get_sender()
    
    if not await is_admin(event):
        await event.answer("⛔ شما دسترسی به این بخش را ندارید.", alert=True)
        return
    
    # Clear admin state
    clear_admin_state(sender.id)
    
    main_message = """👋 به ربات ثبت‌نام دوره‌های زبان خوش آمدید.

از منوی زیر گزینه مورد نظر خود را انتخاب کنید:"""
    
    await edit_or_respond(event, main_message, buttons=KeyboardManager.main_menu())
    logger.info(f"Admin {sender.id} exited admin panel to main menu")

async def cancel_admin_handler(event):
    """Handler for admin canceling an action."""
    sender = await event.get_sender()
    
    if not await is_admin(event):
        return
    
    # Clear admin state
    clear_admin_state(sender.id)
    
    await event.respond("عملیات لغو شد.", buttons=KeyboardManager.admin_menu())

async def register_admin_handlers(bot):
    """Register all admin handlers."""
    
    # Registro del manejador principal de admin
    bot.add_event_handler(admin_handler, events.NewMessage(pattern='/admin'))
    
    # Registro del manejador para volver al menú de admin
    bot.add_event_handler(back_to_admin_menu_handler, events.CallbackQuery(pattern=r'back_to_admin_menu'))
    bot.add_event_handler(back_to_admin_menu_handler, events.CallbackQuery(pattern=r'admin_back'))
    
    # Registro del manejador para salir del panel de admin
    bot.add_event_handler(exit_admin_panel_handler, events.CallbackQuery(pattern=r'exit_admin_panel'))
    
    # Registro del manejador para cancelar acciones
    bot.add_event_handler(cancel_admin_handler, events.NewMessage(pattern='/cancel'))
    
    # Registrar handlers de los otros módulos
    await admin_broadcast.register_handlers(bot)
    await admin_teachers.register_handlers(bot)
    await admin_courses.register_handlers(bot)
    await admin_terms.register_handlers(bot)
    await admin_faq.register_handlers(bot)
    await admin_payments.register_handlers(bot)
    
    logger.info("Admin handlers registered successfully") 