from telethon import events, Button
from handlers.admin_utils import admin_state, db, logger, admin_required, edit_or_respond, clear_admin_state
from utils.keyboards import KeyboardManager

async def manage_courses_handler(event):
    """Handle manage courses request."""
    if not await admin_required(event):
        return
    
    logger.info(f"Admin {event.sender_id} accessing course management")
    
    # Get all courses from database
    courses = db.get_all_courses()
    
    admin_message = "📚 مدیریت دوره‌ها\n\n"
    if courses:
        for course in courses:
            course_id, term_id, teacher_id, day, time, location, topics, price = course
            admin_message += f"🔹 شناسه: {course_id}\n"
            admin_message += f"🔹 شناسه ترم: {term_id}\n"
            admin_message += f"🔹 شناسه استاد: {teacher_id}\n"
            admin_message += f"🔹 برنامه: {day} ساعت {time}\n"
            admin_message += f"🔹 قیمت: {price:,} تومان\n\n"
    else:
        admin_message += "هیچ دوره‌ای در پایگاه داده یافت نشد."
    
    # Add keyboard for course management options
    keyboard = [
        [Button.inline("➕ افزودن دوره", data="add_course")],
        [Button.inline("✏️ ویرایش دوره", data="edit_course")],
        [Button.inline("❌ حذف دوره", data="delete_course")],
        [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
    ]
    
    await edit_or_respond(event, admin_message, buttons=keyboard)

async def add_course_handler(event):
    """Handle add course request."""
    if not await admin_required(event):
        return
    
    logger.info(f"Admin {event.sender_id} accessing add course form")
    
    # Get all terms and teachers for selection
    terms = db.get_terms()
    teachers = db.get_all_teachers()
    
    if not terms:
        await event.edit("ابتدا باید ترم‌ها را تعریف کنید.", buttons=[
            [Button.inline("🔙 بازگشت به مدیریت دوره‌ها", data="admin_manage_courses")]
        ])
        return
    
    if not teachers:
        await event.edit("ابتدا باید استادی تعریف کنید.", buttons=[
            [Button.inline("🔙 بازگشت به مدیریت دوره‌ها", data="admin_manage_courses")]
        ])
        return
    
    # Store state
    admin_state[event.sender_id] = {
        'state': 'adding_course',
        'step': 'term'
    }
    
    # Create keyboard for term selection
    keyboard = []
    for term in terms:
        term_id, term_name, _ = term
        keyboard.append([Button.inline(f"{term_name}", data=f"add_course_term_{term_id}")])
    
    keyboard.append([Button.inline("🔙 بازگشت به مدیریت دوره‌ها", data="admin_manage_courses")])
    
    await event.edit("لطفا ترم مربوط به دوره را انتخاب کنید:", buttons=keyboard)

async def add_course_term_handler(event):
    """Handle term selection when adding a course."""
    if not await admin_required(event):
        return
    
    term_id = int(event.data.decode().split('_')[-1])
    
    # Store term ID in state
    admin_state[event.sender_id]['term_id'] = term_id
    admin_state[event.sender_id]['step'] = 'teacher'
    
    # Get term name for confirmation
    term_name = "نامشخص"
    terms = db.get_terms()
    for term in terms:
        if term[0] == term_id:
            term_name = term[1]
            break
    
    # Get teachers for selection
    teachers = db.get_all_teachers()
    
    # Create keyboard for teacher selection
    keyboard = []
    for teacher in teachers:
        teacher_id, teacher_name, _, _ = teacher
        keyboard.append([Button.inline(f"{teacher_name}", data=f"add_course_teacher_{teacher_id}")])
    
    keyboard.append([Button.inline("🔙 بازگشت به مدیریت دوره‌ها", data="admin_manage_courses")])
    
    await event.edit(f"ترم انتخاب شده: {term_name}\n\nلطفا استاد دوره را انتخاب کنید:", buttons=keyboard)

async def add_course_teacher_handler(event):
    """Handle teacher selection when adding a course."""
    if not await admin_required(event):
        return
    
    teacher_id = int(event.data.decode().split('_')[-1])
    
    # Store teacher ID in state
    admin_state[event.sender_id]['teacher_id'] = teacher_id
    admin_state[event.sender_id]['step'] = 'day'
    
    # Get teacher name for confirmation
    teacher_name = "نامشخص"
    teachers = db.get_all_teachers()
    for teacher in teachers:
        if teacher[0] == teacher_id:
            teacher_name = teacher[1]
            break
    
    await event.edit(f"استاد انتخاب شده: {teacher_name}\n\nلطفا روز برگزاری دوره را وارد کنید (مثال: شنبه، یکشنبه، ...):")

async def edit_course_handler(event):
    """Handle edit course request."""
    if not await admin_required(event):
        return
    
    logger.info(f"Admin {event.sender_id} accessing edit course form")
    
    # Get all courses
    courses = db.get_all_courses()
    
    if not courses:
        await event.edit("هیچ دوره‌ای برای ویرایش وجود ندارد.", buttons=[
            [Button.inline("🔙 بازگشت به مدیریت دوره‌ها", data="admin_manage_courses")]
        ])
        return
    
    # Create keyboard for course selection
    keyboard = []
    for course in courses:
        course_id, term_id, teacher_id, day, time, _, _, _ = course
        
        # Get term and teacher names
        term_name = "نامشخص"
        terms = db.get_terms()
        for term in terms:
            if term[0] == term_id:
                term_name = term[1]
                break
        
        teacher_name = "نامشخص"
        teachers = db.get_all_teachers()
        for teacher in teachers:
            if teacher[0] == teacher_id:
                teacher_name = teacher[1]
                break
        
        keyboard.append([Button.inline(f"{term_name} با {teacher_name} روز {day}", data=f"edit_course_{course_id}")])
    
    keyboard.append([Button.inline("🔙 بازگشت به مدیریت دوره‌ها", data="admin_manage_courses")])
    
    await event.edit("لطفا دوره مورد نظر برای ویرایش را انتخاب کنید:", buttons=keyboard)

async def delete_course_handler(event):
    """Handle delete course request."""
    if not await admin_required(event):
        return
    
    logger.info(f"Admin {event.sender_id} accessing delete course form")
    
    # Get all courses
    courses = db.get_all_courses()
    
    if not courses:
        await event.edit("هیچ دوره‌ای برای حذف وجود ندارد.", buttons=[
            [Button.inline("🔙 بازگشت به مدیریت دوره‌ها", data="admin_manage_courses")]
        ])
        return
    
    # Create keyboard for course selection
    keyboard = []
    for course in courses:
        course_id, term_id, teacher_id, day, time, _, _, _ = course
        
        # Get term and teacher names
        term_name = "نامشخص"
        terms = db.get_terms()
        for term in terms:
            if term[0] == term_id:
                term_name = term[1]
                break
        
        teacher_name = "نامشخص"
        teachers = db.get_all_teachers()
        for teacher in teachers:
            if teacher[0] == teacher_id:
                teacher_name = teacher[1]
                break
        
        keyboard.append([Button.inline(f"{term_name} با {teacher_name} روز {day}", data=f"confirm_delete_course_{course_id}")])
    
    keyboard.append([Button.inline("🔙 بازگشت به مدیریت دوره‌ها", data="admin_manage_courses")])
    
    await event.edit("لطفا دوره مورد نظر برای حذف را انتخاب کنید:", buttons=keyboard)

async def edit_course_id_handler(event):
    """Handle course selection for editing."""
    if not await admin_required(event):
        return
    
    # Extract course ID from callback data
    course_id = int(event.data.decode().split('_')[-1])
    
    # Get course data
    course = None
    courses = db.get_all_courses()
    for c in courses:
        if c[0] == course_id:
            course = c
            break
    
    if not course:
        await event.edit("دوره مورد نظر یافت نشد.", buttons=[
            [Button.inline("🔙 بازگشت به مدیریت دوره‌ها", data="admin_manage_courses")]
        ])
        return
    
    # Get term and teacher names
    term_name = "نامشخص"
    terms = db.get_terms()
    for term in terms:
        if term[0] == course[1]:
            term_name = term[1]
            break
    
    teacher_name = "نامشخص"
    teachers = db.get_all_teachers()
    for teacher in teachers:
        if teacher[0] == course[2]:
            teacher_name = teacher[1]
            break
    
    # Initialize edit state
    admin_state[event.sender_id] = {
        'state': 'editing_course',
        'step': 'term',
        'course_id': course_id,
        'current_term_id': course[1],
        'current_teacher_id': course[2],
        'current_day': course[3],
        'current_time': course[4],
        'current_location': course[5],
        'current_topics': course[6],
        'current_price': course[7]
    }
    
    # Get terms for selection
    terms = db.get_terms()
    
    # Create keyboard for term selection
    keyboard = []
    for term in terms:
        term_id, term_name, _ = term
        keyboard.append([Button.inline(f"{term_name}", data=f"edit_course_term_{term_id}")])
    
    keyboard.append([Button.inline("🔙 بازگشت به مدیریت دوره‌ها", data="admin_manage_courses")])
    
    await event.edit(f"ویرایش دوره با شناسه {course_id}\n\nترم فعلی: {term_name}\nاستاد فعلی: {teacher_name}\nروز: {course[3]}\nساعت: {course[4]}\nمکان: {course[5]}\nمباحث: {course[6]}\nقیمت: {course[7]:,} تومان\n\nلطفا ترم جدید را انتخاب کنید:", buttons=keyboard)

async def edit_course_term_handler(event):
    """Handle term selection when editing a course."""
    if not await admin_required(event):
        return
    
    term_id = int(event.data.decode().split('_')[-1])
    
    # Store term ID in state
    admin_state[event.sender_id]['term_id'] = term_id
    admin_state[event.sender_id]['step'] = 'teacher'
    
    # Get teachers for selection
    teachers = db.get_all_teachers()
    
    # Create keyboard for teacher selection
    keyboard = []
    for teacher in teachers:
        teacher_id, teacher_name, _, _ = teacher
        keyboard.append([Button.inline(f"{teacher_name}", data=f"edit_course_teacher_{teacher_id}")])
    
    keyboard.append([Button.inline("🔙 بازگشت به مدیریت دوره‌ها", data="admin_manage_courses")])
    
    await event.edit("لطفا استاد جدید دوره را انتخاب کنید:", buttons=keyboard)

async def edit_course_teacher_handler(event):
    """Handle teacher selection when editing a course."""
    if not await admin_required(event):
        return
    
    teacher_id = int(event.data.decode().split('_')[-1])
    
    # Store teacher ID in state
    admin_state[event.sender_id]['teacher_id'] = teacher_id
    admin_state[event.sender_id]['step'] = 'day'
    
    await event.edit("لطفا روز جدید برگزاری دوره را وارد کنید (مثال: شنبه، یکشنبه، ...):")

async def confirm_delete_course_handler(event):
    """Handle confirmation for deleting a course."""
    if not await admin_required(event):
        return
    
    # Extract course ID from callback data
    course_id = int(event.data.decode().split('_')[-1])
    
    # Get course data
    course = None
    courses = db.get_all_courses()
    for c in courses:
        if c[0] == course_id:
            course = c
            break
    
    if not course:
        await event.edit("دوره مورد نظر یافت نشد.", buttons=[
            [Button.inline("🔙 بازگشت به مدیریت دوره‌ها", data="admin_manage_courses")]
        ])
        return
    
    # Get term and teacher names
    term_name = "نامشخص"
    terms = db.get_terms()
    for term in terms:
        if term[0] == course[1]:
            term_name = term[1]
            break
    
    teacher_name = "نامشخص"
    teachers = db.get_all_teachers()
    for teacher in teachers:
        if teacher[0] == course[2]:
            teacher_name = teacher[1]
            break
    
    await event.edit(f"آیا از حذف دوره «{term_name} با {teacher_name} روز {course[3]}» اطمینان دارید؟", buttons=[
        [Button.inline("✅ بله، حذف شود", data=f"delete_course_confirmed_{course_id}")],
        [Button.inline("❌ خیر، لغو شود", data="admin_manage_courses")]
    ])

async def delete_course_confirmed_handler(event):
    """Handle confirmed course deletion."""
    if not await admin_required(event):
        return
    
    # Extract course ID from callback data
    course_id = int(event.data.decode().split('_')[-1])
    
    try:
        # Delete course from database
        success = db.delete_course(course_id)
        
        if success:
            await event.edit("دوره با موفقیت حذف شد.", buttons=[
                [Button.inline("🔙 بازگشت به مدیریت دوره‌ها", data="admin_manage_courses")]
            ])
        else:
            await event.edit("خطا در حذف دوره. ممکن است این دوره در ثبت‌نام‌هایی استفاده شده باشد.", buttons=[
                [Button.inline("🔙 بازگشت به مدیریت دوره‌ها", data="admin_manage_courses")]
            ])
        
    except Exception as e:
        logger.error(f"Error deleting course: {e}")
        await event.edit("خطا در حذف دوره. ممکن است این دوره در ثبت‌نام‌هایی استفاده شده باشد.", buttons=[
            [Button.inline("🔙 بازگشت به مدیریت دوره‌ها", data="admin_manage_courses")]
        ])

async def process_course_message(event):
    """Process messages from admin related to course management."""
    sender = await event.get_sender()
    sender_id = sender.id
    
    # Check if admin is adding a course
    if sender_id in admin_state and admin_state[sender_id].get('state') == 'adding_course':
        current_step = admin_state[sender_id].get('step')
        
        if current_step == 'day':
            # Store course day
            course_day = event.text
            admin_state[sender_id]['day'] = course_day
            admin_state[sender_id]['step'] = 'time'
            
            await event.respond(f"روز برگزاری: {course_day}\n\nلطفا ساعت برگزاری دوره را وارد کنید (مثال: 16:00):")
            return True
        
        elif current_step == 'time':
            # Store course time
            course_time = event.text
            admin_state[sender_id]['time'] = course_time
            admin_state[sender_id]['step'] = 'location'
            
            await event.respond(f"ساعت برگزاری: {course_time}\n\nلطفا مکان برگزاری دوره را وارد کنید:")
            return True
        
        elif current_step == 'location':
            # Store course location
            course_location = event.text
            admin_state[sender_id]['location'] = course_location
            admin_state[sender_id]['step'] = 'topics'
            
            await event.respond(f"مکان برگزاری: {course_location}\n\nلطفا مباحث دوره را وارد کنید:")
            return True
        
        elif current_step == 'topics':
            # Store course topics
            course_topics = event.text
            admin_state[sender_id]['topics'] = course_topics
            admin_state[sender_id]['step'] = 'price'
            
            await event.respond(f"مباحث دوره: {course_topics}\n\nلطفا قیمت دوره را به تومان وارد کنید (فقط عدد):")
            return True
        
        elif current_step == 'price':
            # Store course price
            try:
                course_price = int(event.text.replace(',', ''))
                
                # Get stored data
                term_id = admin_state[sender_id]['term_id']
                teacher_id = admin_state[sender_id]['teacher_id']
                day = admin_state[sender_id]['day']
                time = admin_state[sender_id]['time']
                location = admin_state[sender_id]['location']
                topics = admin_state[sender_id]['topics']
                
                # Add course to database
                try:
                    course_id = db.add_course(term_id, teacher_id, day, time, location, topics, course_price)
                    
                    # Success message
                    await event.respond(f"دوره جدید با موفقیت اضافه شد!\n\nشناسه: {course_id}\nروز: {day}\nساعت: {time}\nمکان: {location}\nمباحث: {topics}\nقیمت: {course_price:,} تومان", buttons=[
                        [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                    ])
                    
                    # Clear state
                    clear_admin_state(sender_id)
                    
                except Exception as e:
                    logger.error(f"Error adding course: {e}")
                    await event.respond("خطا در ثبت دوره. لطفا مجددا تلاش کنید.", buttons=[
                        [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                    ])
            except ValueError:
                await event.respond("لطفا قیمت را به صورت عدد صحیح وارد کنید (مثال: 1500000):")
            return True
    
    # Check if admin is editing a course
    elif sender_id in admin_state and admin_state[sender_id].get('state') == 'editing_course':
        current_step = admin_state[sender_id].get('step')
        
        if current_step == 'day':
            # Store course day
            course_day = event.text
            admin_state[sender_id]['day'] = course_day
            admin_state[sender_id]['step'] = 'time'
            
            await event.respond(f"روز برگزاری جدید: {course_day}\n\nلطفا ساعت برگزاری جدید دوره را وارد کنید (مثال: 16:00):")
            return True
        
        elif current_step == 'time':
            # Store course time
            course_time = event.text
            admin_state[sender_id]['time'] = course_time
            admin_state[sender_id]['step'] = 'location'
            
            await event.respond(f"ساعت برگزاری جدید: {course_time}\n\nلطفا مکان برگزاری جدید دوره را وارد کنید:")
            return True
        
        elif current_step == 'location':
            # Store course location
            course_location = event.text
            admin_state[sender_id]['location'] = course_location
            admin_state[sender_id]['step'] = 'topics'
            
            await event.respond(f"مکان برگزاری جدید: {course_location}\n\nلطفا مباحث جدید دوره را وارد کنید:")
            return True
        
        elif current_step == 'topics':
            # Store course topics
            course_topics = event.text
            admin_state[sender_id]['topics'] = course_topics
            admin_state[sender_id]['step'] = 'price'
            
            await event.respond(f"مباحث جدید دوره: {course_topics}\n\nلطفا قیمت جدید دوره را به تومان وارد کنید (فقط عدد):")
            return True
        
        elif current_step == 'price':
            # Store course price
            try:
                course_price = int(event.text.replace(',', ''))
                
                # Get stored data
                course_id = admin_state[sender_id]['course_id']
                term_id = admin_state[sender_id]['term_id']
                teacher_id = admin_state[sender_id]['teacher_id']
                day = admin_state[sender_id]['day']
                time = admin_state[sender_id]['time']
                location = admin_state[sender_id]['location']
                topics = admin_state[sender_id]['topics']
                
                # Update course in database
                try:
                    success = db.update_course(course_id, term_id, teacher_id, day, time, location, topics, course_price)
                    
                    if success:
                        # Success message
                        await event.respond(f"دوره با موفقیت بروزرسانی شد!\n\nشناسه: {course_id}\nروز جدید: {day}\nساعت جدید: {time}\nمکان جدید: {location}\nمباحث جدید: {topics}\nقیمت جدید: {course_price:,} تومان", buttons=[
                            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                        ])
                    else:
                        await event.respond("دوره مورد نظر یافت نشد یا خطایی در بروزرسانی رخ داد.", buttons=[
                            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                        ])
                    
                    # Clear state
                    clear_admin_state(sender_id)
                    
                except Exception as e:
                    logger.error(f"Error updating course: {e}")
                    await event.respond("خطا در بروزرسانی دوره. لطفا مجددا تلاش کنید.", buttons=[
                        [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                    ])
            except ValueError:
                await event.respond("لطفا قیمت را به صورت عدد صحیح وارد کنید (مثال: 1500000):")
            return True
    
    return False

async def register_handlers(bot):
    """Register course management handlers."""
    bot.add_event_handler(manage_courses_handler, events.CallbackQuery(pattern=r'admin_manage_courses'))
    bot.add_event_handler(add_course_handler, events.CallbackQuery(pattern=r'add_course'))
    bot.add_event_handler(edit_course_handler, events.CallbackQuery(pattern=r'edit_course'))
    bot.add_event_handler(delete_course_handler, events.CallbackQuery(pattern=r'delete_course'))
    bot.add_event_handler(add_course_term_handler, events.CallbackQuery(pattern=r'add_course_term_\d+'))
    bot.add_event_handler(add_course_teacher_handler, events.CallbackQuery(pattern=r'add_course_teacher_\d+'))
    bot.add_event_handler(edit_course_id_handler, events.CallbackQuery(pattern=r'edit_course_\d+'))
    bot.add_event_handler(edit_course_term_handler, events.CallbackQuery(pattern=r'edit_course_term_\d+'))
    bot.add_event_handler(edit_course_teacher_handler, events.CallbackQuery(pattern=r'edit_course_teacher_\d+'))
    bot.add_event_handler(confirm_delete_course_handler, events.CallbackQuery(pattern=r'confirm_delete_course_\d+'))
    bot.add_event_handler(delete_course_confirmed_handler, events.CallbackQuery(pattern=r'delete_course_confirmed_\d+'))
    
    logger.info("Admin course handlers registered successfully") 