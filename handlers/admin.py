from telethon import events
import logging
from utils.keyboards import KeyboardManager
from database import Database
from utils.config import Config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database instance
db = Database()

# Admin state storage
admin_state = {}

async def register_admin_handlers(bot):
    """Register all admin handlers."""
    
    @bot.on(events.NewMessage(pattern='/admin'))
    async def admin_handler(event):
        """Handler for admin command."""
        sender = await event.get_sender()
        sender_id = sender.id
        
        # Check if sender is admin
        if sender_id != Config.ADMIN_ID:
            await event.respond("شما مجوز دسترسی به پنل ادمین را ندارید.")
            return
        
        admin_message = """🔐 **پنل مدیریت**

به پنل مدیریت ربات ثبت‌نام دوره‌های زبان خوش آمدید.
لطفا از منوی زیر گزینه مورد نظر خود را انتخاب کنید:"""
        
        await event.respond(admin_message, buttons=KeyboardManager.admin_menu())
    
    @bot.on(events.NewMessage(pattern='📊 مدیریت پرداخت‌ها'))
    async def manage_payments_handler(event):
        """Handler for managing payments."""
        sender = await event.get_sender()
        sender_id = sender.id
        
        # Check if sender is admin
        if sender_id != Config.ADMIN_ID:
            return
        
        # Get pending registrations
        pending_registrations = db.get_pending_registrations()
        
        if not pending_registrations:
            await event.respond("در حال حاضر هیچ درخواست پرداخت در انتظار تأیید وجود ندارد.",
                               buttons=KeyboardManager.back_to_main())
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
        
        await event.respond(message, buttons=KeyboardManager.back_to_main())
    
    @bot.on(events.NewMessage(pattern='📨 ارسال پیام گروهی'))
    async def broadcast_message_handler(event):
        """Handler for sending broadcast messages."""
        sender = await event.get_sender()
        sender_id = sender.id
        
        # Check if sender is admin
        if sender_id != Config.ADMIN_ID:
            return
        
        admin_state[sender_id] = {'state': 'awaiting_broadcast_message'}
        
        await event.respond("""لطفا پیام خود را برای ارسال به همه کاربران ربات وارد کنید:

برای لغو عملیات، دستور /cancel را ارسال کنید.""")
    
    @bot.on(events.NewMessage(func=lambda e: e.is_private and not e.text.startswith('/') and e.sender_id == Config.ADMIN_ID))
    async def admin_message_handler(event):
        """Handler for processing admin messages."""
        sender = await event.get_sender()
        sender_id = sender.id
        
        # Check if admin is in broadcasting state
        if sender_id in admin_state and admin_state[sender_id].get('state') == 'awaiting_broadcast_message':
            # Get broadcast message
            broadcast_message = event.text
            
            # Confirm before sending
            admin_state[sender_id]['broadcast_message'] = broadcast_message
            admin_state[sender_id]['state'] = 'confirm_broadcast'
            
            confirm_message = f"""پیام شما برای ارسال گروهی:

{broadcast_message}

آیا از ارسال این پیام به تمام کاربران اطمینان دارید؟"""
            
            await event.respond(confirm_message, buttons=[
                [events.Button.inline("✅ بله، ارسال شود", data="confirm_broadcast")],
                [events.Button.inline("❌ خیر، لغو شود", data="cancel_broadcast")]
            ])
    
    @bot.on(events.CallbackQuery(pattern=r'confirm_broadcast'))
    async def confirm_broadcast_handler(event):
        """Handler for confirming broadcast message."""
        sender = await event.get_sender()
        sender_id = sender.id
        
        # Check if sender is admin
        if sender_id != Config.ADMIN_ID:
            await event.answer("شما مجوز انجام این عملیات را ندارید.", alert=True)
            return
        
        # Check if admin is in confirm broadcast state
        if sender_id in admin_state and admin_state[sender_id].get('state') == 'confirm_broadcast':
            broadcast_message = admin_state[sender_id]['broadcast_message']
            
            # Get all users
            db.cursor.execute("SELECT telegram_id FROM users")
            users = db.cursor.fetchall()
            
            if not users:
                await event.edit("هیچ کاربری برای ارسال پیام یافت نشد.")
                return
            
            # Count successful sends
            successful_sends = 0
            
            # Send broadcast message
            await event.edit("در حال ارسال پیام گروهی...")
            
            for user_id in users:
                try:
                    await bot.send_message(user_id[0], f"**پیام از طرف انجمن زبان**:\n\n{broadcast_message}")
                    successful_sends += 1
                except Exception as e:
                    logger.error(f"Error sending broadcast to user {user_id[0]}: {e}")
            
            # Clear admin state
            admin_state.pop(sender_id, None)
            
            await bot.send_message(sender_id, f"پیام گروهی با موفقیت به {successful_sends} کاربر از {len(users)} کاربر ارسال شد.",
                                  buttons=KeyboardManager.back_to_main())
    
    @bot.on(events.CallbackQuery(pattern=r'cancel_broadcast'))
    async def cancel_broadcast_handler(event):
        """Handler for cancelling broadcast message."""
        sender = await event.get_sender()
        sender_id = sender.id
        
        # Check if sender is admin
        if sender_id != Config.ADMIN_ID:
            await event.answer("شما مجوز انجام این عملیات را ندارید.", alert=True)
            return
        
        # Clear admin state
        admin_state.pop(sender_id, None)
        
        await event.edit("ارسال پیام گروهی لغو شد.", buttons=KeyboardManager.back_to_main())
    
    @bot.on(events.NewMessage(pattern='/cancel'))
    async def cancel_admin_handler(event):
        """Handler for admin cancelling operations."""
        sender = await event.get_sender()
        sender_id = sender.id
        
        # Check if sender is admin
        if sender_id != Config.ADMIN_ID:
            return
        
        # Clear admin state
        admin_state.pop(sender_id, None)
        
        await event.respond("عملیات لغو شد.", buttons=KeyboardManager.back_to_main())
    
    logger.info("Admin handlers registered successfully") 