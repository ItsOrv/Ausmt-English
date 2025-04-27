from telethon import events, Button
from handlers.admin_utils import admin_state, db, logger, admin_required, edit_or_respond, clear_admin_state
from utils.keyboards import KeyboardManager

async def manage_teachers_handler(event):
    """Handle manage teachers request."""
    if not await admin_required(event):
        return
    
    logger.info(f"Admin {event.sender_id} accessing teacher management")
    
    # Get all teachers from database
    teachers = db.get_all_teachers()
    
    admin_message = "👨‍🏫 مدیریت اساتید\n\n"
    if teachers:
        for teacher in teachers:
            teacher_id, name, term_id, bio = teacher
            admin_message += f"🔹 شناسه: {teacher_id}\n"
            admin_message += f"🔹 نام: {name}\n"
            admin_message += f"🔹 شناسه ترم: {term_id}\n"
            admin_message += f"🔹 بیوگرافی: {bio[:50]}...\n\n"
    else:
        admin_message += "هیچ استادی در پایگاه داده یافت نشد."
    
    # Add keyboard for teacher management options
    keyboard = [
        [Button.inline("➕ افزودن استاد", data="add_teacher")],
        [Button.inline("✏️ ویرایش استاد", data="edit_teacher")],
        [Button.inline("❌ حذف استاد", data="delete_teacher")],
        [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
    ]
    
    await edit_or_respond(event, admin_message, buttons=keyboard)

async def add_teacher_handler(event):
    """Handle add teacher request."""
    if not await admin_required(event):
        return
    
    logger.info(f"Admin {event.sender_id} accessing add teacher form")
    
    # Get all terms for selection
    terms = db.get_terms()
    
    if not terms:
        await event.edit("ابتدا باید ترم‌ها را تعریف کنید.", buttons=[
            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
        ])
        return
    
    # Store state
    admin_state[event.sender_id] = {
        'state': 'adding_teacher',
        'step': 'name'
    }
    
    await event.edit("""لطفا نام استاد را وارد کنید:

برای لغو عملیات، دستور /cancel را ارسال کنید.""")

async def edit_teacher_handler(event):
    """Handle edit teacher request."""
    if not await admin_required(event):
        return
    
    logger.info(f"Admin {event.sender_id} accessing edit teacher form")
    
    # Get all teachers
    teachers = db.get_all_teachers()
    
    if not teachers:
        await event.edit("هیچ استادی برای ویرایش وجود ندارد.", buttons=[
            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
        ])
        return
    
    # Create keyboard for teacher selection
    keyboard = []
    for teacher in teachers:
        teacher_id, name, _, _ = teacher
        keyboard.append([Button.inline(f"{name}", data=f"edit_teacher_{teacher_id}")])
    
    keyboard.append([Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")])
    
    await event.edit("لطفا استاد مورد نظر برای ویرایش را انتخاب کنید:", buttons=keyboard)

async def delete_teacher_handler(event):
    """Handle delete teacher request."""
    if not await admin_required(event):
        return
    
    logger.info(f"Admin {event.sender_id} accessing delete teacher form")
    
    # Get all teachers
    teachers = db.get_all_teachers()
    
    if not teachers:
        await event.edit("هیچ استادی برای حذف وجود ندارد.", buttons=[
            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
        ])
        return
    
    # Create keyboard for teacher selection
    keyboard = []
    for teacher in teachers:
        teacher_id, name, _, _ = teacher
        keyboard.append([Button.inline(f"{name}", data=f"confirm_delete_teacher_{teacher_id}")])
    
    keyboard.append([Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")])
    
    await event.edit("لطفا استاد مورد نظر برای حذف را انتخاب کنید:", buttons=keyboard)

async def add_teacher_term_handler(event):
    """Handle term selection when adding a teacher."""
    if not await admin_required(event):
        return
    
    sender_id = event.sender_id
    
    # Check if admin is in the correct state
    if sender_id not in admin_state or admin_state[sender_id].get('state') != 'adding_teacher':
        await event.answer("وضعیت شما معتبر نیست. لطفا مجددا تلاش کنید.", alert=True)
        return
    
    # Extract term ID from callback data
    term_id = int(event.data.decode().split('_')[-1])
    
    # Store term ID in state
    admin_state[sender_id]['term_id'] = term_id
    admin_state[sender_id]['step'] = 'bio'
    
    # Get term name for confirmation
    term_name = "نامشخص"
    terms = db.get_terms()
    for term in terms:
        if term[0] == term_id:
            term_name = term[1]
            break
    
    # Ensure the admin state has the required data
    if 'name' not in admin_state[sender_id]:
        logger.error(f"Missing 'name' in admin_state for {sender_id}")
        await event.edit("خطا در فرآیند افزودن استاد. لطفا مجددا تلاش کنید.", buttons=[
            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
        ])
        return
    
    teacher_name = admin_state[sender_id]['name']
    
    await event.edit(f"نام استاد: {teacher_name}\nترم انتخاب شده: {term_name}\n\nلطفا بیوگرافی استاد را وارد کنید:")

async def edit_teacher_term_handler(event):
    """Handle term selection when editing a teacher."""
    if not await admin_required(event):
        return
    
    sender_id = event.sender_id
    
    # Check if admin is in the correct state
    if sender_id not in admin_state or admin_state[sender_id].get('state') != 'editing_teacher':
        await event.answer("وضعیت شما معتبر نیست. لطفا مجددا تلاش کنید.", alert=True)
        return
    
    # Extract term ID from callback data
    term_id = int(event.data.decode().split('_')[-1])
    
    # Store term ID in state
    admin_state[sender_id]['term_id'] = term_id
    admin_state[sender_id]['step'] = 'bio'
    
    # Get term name for confirmation
    term_name = "نامشخص"
    terms = db.get_terms()
    for term in terms:
        if term[0] == term_id:
            term_name = term[1]
            break
    
    # Ensure the admin state has the required data
    if 'name' not in admin_state[sender_id] or 'teacher_id' not in admin_state[sender_id]:
        logger.error(f"Missing data in admin_state for {sender_id}")
        await event.edit("خطا در فرآیند ویرایش استاد. لطفا مجددا تلاش کنید.", buttons=[
            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
        ])
        return
    
    teacher_name = admin_state[sender_id]['name']
    teacher_id = admin_state[sender_id]['teacher_id']
    
    await event.edit(f"شناسه استاد: {teacher_id}\nنام جدید: {teacher_name}\nترم جدید: {term_name}\n\nلطفا بیوگرافی جدید استاد را وارد کنید:")

async def edit_teacher_id_handler(event):
    """Handle teacher selection for editing."""
    if not await admin_required(event):
        return
    
    # Extract teacher ID from callback data
    teacher_id = int(event.data.decode().split('_')[-1])
    
    # Get teacher data
    teacher = None
    teachers = db.get_all_teachers()
    for t in teachers:
        if t[0] == teacher_id:
            teacher = t
            break
    
    if not teacher:
        await event.edit("استاد مورد نظر یافت نشد.", buttons=[
            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
        ])
        return
    
    # Initialize edit state
    admin_state[event.sender_id] = {
        'state': 'editing_teacher',
        'step': 'name',
        'teacher_id': teacher_id,
        'current_name': teacher[1],
        'current_term_id': teacher[2],
        'current_bio': teacher[3]
    }
    
    await event.edit(f"ویرایش استاد با شناسه {teacher_id}\n\nنام فعلی: {teacher[1]}\n\nلطفا نام جدید استاد را وارد کنید (برای حفظ نام فعلی، همان را وارد کنید):")

async def confirm_delete_teacher_handler(event):
    """Handle confirmation for deleting a teacher."""
    if not await admin_required(event):
        return
    
    # Extract teacher ID from callback data
    teacher_id = int(event.data.decode().split('_')[-1])
    
    # Get teacher data
    teacher = None
    teachers = db.get_all_teachers()
    for t in teachers:
        if t[0] == teacher_id:
            teacher = t
            break
    
    if not teacher:
        await event.edit("استاد مورد نظر یافت نشد.", buttons=[
            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
        ])
        return
    
    await event.edit(f"آیا از حذف استاد «{teacher[1]}» اطمینان دارید؟", buttons=[
        [Button.inline("✅ بله، حذف شود", data=f"delete_teacher_confirmed_{teacher_id}")],
        [Button.inline("❌ خیر، لغو شود", data="back_to_admin_menu")]
    ])

async def delete_teacher_confirmed_handler(event):
    """Handle confirmed teacher deletion."""
    if not await admin_required(event):
        return
    
    # Extract teacher ID from callback data
    teacher_id = int(event.data.decode().split('_')[-1])
    
    try:
        # Delete teacher from database
        success = db.delete_teacher(teacher_id)
        
        if success:
            await event.edit("استاد با موفقیت حذف شد.", buttons=[
                [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
            ])
        else:
            await event.edit("خطا در حذف استاد. ممکن است این استاد در دوره‌هایی استفاده شده باشد.", buttons=[
                [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
            ])
        
    except Exception as e:
        logger.error(f"Error deleting teacher: {e}")
        await event.edit("خطا در حذف استاد. ممکن است این استاد در دوره‌هایی استفاده شده باشد.", buttons=[
            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
        ])

async def process_teacher_message(event):
    """Process messages from admin related to teacher management."""
    sender = await event.get_sender()
    sender_id = sender.id
    
    # Check if admin is adding a teacher
    if sender_id in admin_state and admin_state[sender_id].get('state') == 'adding_teacher':
        current_step = admin_state[sender_id].get('step')
        
        if current_step == 'name':
            # Store teacher name
            teacher_name = event.text
            admin_state[sender_id]['name'] = teacher_name
            admin_state[sender_id]['step'] = 'term'
            
            # Get terms for selection
            terms = db.get_terms()
            
            # Create keyboard for term selection
            keyboard = []
            for term in terms:
                term_id, term_name, _ = term
                keyboard.append([Button.inline(f"{term_name}", data=f"add_teacher_term_{term_id}")])
            
            keyboard.append([Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")])
            
            await event.respond(f"نام استاد ثبت شد: {teacher_name}\n\nلطفا ترم مربوطه را انتخاب کنید:", buttons=keyboard)
            return True
        
        elif current_step == 'bio':
            try:
                # Store teacher bio
                teacher_bio = event.text
                
                # Verify that required data exists in admin_state
                if 'name' not in admin_state[sender_id] or 'term_id' not in admin_state[sender_id]:
                    logger.error(f"Missing required data in admin_state for {sender_id}: {admin_state[sender_id]}")
                    await event.respond("خطا در فرآیند افزودن استاد. لطفا مجددا تلاش کنید.", buttons=[
                        [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                    ])
                    clear_admin_state(sender_id)
                    return True
                    
                admin_state[sender_id]['bio'] = teacher_bio
                
                # Get stored data
                name = admin_state[sender_id]['name']
                term_id = admin_state[sender_id]['term_id']
                
                # Add teacher to database
                try:
                    teacher_id = db.add_teacher(name, term_id, teacher_bio)
                    
                    # Success message
                    await event.respond(f"استاد جدید با موفقیت اضافه شد!\n\nشناسه: {teacher_id}\nنام: {name}\nبیوگرافی: {teacher_bio}", buttons=[
                        [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                    ])
                    
                    # Clear state
                    clear_admin_state(sender_id)
                    
                except Exception as e:
                    logger.error(f"Error adding teacher: {e}")
                    await event.respond("خطا در ثبت استاد. لطفا مجددا تلاش کنید.", buttons=[
                        [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                    ])
                return True
            except Exception as e:
                logger.error(f"Error in bio step: {e}")
                await event.respond("خطا در پردازش بیوگرافی استاد. لطفا مجددا تلاش کنید.", buttons=[
                    [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                ])
                clear_admin_state(sender_id)
                return True
    
    # Check if admin is editing a teacher
    elif sender_id in admin_state and admin_state[sender_id].get('state') == 'editing_teacher':
        current_step = admin_state[sender_id].get('step')
        
        if current_step == 'name':
            # Store teacher name
            teacher_name = event.text
            admin_state[sender_id]['name'] = teacher_name
            admin_state[sender_id]['step'] = 'term'
            
            # Get terms for selection
            terms = db.get_terms()
            
            # Create keyboard for term selection
            keyboard = []
            for term in terms:
                term_id, term_name, _ = term
                keyboard.append([Button.inline(f"{term_name}", data=f"edit_teacher_term_{term_id}")])
            
            keyboard.append([Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")])
            
            await event.respond(f"نام استاد جدید: {teacher_name}\n\nلطفا ترم جدید را انتخاب کنید:", buttons=keyboard)
            return True
        
        elif current_step == 'bio':
            try:
                # Store teacher bio
                teacher_bio = event.text
                
                # Verify that required data exists in admin_state
                if 'name' not in admin_state[sender_id] or 'term_id' not in admin_state[sender_id] or 'teacher_id' not in admin_state[sender_id]:
                    logger.error(f"Missing required data in admin_state for {sender_id}: {admin_state[sender_id]}")
                    await event.respond("خطا در فرآیند ویرایش استاد. لطفا مجددا تلاش کنید.", buttons=[
                        [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                    ])
                    clear_admin_state(sender_id)
                    return True
                
                # Get stored data
                name = admin_state[sender_id]['name']
                term_id = admin_state[sender_id]['term_id']
                teacher_id = admin_state[sender_id]['teacher_id']
                
                # Update teacher in database
                try:
                    success = db.update_teacher(teacher_id, name, term_id, teacher_bio)
                    
                    if success:
                        # Success message
                        await event.respond(f"استاد با موفقیت بروزرسانی شد!\n\nشناسه: {teacher_id}\nنام جدید: {name}\nبیوگرافی جدید: {teacher_bio}", buttons=[
                            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                        ])
                    else:
                        await event.respond("استاد مورد نظر یافت نشد یا خطایی در بروزرسانی رخ داد.", buttons=[
                            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                        ])
                    
                    # Clear state
                    clear_admin_state(sender_id)
                    
                except Exception as e:
                    logger.error(f"Error updating teacher: {e}")
                    await event.respond("خطا در بروزرسانی استاد. لطفا مجددا تلاش کنید.", buttons=[
                        [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                    ])
                return True
            except Exception as e:
                logger.error(f"Error in bio edit step: {e}")
                await event.respond("خطا در پردازش بیوگرافی استاد. لطفا مجددا تلاش کنید.", buttons=[
                    [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                ])
                clear_admin_state(sender_id)
                return True
    
    return False

async def register_handlers(bot):
    """Register teacher management handlers."""
    bot.add_event_handler(manage_teachers_handler, events.CallbackQuery(pattern=r'admin_manage_teachers'))
    bot.add_event_handler(add_teacher_handler, events.CallbackQuery(pattern=r'add_teacher'))
    bot.add_event_handler(edit_teacher_handler, events.CallbackQuery(pattern=r'edit_teacher'))
    bot.add_event_handler(delete_teacher_handler, events.CallbackQuery(pattern=r'delete_teacher'))
    bot.add_event_handler(add_teacher_term_handler, events.CallbackQuery(pattern=r'add_teacher_term_\d+'))
    bot.add_event_handler(edit_teacher_term_handler, events.CallbackQuery(pattern=r'edit_teacher_term_\d+'))
    bot.add_event_handler(edit_teacher_id_handler, events.CallbackQuery(pattern=r'edit_teacher_\d+'))
    bot.add_event_handler(confirm_delete_teacher_handler, events.CallbackQuery(pattern=r'confirm_delete_teacher_\d+'))
    bot.add_event_handler(delete_teacher_confirmed_handler, events.CallbackQuery(pattern=r'delete_teacher_confirmed_\d+'))
    
    logger.info("Admin teacher handlers registered successfully") 