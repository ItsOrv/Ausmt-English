from telethon import events, Button
from handlers.admin_utils import admin_state, db, logger, admin_required, edit_or_respond, clear_admin_state
from utils.keyboards import KeyboardManager

async def manage_terms_handler(event):
    """Handle manage terms request."""
    if not await admin_required(event):
        return
    
    logger.info(f"Admin {event.sender_id} accessing term management")
    
    # Get all terms from database
    terms = db.get_terms()
    
    admin_message = "🗓️ مدیریت ترم‌ها\n\n"
    if terms:
        for term in terms:
            term_id, name, description = term
            admin_message += f"🔹 شناسه: {term_id}\n"
            admin_message += f"🔹 نام: {name}\n"
            admin_message += f"🔹 توضیحات: {description}\n\n"
    else:
        admin_message += "هیچ ترمی در پایگاه داده یافت نشد."
    
    # Add keyboard for term management options
    keyboard = [
        [Button.inline("➕ افزودن ترم", data="add_term")],
        [Button.inline("✏️ ویرایش ترم", data="edit_term")],
        [Button.inline("❌ حذف ترم", data="delete_term")],
        [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
    ]
    
    await edit_or_respond(event, admin_message, buttons=keyboard)

async def add_term_handler(event):
    """Handle add term request."""
    if not await admin_required(event):
        return
    
    logger.info(f"Admin {event.sender_id} accessing add term form")
    
    # Store state
    admin_state[event.sender_id] = {
        'state': 'adding_term',
        'step': 'name'
    }
    
    await event.edit("""لطفا نام ترم را وارد کنید (مثلا: ترم بهار 1402):

برای لغو عملیات، دستور /cancel را ارسال کنید.""")

async def edit_term_handler(event):
    """Handle edit term request."""
    if not await admin_required(event):
        return
    
    logger.info(f"Admin {event.sender_id} accessing edit term form")
    
    # Get all terms
    terms = db.get_terms()
    
    if not terms:
        await event.edit("هیچ ترمی برای ویرایش وجود ندارد.", buttons=[
            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
        ])
        return
    
    # Create keyboard for term selection
    keyboard = []
    for term in terms:
        term_id, name, _ = term
        keyboard.append([Button.inline(f"{name}", data=f"edit_term_{term_id}")])
    
    keyboard.append([Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")])
    
    await event.edit("لطفا ترم مورد نظر برای ویرایش را انتخاب کنید:", buttons=keyboard)

async def delete_term_handler(event):
    """Handle delete term request."""
    if not await admin_required(event):
        return
    
    logger.info(f"Admin {event.sender_id} accessing delete term form")
    
    # Get all terms
    terms = db.get_terms()
    
    if not terms:
        await event.edit("هیچ ترمی برای حذف وجود ندارد.", buttons=[
            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
        ])
        return
    
    # Create keyboard for term selection
    keyboard = []
    for term in terms:
        term_id, name, _ = term
        keyboard.append([Button.inline(f"{name}", data=f"confirm_delete_term_{term_id}")])
    
    keyboard.append([Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")])
    
    await event.edit("لطفا ترم مورد نظر برای حذف را انتخاب کنید:", buttons=keyboard)

async def edit_term_id_handler(event):
    """Handle term selection for editing."""
    if not await admin_required(event):
        return
    
    # Extract term ID from callback data
    term_id = int(event.data.decode().split('_')[-1])
    
    # Get term data
    term = None
    terms = db.get_terms()
    for t in terms:
        if t[0] == term_id:
            term = t
            break
    
    if not term:
        await event.edit("ترم مورد نظر یافت نشد.", buttons=[
            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
        ])
        return
    
    # Initialize edit state
    admin_state[event.sender_id] = {
        'state': 'editing_term',
        'step': 'name',
        'term_id': term_id,
        'current_name': term[1],
        'current_description': term[2]
    }
    
    await event.edit(f"ویرایش ترم با شناسه {term_id}\n\nنام فعلی: {term[1]}\n\nلطفا نام جدید ترم را وارد کنید (برای حفظ نام فعلی، همان را وارد کنید):")

async def confirm_delete_term_handler(event):
    """Handle confirmation for deleting a term."""
    if not await admin_required(event):
        return
    
    # Extract term ID from callback data
    term_id = int(event.data.decode().split('_')[-1])
    
    # Get term data
    term = None
    terms = db.get_terms()
    for t in terms:
        if t[0] == term_id:
            term = t
            break
    
    if not term:
        await event.edit("ترم مورد نظر یافت نشد.", buttons=[
            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
        ])
        return
    
    await event.edit(f"آیا از حذف ترم «{term[1]}» اطمینان دارید؟", buttons=[
        [Button.inline("✅ بله، حذف شود", data=f"delete_term_confirmed_{term_id}")],
        [Button.inline("❌ خیر، لغو شود", data="back_to_admin_menu")]
    ])

async def delete_term_confirmed_handler(event):
    """Handle confirmed term deletion."""
    if not await admin_required(event):
        return
    
    # Extract term ID from callback data
    term_id = int(event.data.decode().split('_')[-1])
    
    try:
        # Delete term from database
        success = db.delete_term(term_id)
        
        if success:
            await event.edit("ترم با موفقیت حذف شد.", buttons=[
                [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
            ])
        else:
            await event.edit("خطا در حذف ترم. ممکن است این ترم در دوره‌ها یا اساتید استفاده شده باشد.", buttons=[
                [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
            ])
        
    except Exception as e:
        logger.error(f"Error deleting term: {e}")
        await event.edit("خطا در حذف ترم. ممکن است این ترم در دوره‌ها یا اساتید استفاده شده باشد.", buttons=[
            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
        ])

async def process_term_message(event):
    """Process messages from admin related to term management."""
    sender = await event.get_sender()
    sender_id = sender.id
    
    # Check if admin is adding a term
    if sender_id in admin_state and admin_state[sender_id].get('state') == 'adding_term':
        current_step = admin_state[sender_id].get('step')
        
        if current_step == 'name':
            # Store term name
            term_name = event.text
            admin_state[sender_id]['name'] = term_name
            admin_state[sender_id]['step'] = 'description'
            
            await event.respond(f"نام ترم ثبت شد: {term_name}\n\nلطفا توضیحات ترم را وارد کنید:")
            return True
        
        elif current_step == 'description':
            # Store term description
            term_description = event.text
            
            # Get stored data
            name = admin_state[sender_id]['name']
            
            # Add term to database
            try:
                term_id = db.add_term(name, term_description)
                
                # Success message
                await event.respond(f"ترم جدید با موفقیت اضافه شد!\n\nشناسه: {term_id}\nنام: {name}\nتوضیحات: {term_description}", buttons=[
                    [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                ])
                
                # Clear state
                clear_admin_state(sender_id)
                
            except Exception as e:
                logger.error(f"Error adding term: {e}")
                await event.respond("خطا در ثبت ترم. لطفا مجددا تلاش کنید.", buttons=[
                    [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                ])
            return True
    
    # Check if admin is editing a term
    elif sender_id in admin_state and admin_state[sender_id].get('state') == 'editing_term':
        current_step = admin_state[sender_id].get('step')
        term_id = admin_state[sender_id].get('term_id')
        
        if current_step == 'name':
            # Store term name
            term_name = event.text
            admin_state[sender_id]['name'] = term_name
            admin_state[sender_id]['step'] = 'description'
            
            await event.respond(f"نام ترم جدید: {term_name}\n\nلطفا توضیحات جدید ترم را وارد کنید:")
            return True
        
        elif current_step == 'description':
            # Store term description
            term_description = event.text
            
            # Get stored data
            name = admin_state[sender_id]['name']
            
            # Update term in database
            try:
                success = db.update_term(term_id, name, term_description)
                
                if success:
                    # Success message
                    await event.respond(f"ترم با موفقیت بروزرسانی شد!\n\nشناسه: {term_id}\nنام جدید: {name}\nتوضیحات جدید: {term_description}", buttons=[
                        [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                    ])
                else:
                    await event.respond("ترم مورد نظر یافت نشد یا خطایی در بروزرسانی رخ داد.", buttons=[
                        [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                    ])
                
                # Clear state
                clear_admin_state(sender_id)
                
            except Exception as e:
                logger.error(f"Error updating term: {e}")
                await event.respond("خطا در بروزرسانی ترم. لطفا مجددا تلاش کنید.", buttons=[
                    [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                ])
            return True
    
    return False

async def register_handlers(bot):
    """Register term management handlers."""
    bot.add_event_handler(manage_terms_handler, events.CallbackQuery(pattern=r'admin_manage_terms'))
    bot.add_event_handler(add_term_handler, events.CallbackQuery(pattern=r'add_term'))
    bot.add_event_handler(edit_term_handler, events.CallbackQuery(pattern=r'edit_term'))
    bot.add_event_handler(delete_term_handler, events.CallbackQuery(pattern=r'delete_term'))
    bot.add_event_handler(edit_term_id_handler, events.CallbackQuery(pattern=r'edit_term_\d+'))
    bot.add_event_handler(confirm_delete_term_handler, events.CallbackQuery(pattern=r'confirm_delete_term_\d+'))
    bot.add_event_handler(delete_term_confirmed_handler, events.CallbackQuery(pattern=r'delete_term_confirmed_\d+'))
    
    logger.info("Admin term handlers registered successfully") 