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

async def register_start_handlers(bot):
    """Register all start and main menu handlers."""
    
    @bot.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        """Handler for /start command."""
        sender = await event.get_sender()
        logger.info(f"Start command received from {sender.id}")
        
        # Welcome message with user's first name
        welcome_message = f"""سلام {sender.first_name}! 👋

به ربات ثبت‌نام دوره‌های زبان انجمن خوش آمدید.
لطفا از منوی زیر گزینه مورد نظر خود را انتخاب کنید:"""
        
        # Send welcome message with main menu keyboard
        await event.respond(welcome_message, buttons=KeyboardManager.main_menu())
    
    @bot.on(events.NewMessage(pattern='📚 مشاهده دوره‌ها'))
    async def view_courses_handler(event):
        """Handler for viewing courses."""
        # Get all terms from database
        terms = db.get_terms()
        
        await event.respond("لطفا ترم مورد نظر خود را انتخاب کنید:", 
                           buttons=KeyboardManager.terms_menu(terms))
    
    @bot.on(events.CallbackQuery(pattern=r'term_(\d+)'))
    async def term_selection_handler(event):
        """Handler for term selection."""
        # Extract term ID from callback data
        term_id = int(event.data.decode('utf-8').split('_')[1])
        
        # Get teachers for this term
        teachers = db.get_teachers_by_term(term_id)
        
        # Store term selection in user data (will be implemented in session management)
        # For now, we'll use a simple callback data approach
        
        await event.edit("لطفا استاد مورد نظر خود را انتخاب کنید:",
                        buttons=KeyboardManager.teachers_menu(teachers))
    
    @bot.on(events.CallbackQuery(pattern=r'teacher_(\d+)'))
    async def teacher_selection_handler(event):
        """Handler for teacher selection."""
        # Extract teacher ID from callback data
        teacher_id = int(event.data.decode('utf-8').split('_')[1])
        
        # Get term ID from previous selection (would be in user session in real app)
        # For now, we'll query the database directly
        query = await event.get_message()
        prev_data = query.raw_text
        
        # This would be replaced with proper session management
        # For demonstration, we'll assume a fixed term ID
        term_id = db.cursor.execute("SELECT term_id FROM teachers WHERE id = ?", (teacher_id,)).fetchone()[0]
        
        # Get course details
        course_details = db.get_course_details(term_id, teacher_id)
        
        if not course_details:
            await event.edit("متأسفانه جزئیات دوره یافت نشد. لطفا با پشتیبانی تماس بگیرید.")
            return
        
        # Unpack course details
        course_id, term_name, day, time, location, topics, price = course_details
        
        # Format course details
        details_message = f"""**جزئیات دوره**

🔖 **ترم**: {term_name}
👨‍🏫 **استاد**: {db.cursor.execute("SELECT name FROM teachers WHERE id = ?", (teacher_id,)).fetchone()[0]}
📅 **روز**: {day}
🕒 **ساعت**: {time}
📍 **مکان**: {location}
📚 **مباحث**: {topics}
💰 **شهریه**: {price:,} تومان

برای ثبت‌نام و پرداخت دکمه زیر را فشار دهید:"""
        
        # Store course info in callback data
        callback_data = f"course_{course_id}_term_{term_id}_teacher_{teacher_id}"
        
        await event.edit(details_message, buttons=KeyboardManager.registration_menu())
    
    @bot.on(events.CallbackQuery(pattern=r'back_to_main'))
    async def back_to_main_handler(event):
        """Handler for back to main menu button."""
        sender = await event.get_sender()
        
        # Welcome message with user's first name
        welcome_message = f"""منوی اصلی

لطفا گزینه مورد نظر خود را انتخاب کنید:"""
        
        await event.edit(welcome_message, buttons=KeyboardManager.main_menu())
    
    @bot.on(events.CallbackQuery(pattern=r'back_to_terms'))
    async def back_to_terms_handler(event):
        """Handler for back to terms selection button."""
        # Get all terms from database
        terms = db.get_terms()
        
        await event.edit("لطفا ترم مورد نظر خود را انتخاب کنید:", 
                         buttons=KeyboardManager.terms_menu(terms))
    
    @bot.on(events.CallbackQuery(pattern=r'back_to_teachers'))
    async def back_to_teachers_handler(event):
        """Handler for back to teachers selection button."""
        # This would ideally use session data to get the last selected term
        # For demonstration, we'll assume the user is viewing a course
        # with a teacher who belongs to a term, so we'll get the term from there
        query = await event.get_message()
        message_text = query.raw_text
        
        # Extract term from message (in a real app, use session data)
        try:
            term_name = message_text.split("🔖 **ترم**: ")[1].split("\n")[0]
            term_id = db.cursor.execute("SELECT id FROM terms WHERE name = ?", (term_name,)).fetchone()[0]
        except:
            # Fallback to first term if parsing fails
            term_id = 1
        
        # Get teachers for this term
        teachers = db.get_teachers_by_term(term_id)
        
        await event.edit("لطفا استاد مورد نظر خود را انتخاب کنید:",
                         buttons=KeyboardManager.teachers_menu(teachers))
    
    @bot.on(events.NewMessage(pattern='ℹ️ درباره انجمن'))
    async def about_handler(event):
        """Handler for about the association."""
        # Get about information from database
        about = db.get_about()
        
        if about:
            title, content = about
            about_message = f"""**{title}**

{content}"""
        else:
            about_message = "اطلاعاتی درباره انجمن وجود ندارد."
        
        await event.respond(about_message, buttons=KeyboardManager.back_to_main())
    
    @bot.on(events.NewMessage(pattern='❓ سوالات متداول'))
    async def faq_handler(event):
        """Handler for FAQ."""
        # Get FAQ items from database
        faq_items = db.get_faq()
        
        if faq_items:
            faq_message = "**سوالات متداول**\n\n"
            for i, (question, answer) in enumerate(faq_items, 1):
                faq_message += f"**{i}. {question}**\n{answer}\n\n"
        else:
            faq_message = "در حال حاضر سوالی در بخش سوالات متداول وجود ندارد."
        
        await event.respond(faq_message, buttons=KeyboardManager.back_to_main())
    
    @bot.on(events.NewMessage(pattern='📞 ارتباط با پشتیبانی'))
    async def contact_support_handler(event):
        """Handler for contacting support."""
        support_message = """**ارتباط با پشتیبانی**

برای ارتباط با پشتیبانی می‌توانید از راه‌های زیر اقدام کنید:

📱 **شماره تماس**: 021-12345678
📧 **ایمیل**: support@example.com
🌐 **کانال تلگرام**: @language_association
⏰ **ساعات پاسخگویی**: شنبه تا چهارشنبه، ساعت 8 تا 16"""
        
        await event.respond(support_message, buttons=KeyboardManager.back_to_main())
    
    logger.info("Start and main menu handlers registered successfully") 