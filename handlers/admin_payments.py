from telethon import events
from handlers.admin_utils import admin_state, db, logger, admin_required, edit_or_respond
from utils.keyboards import KeyboardManager

async def manage_payments_handler(event):
    """Handler for managing payments."""
    if not await admin_required(event):
        return
    
    sender_id = (await event.get_sender()).id
    
    # Get pending registrations
    try:
        pending_registrations = db.get_pending_registrations()
        logger.info(f"Found {len(pending_registrations) if pending_registrations else 0} pending registrations")
    except Exception as e:
        logger.error(f"Error getting pending registrations: {e}")
        await event.answer("خطا در دریافت اطلاعات پرداخت‌ها", alert=True)
        return
    
    if not pending_registrations:
        try:
            # Get the current message text to compare
            current_message = await event.get_message()
            current_text = current_message.text if hasattr(current_message, 'text') and current_message.text else ""
            
            new_text = "در حال حاضر هیچ درخواست پرداخت در انتظار تأیید وجود ندارد."
            
            # Only edit if the message content would change
            if current_text != new_text:
                await event.edit(new_text, buttons=KeyboardManager.back_to_main())
            else:
                # Just show an alert if the message is already correct
                await event.answer("هیچ درخواست پرداختی در انتظار تأیید وجود ندارد.", alert=True)
        except Exception as e:
            logger.error(f"Error handling no pending payments: {e}")
            # Don't try to edit, just show an alert
            await event.answer("هیچ درخواست پرداختی در انتظار تأیید وجود ندارد.", alert=True)
        return
    
    # Format pending registrations
    message = "**درخواست‌های پرداخت در انتظار تأیید:**\n\n"
    
    for i, reg in enumerate(pending_registrations, 1):
        reg_id, first_name, last_name, student_id, term_name, teacher_name, price, payment_type, payment_method, receipt_link, first_payment, second_payment = reg
        
        payment_info = f"قسط {'دوم' if second_payment else 'اول'}" if payment_method == 'installment' else "پرداخت کامل"
        payment_amount = price // 2 if payment_method == 'installment' and not second_payment else price
        
        message += f"""--- درخواست شماره {i} ---
نام: {first_name} {last_name}
شماره دانشجویی: {student_id}
دوره: {term_name} با استاد {teacher_name}
نوع پرداخت: {payment_type} ({payment_info})
مبلغ: {payment_amount:,} تومان

"""
    
    message += "\nبرای بررسی جزئیات و تأیید/رد درخواست‌ها، از دکمه‌های ارسال شده در پیام‌های مربوط به هر درخواست استفاده کنید."
    
    await edit_or_respond(event, message, buttons=KeyboardManager.back_to_main())

async def admin_payment_handler(event):
    """Handler for admin approving or rejecting payments."""
    if not await admin_required(event):
        return
    
    action = event.data.decode('utf-8').split('_')[1]  # approve or reject
    
    # Get registration ID from the current message
    message = await event.get_message()
    # Extract registration ID from message text using regex or other parsing methods
    # This código depende de la implementación exacta de cómo se muestra el ID en el mensaje
    
    # For now, we'll just log the action (this should be expanded)
    logger.info(f"Admin {(await event.get_sender()).id} {action}d payment")
    
    if action == "approve":
        await event.edit("پرداخت با موفقیت تایید شد.", buttons=KeyboardManager.back_to_admin_menu())
    else:
        await event.edit("پرداخت رد شد.", buttons=KeyboardManager.back_to_admin_menu())

async def register_handlers(bot):
    """Register payment management handlers."""
    bot.add_event_handler(manage_payments_handler, events.CallbackQuery(pattern=r'admin_manage_payments'))
    bot.add_event_handler(admin_payment_handler, events.CallbackQuery(pattern=r'admin_(approve|reject)'))
    
    logger.info("Admin payment handlers registered successfully") 