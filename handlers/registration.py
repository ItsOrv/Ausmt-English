from telethon import events
import logging
import re
import os
from datetime import datetime
from utils.keyboards import KeyboardManager
from database import Database
from utils.config import Config
from utils.excel_handler import ExcelHandler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database and Excel handler instances
db = Database()
excel_handler = ExcelHandler()

# Dictionary to store user states and data
user_data = {}

async def register_registration_handlers(bot):
    """Register all registration and payment related handlers."""
    
    @bot.on(events.CallbackQuery(pattern=r'register'))
    async def registration_start_handler(event):
        """Handler for starting the registration process."""
        sender = await event.get_sender()
        sender_id = sender.id
        
        # Get course details from the message
        message = await event.get_message()
        message_text = message.raw_text
        
        # Extract course information from the message text
        try:
            # Create more flexible pattern matching that works with or without bold formatting
            term_pattern = "🔖 (?:\\*\\*)?ترم(?:\\*\\*)?:"
            teacher_pattern = "👨‍🏫 (?:\\*\\*)?استاد(?:\\*\\*)?:"
            price_pattern = "💰 (?:\\*\\*)?شهریه(?:\\*\\*)?:"
            
            # Check if the message contains the required information
            if not (re.search(term_pattern, message_text) and 
                    re.search(teacher_pattern, message_text) and 
                    re.search(price_pattern, message_text)):
                logger.error(f"Required course information not found in message: {message_text}")
                await event.edit("""اطلاعات کافی برای ثبت‌نام در دسترس نیست.

لطفا ابتدا از منوی اصلی، گزینه «مشاهده دوره‌ها» را انتخاب کنید و پس از انتخاب ترم و استاد، از صفحه جزئیات دوره اقدام به ثبت‌نام نمایید.""", 
                               buttons=KeyboardManager.back_to_main())
                return
                
            # Extract term name (handle both bold and non-bold formats)
            term_match = re.search(f"{term_pattern} (.*?)(?:\\n|$)", message_text)
            if not term_match:
                raise Exception("Could not extract term name")
            term_name = term_match.group(1).strip()
            
            # Extract teacher name (handle both bold and non-bold formats)
            teacher_match = re.search(f"{teacher_pattern} (.*?)(?:\\n|$)", message_text)
            if not teacher_match:
                raise Exception("Could not extract teacher name")
            teacher_name = teacher_match.group(1).strip()
            
            # Extract price (handle both bold and non-bold formats)
            price_match = re.search(f"{price_pattern} (.*?)(?:\\s+تومان|$)", message_text)
            if not price_match:
                raise Exception("Could not extract price")
            price_str = price_match.group(1).strip()
            price = int(price_str.replace(",", ""))
            
            # Get IDs from names
            term_result = db.cursor.execute("SELECT id FROM terms WHERE name = ?", (term_name,)).fetchone()
            if not term_result:
                logger.error(f"Term not found in database: {term_name}")
                await event.edit("ترم مورد نظر در سیستم یافت نشد. لطفا با پشتیبانی تماس بگیرید.", 
                               buttons=KeyboardManager.back_to_main())
                return
                
            term_id = term_result[0]
            
            teacher_result = db.cursor.execute("SELECT id FROM teachers WHERE name = ?", (teacher_name,)).fetchone()
            if not teacher_result:
                logger.error(f"Teacher not found in database: {teacher_name}")
                await event.edit("استاد مورد نظر در سیستم یافت نشد. لطفا با پشتیبانی تماس بگیرید.", 
                               buttons=KeyboardManager.back_to_main())
                return
                
            teacher_id = teacher_result[0]
            
            course_result = db.cursor.execute("SELECT id FROM courses WHERE term_id = ? AND teacher_id = ?", 
                                          (term_id, teacher_id)).fetchone()
            if not course_result:
                logger.error(f"Course not found in database: term_id={term_id}, teacher_id={teacher_id}")
                await event.edit("دوره مورد نظر در سیستم یافت نشد. لطفا با پشتیبانی تماس بگیرید.", 
                               buttons=KeyboardManager.back_to_main())
                return
                
            course_id = course_result[0]
            
            # Store registration info in user_data
            user_data[sender_id] = {
                'term_id': term_id,
                'term_name': term_name,
                'teacher_id': teacher_id,
                'teacher_name': teacher_name,
                'course_id': course_id,
                'price': price,
                'registration_state': 'awaiting_student_id'
            }
            
            # Ask for student ID or national ID
            await event.edit("لطفا شماره دانشجویی یا کد ملی خود را وارد کنید:")
            
        except Exception as e:
            logger.error(f"Error extracting course info: {e}")
            await event.edit("""خطایی در فرآیند ثبت‌نام رخ داد.

لطفا از منوی اصلی، گزینه «مشاهده دوره‌ها» را انتخاب کرده و پس از انتخاب ترم و استاد، از صفحه جزئیات دوره اقدام به ثبت‌نام نمایید.""", 
                           buttons=KeyboardManager.back_to_main())
    
    @bot.on(events.NewMessage(func=lambda e: e.is_private and not e.text.startswith('/')))
    async def message_handler(event):
        """Handler for processing user messages during registration."""
        sender = await event.get_sender()
        sender_id = sender.id
        
        # Check if user is in registration process
        if sender_id in user_data:
            state = user_data[sender_id].get('registration_state')
            
            # Handle student ID input
            if state == 'awaiting_student_id':
                student_id = event.text.strip()
                
                # Validate student ID (updated validation - only max length)
                if not re.match(r'^\d{1,20}$', student_id):
                    await event.respond("شماره دانشجویی یا کد ملی باید حداکثر ۲۰ رقم باشد. لطفا مجددا وارد کنید:")
                    return
                
                # Check student ID in Excel file
                exists, first_name, last_name = excel_handler.check_student_id(student_id)
                
                # Store student ID regardless of whether it exists
                user_data[sender_id]['student_id'] = student_id
                user_data[sender_id]['registration_state'] = 'confirm_student_info'
                
                if exists:
                    # Student exists in Excel file - store their info
                    user_data[sender_id]['first_name'] = first_name
                    user_data[sender_id]['last_name'] = last_name
                    
                    # Ask for confirmation with full information
                    confirm_message = f"""اطلاعات دانشجویی شما:

نام و نام خانوادگی: **{first_name} {last_name}**
شماره شناسایی: **{student_id}**

آیا اطلاعات فوق صحیح است؟"""
                    
                    await event.respond(confirm_message, buttons=KeyboardManager.confirm_keyboard())
                else:
                    # Student not found - use placeholder values and let them continue
                    user_data[sender_id]['first_name'] = "در حال بررسی"
                    user_data[sender_id]['last_name'] = "در حال بررسی"
                    
                    # Inform user and let them continue
                    not_found_message = f"""در لیست فعلی مشخصات شما با شماره **{student_id}** پیدا نشد.

در ساعات آینده بعد از بررسی دقیق‌تر، درخواست تایید اطلاعات برایتان ارسال خواهد شد.
بدون در نظر گرفتن این مورد می‌توانید به بقیه مراحل ثبت‌نام خود بپردازید.

آیا مایل به ادامه ثبت‌نام هستید؟"""
                    
                    await event.respond(not_found_message, buttons=KeyboardManager.confirm_keyboard())
            
    @bot.on(events.CallbackQuery(pattern=r'confirm'))
    async def confirm_student_info_handler(event):
        """Handler for confirming student information."""
        sender = await event.get_sender()
        sender_id = sender.id
        
        if sender_id in user_data and user_data[sender_id].get('registration_state') == 'confirm_student_info':
            # Update registration state
            user_data[sender_id]['registration_state'] = 'select_payment_type'
            
            # Register user in database
            db.register_user(
                telegram_id=sender_id,
                student_id=user_data[sender_id]['student_id'],
                first_name=user_data[sender_id]['first_name'],
                last_name=user_data[sender_id]['last_name']
            )
            
            # Ask for payment type
            await event.edit("لطفا نوع پرداخت را انتخاب کنید:", 
                             buttons=KeyboardManager.payment_type_menu())
    
    @bot.on(events.CallbackQuery(pattern=r'payment_type_(in_person|card)'))
    async def payment_type_handler(event):
        """Handler for payment type selection."""
        sender = await event.get_sender()
        sender_id = sender.id
        payment_type = event.data.decode('utf-8').split('_')[-1]
        
        if sender_id in user_data and user_data[sender_id].get('registration_state') == 'select_payment_type':
            # Store payment type
            user_data[sender_id]['payment_type'] = 'in_person' if payment_type == 'in_person' else 'card'
            user_data[sender_id]['registration_state'] = 'select_payment_method'
            
            # Ask for payment method
            await event.edit("لطفا نحوه پرداخت را انتخاب کنید:", 
                             buttons=KeyboardManager.payment_method_menu())
    
    @bot.on(events.CallbackQuery(pattern=r'payment_method_(full|installment)'))
    async def payment_method_handler(event):
        """Handler for payment method selection."""
        sender = await event.get_sender()
        sender_id = sender.id
        payment_method = event.data.decode('utf-8').split('_')[-1]
        
        if sender_id in user_data and user_data[sender_id].get('registration_state') == 'select_payment_method':
            # Store payment method
            user_data[sender_id]['payment_method'] = payment_method
            
            # Add registration to database
            registration_id = db.add_registration(
                telegram_id=sender_id,
                student_id=user_data[sender_id]['student_id'],
                course_id=user_data[sender_id]['course_id'],
                term_id=user_data[sender_id]['term_id'],
                teacher_id=user_data[sender_id]['teacher_id'],
                payment_type=user_data[sender_id]['payment_type'],
                payment_method=payment_method
            )
            
            if not registration_id:
                await event.edit("خطایی در ثبت درخواست رخ داد. لطفا مجددا تلاش کنید.")
                return
            
            # Store registration ID
            user_data[sender_id]['registration_id'] = registration_id
            
            # Calculate payment amount
            price = user_data[sender_id]['price']
            if payment_method == 'installment':
                payment_amount = price // 2
                payment_text = f"قسط اول: {payment_amount:,} تومان"
            else:
                payment_amount = price
                payment_text = f"مبلغ کامل: {payment_amount:,} تومان"
            
            user_data[sender_id]['payment_amount'] = payment_amount
            
            # Process according to payment type
            if user_data[sender_id]['payment_type'] == 'in_person':
                # Process in-person payment
                user_data[sender_id]['registration_state'] = 'in_person_payment'
                
                message = f"""درخواست ثبت‌نام شما با موفقیت ثبت شد.

**اطلاعات پرداخت حضوری:**
دوره: {user_data[sender_id]['term_name']} با استاد {user_data[sender_id]['teacher_name']}
{payment_text}

لطفا در ساعات اداری به دفتر انجمن مراجعه کنید و پس از پرداخت، شماره رسید را به این ربات ارسال کنید.

آدرس دفتر انجمن: ساختمان مرکزی دانشگاه، طبقه دوم، اتاق 204
ساعات کاری: شنبه تا چهارشنبه، 8 الی 16"""
                
                # Notify admin
                needs_verification = user_data[sender_id]['first_name'] == "در حال بررسی"
                verification_note = "\n⚠️ نیاز به بررسی هویت دانشجو (اطلاعات در سیستم یافت نشد)" if needs_verification else ""
                
                admin_message = f"""درخواست پرداخت حضوری جدید:

نام و نام خانوادگی: {user_data[sender_id]['first_name']} {user_data[sender_id]['last_name']}
شماره دانشجویی/کد ملی: {user_data[sender_id]['student_id']}
دوره: {user_data[sender_id]['term_name']} با استاد {user_data[sender_id]['teacher_name']}
نوع پرداخت: {'قسطی' if payment_method == 'installment' else 'کامل'}
مبلغ: {payment_amount:,} تومان{verification_note}"""
                
                try:
                    admin_id = Config.ADMIN_ID
                    if admin_id:
                        await bot.send_message(admin_id, admin_message, 
                                               buttons=KeyboardManager.admin_payment_approval())
                except Exception as e:
                    logger.error(f"Error notifying admin: {e}")
                
                await event.edit(message, buttons=KeyboardManager.back_to_main())
                
            else:
                # Process card payment
                user_data[sender_id]['registration_state'] = 'card_payment'
                
                message = f"""درخواست ثبت‌نام شما با موفقیت ثبت شد.

**اطلاعات پرداخت کارت به کارت:**
دوره: {user_data[sender_id]['term_name']} با استاد {user_data[sender_id]['teacher_name']}
{payment_text}

لطفا مبلغ را به شماره کارت زیر واریز کنید و تصویر رسید پرداخت را ارسال نمایید:

🏦 شماره کارت: {Config.CARD_NUMBER}
📝 به نام: {Config.CARD_OWNER}"""
                
                await event.edit(message)
    
    @bot.on(events.NewMessage(func=lambda e: e.is_private and e.photo))
    async def receipt_photo_handler(event):
        """Handler for processing receipt photos."""
        sender = await event.get_sender()
        sender_id = sender.id
        
        if sender_id in user_data and user_data[sender_id].get('registration_state') == 'card_payment':
            # Download and save the photo
            photo = await event.download_media(file=f"data/receipts/{sender_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
            
            if photo:
                # Update registration with receipt photo
                db.update_registration_receipt(
                    registration_id=user_data[sender_id]['registration_id'],
                    receipt_photo_link=photo
                )
                
                # Notify admin
                needs_verification = user_data[sender_id]['first_name'] == "در حال بررسی"
                verification_note = "\n⚠️ نیاز به بررسی هویت دانشجو (اطلاعات در سیستم یافت نشد)" if needs_verification else ""
                
                admin_message = f"""درخواست بررسی پرداخت کارت به کارت جدید:

نام و نام خانوادگی: {user_data[sender_id]['first_name']} {user_data[sender_id]['last_name']}
شماره دانشجویی/کد ملی: {user_data[sender_id]['student_id']}
دوره: {user_data[sender_id]['term_name']} با استاد {user_data[sender_id]['teacher_name']}
نوع پرداخت: {'قسطی' if user_data[sender_id]['payment_method'] == 'installment' else 'کامل'}
مبلغ: {user_data[sender_id]['payment_amount']:,} تومان{verification_note}"""
                
                # Make registration ID available to admin for approval/rejection
                user_data[sender_id]['receipt_data'] = {
                    'registration_id': user_data[sender_id]['registration_id'],
                    'is_first_payment': True
                }
                
                try:
                    admin_id = Config.ADMIN_ID
                    if admin_id:
                        # Send message with photo to admin
                        await bot.send_file(admin_id, photo, caption=admin_message, 
                                           buttons=KeyboardManager.admin_payment_approval())
                except Exception as e:
                    logger.error(f"Error notifying admin: {e}")
                
                # Thank user and update state
                await event.respond("""تصویر رسید پرداخت شما دریافت شد.
پس از بررسی و تأیید، نتیجه به شما اطلاع داده خواهد شد.
با تشکر از ثبت‌نام شما.""", buttons=KeyboardManager.back_to_main())
                
                # Reset user registration state
                user_data[sender_id]['registration_state'] = 'receipt_submitted'
            else:
                await event.respond("خطا در دریافت تصویر رسید. لطفا مجددا تلاش کنید.")
    
    @bot.on(events.CallbackQuery(pattern=r'check_registration_status'))
    async def check_status_handler(event):
        """Handler for checking registration status."""
        sender = await event.get_sender()
        sender_id = sender.id
        
        # Get user's registrations from database
        registrations = db.get_user_registrations(sender_id)
        
        if not registrations:
            await event.edit("""شما هیچ ثبت‌نامی در سیستم ندارید.

برای ثبت‌نام در دوره‌ها، از منوی اصلی گزینه «مشاهده دوره‌ها» را انتخاب کنید.""", buttons=KeyboardManager.back_to_main())
            return
        
        # Format registrations list
        message = "**ثبت‌نام‌های شما:**\n\n"
        
        for i, reg in enumerate(registrations, 1):
            # Unpack the registration data to match the database columns
            # From the SQL query, the columns are:
            # r.id, tm.name as term_name, t.name as teacher_name, c.price, 
            # r.payment_status, r.first_payment_confirmed, r.second_payment_confirmed,
            # r.payment_type, r.payment_method, r.registration_date
            
            reg_id = reg[0]
            term_name = reg[1]
            teacher_name = reg[2]
            price = reg[3]
            payment_status = reg[4]
            first_payment = reg[5]
            second_payment = reg[6]
            payment_type = reg[7]
            payment_method = reg[8]
            # registration_date = reg[9] (not used here)
            
            payment_info = f"قسط {'دوم' if second_payment else 'اول'}" if payment_method == 'installment' else "پرداخت کامل"
            payment_amount = price // 2 if payment_method == 'installment' and not second_payment else price
            
            # Format payment status
            if payment_status == 'pending':
                status_text = "در انتظار تأیید"
            elif payment_status == 'approved':
                if payment_method == 'installment' and not second_payment:
                    status_text = "قسط اول تأیید شده"
                    # Add button for second payment
                    second_payment_button = KeyboardManager.second_payment_menu(reg_id)
                else:
                    status_text = "تأیید شده"
                    second_payment_button = None
            else:
                status_text = "نامشخص"
                second_payment_button = None
            
            message += f"""--- دوره شماره {i} ---
دوره: {term_name} با استاد {teacher_name}
نوع پرداخت: {payment_type} ({payment_info})
مبلغ: {payment_amount:,} تومان
وضعیت: {status_text}

"""
            
            # If registration is approved and needs second payment, send separate message with payment button
            if payment_status == 'approved' and payment_method == 'installment' and not second_payment:
                second_payment_message = f"""برای پرداخت قسط دوم دوره {term_name} با استاد {teacher_name} به مبلغ {price // 2:,} تومان، از دکمه زیر استفاده کنید:"""
                await bot.send_message(sender_id, second_payment_message, buttons=second_payment_button)
        
        # Send main message with back button
        await event.edit(message, buttons=KeyboardManager.back_to_main())
    
    @bot.on(events.CallbackQuery(pattern=r'pay_second_installment_(\d+)'))
    async def second_payment_handler(event):
        """Handler for second installment payment."""
        sender = await event.get_sender()
        sender_id = sender.id
        registration_id = int(event.data.decode('utf-8').split('_')[-1])
        
        # Get registration details
        registration = db.get_registration_by_id(registration_id)
        
        if not registration:
            await event.edit("اطلاعات ثبت‌نام یافت نشد. لطفا با پشتیبانی تماس بگیرید.")
            return
        
        # Prepare user data for second payment
        user_data[sender_id] = {
            'registration_id': registration_id,
            'payment_amount': registration[14] // 2,  # Half of the course price
            'payment_type': registration[7],
            'registration_state': 'second_payment'
        }
        
        # Check payment type
        if registration[7] == 'in_person':
            # In-person payment instructions
            message = f"""**اطلاعات پرداخت قسط دوم (حضوری):**

مبلغ: {user_data[sender_id]['payment_amount']:,} تومان

لطفا در ساعات اداری به دفتر انجمن مراجعه کنید و پس از پرداخت، شماره رسید را به این ربات ارسال کنید.

آدرس دفتر انجمن: ساختمان مرکزی دانشگاه، طبقه دوم، اتاق 204
ساعات کاری: شنبه تا چهارشنبه، 8 الی 16"""
            
            await event.edit(message, buttons=KeyboardManager.back_to_main())
            
            # Notify admin
            admin_message = f"""درخواست پرداخت حضوری قسط دوم:

نام و نام خانوادگی: {registration[15]} {registration[16]}
شماره دانشجویی/کد ملی: {registration[2]}
دوره: {registration[19]} با استاد {registration[18]}
مبلغ: {user_data[sender_id]['payment_amount']:,} تومان"""
            
            # Check if the name indicates the user needs verification
            if registration[15] == "در حال بررسی":
                admin_message += "\n⚠️ نیاز به بررسی هویت دانشجو (اطلاعات در سیستم یافت نشد)"
            
            try:
                admin_id = Config.ADMIN_ID
                if admin_id:
                    await bot.send_message(admin_id, admin_message, 
                                         buttons=KeyboardManager.admin_payment_approval())
            except Exception as e:
                logger.error(f"Error notifying admin: {e}")
        else:
            # Card payment instructions
            message = f"""**اطلاعات پرداخت قسط دوم (کارت به کارت):**

مبلغ: {user_data[sender_id]['payment_amount']:,} تومان

لطفا مبلغ را به شماره کارت زیر واریز کنید و تصویر رسید پرداخت را ارسال نمایید:

🏦 شماره کارت: {Config.CARD_NUMBER}
📝 به نام: {Config.CARD_OWNER}"""
            
            await event.edit(message)
            
            # Set state for receipt handling
            user_data[sender_id]['registration_state'] = 'second_payment_receipt'
    
    # Admin payment approval handling
    @bot.on(events.CallbackQuery(pattern=r'admin_(approve|reject)'))
    async def admin_payment_handler(event):
        """Handler for admin payment approval or rejection."""
        sender = await event.get_sender()
        sender_id = sender.id
        action = event.data.decode('utf-8').split('_')[1]
        
        # Only admin can approve/reject payments
        if sender_id != Config.ADMIN_ID:
            await event.answer("شما مجوز انجام این عملیات را ندارید.", alert=True)
            return
        
        # Get message to extract registration info
        message = await event.get_message()
        message_text = message.raw_text
        
        # Extract student info from message
        try:
            lines = message_text.split('\n')
            name_line = [line for line in lines if "نام و نام خانوادگی:" in line][0]
            # Check both formats for student ID line
            student_id_line = next((line for line in lines if "شماره دانشجویی/کد ملی:" in line or "شماره دانشجویی:" in line), None)
            
            if not student_id_line:
                raise Exception("Student ID line not found in message")
                
            name = name_line.split(": ")[1].strip()
            student_id = student_id_line.split(": ")[1].strip()
            
            # Find the user and registration in database
            telegram_id = db.cursor.execute("SELECT telegram_id FROM users WHERE student_id = ?", 
                                           (student_id,)).fetchone()[0]
            
            # Get the most recent pending registration for this user
            registration_id = db.cursor.execute("""
            SELECT id FROM registrations 
            WHERE telegram_id = ? AND payment_status = 'pending'
            ORDER BY registration_date DESC LIMIT 1
            """, (telegram_id,)).fetchone()[0]
            
            # Check if this is a second payment
            is_second_payment = "قسط دوم" in message_text
            
            # Update payment status
            new_status = 'confirmed' if action == 'approve' else 'rejected'
            db.update_payment_status(registration_id, new_status, not is_second_payment)
            
            # Notify user
            if action == 'approve':
                user_message = f"""پرداخت شما با موفقیت تأیید شد.

{f'قسط {"دوم" if is_second_payment else "اول"} پرداخت شد.' if "قسطی" in message_text else 'پرداخت کامل انجام شد.'}

با تشکر از ثبت‌نام شما در دوره."""
            else:
                user_message = f"""متأسفانه پرداخت شما تأیید نشد.

دلیل: تصویر رسید پرداخت نامعتبر یا ناخوانا.

لطفا مجددا اقدام کنید یا با پشتیبانی تماس بگیرید."""
            
            await bot.send_message(telegram_id, user_message, buttons=KeyboardManager.back_to_main())
            
            # Update admin message
            await event.edit(f"{message_text}\n\n{'✅ تأیید شد' if action == 'approve' else '❌ رد شد'}")
            
        except Exception as e:
            logger.error(f"Error in admin payment handler: {e}")
            await event.answer("خطا در پردازش درخواست. لطفا مجددا تلاش کنید.", alert=True)
    
    @bot.on(events.CallbackQuery(pattern=r'cancel'))
    async def cancel_handler(event):
        """Handler for cancelling operations."""
        sender = await event.get_sender()
        sender_id = sender.id
        
        if sender_id in user_data:
            # Clear user data
            user_data.pop(sender_id, None)
        
        await event.edit("عملیات لغو شد. به منوی اصلی بازگشتید.", 
                        buttons=KeyboardManager.main_menu())
    
    logger.info("Registration handlers registered successfully") 