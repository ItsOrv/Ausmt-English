from telethon import Button
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KeyboardManager:
    """
    Class to manage keyboard creation for the Telegram bot.
    All keyboard buttons are defined here for easy management and consistency.
    """
    
    @staticmethod
    def main_menu():
        """Create main menu keyboard."""
        keyboard = [
            [Button.text("📚 مشاهده دوره‌ها", resize=True)],
            [Button.text("📄 پیگیری وضعیت ثبت‌نام و پرداخت", resize=True)],
            [Button.text("ℹ️ درباره انجمن", resize=True)],
            [Button.text("❓ سوالات متداول", resize=True)],
            [Button.text("📞 ارتباط با پشتیبانی", resize=True)]
        ]
        return keyboard
    
    @staticmethod
    def terms_menu(terms):
        """
        Create keyboard for terms selection.
        
        Args:
            terms (list): List of (id, name, description) tuples for each term
            
        Returns:
            list: Keyboard buttons for terms
        """
        keyboard = []
        for term_id, term_name, _ in terms:
            keyboard.append([Button.inline(term_name, data=f"term_{term_id}")])
        
        # Add back button
        keyboard.append([Button.inline("🔙 بازگشت به منوی اصلی", data="back_to_main")])
        return keyboard
    
    @staticmethod
    def teachers_menu(teachers):
        """
        Create keyboard for teachers selection.
        
        Args:
            teachers (list): List of (id, name, bio) tuples for each teacher
            
        Returns:
            list: Keyboard buttons for teachers
        """
        keyboard = []
        for teacher_id, teacher_name, _ in teachers:
            keyboard.append([Button.inline(teacher_name, data=f"teacher_{teacher_id}")])
        
        # Add back button
        keyboard.append([Button.inline("🔙 بازگشت به انتخاب ترم", data="back_to_terms")])
        return keyboard
    
    @staticmethod
    def registration_menu():
        """Create registration keyboard."""
        keyboard = [
            [Button.inline("ثبت‌نام و پرداخت ✅", data="register")],
            [Button.inline("🔙 بازگشت به انتخاب استاد", data="back_to_teachers")]
        ]
        return keyboard
    
    @staticmethod
    def payment_type_menu():
        """Create payment type selection keyboard."""
        keyboard = [
            [Button.inline("💵 پرداخت حضوری", data="payment_type_in_person")],
            [Button.inline("💳 پرداخت کارت به کارت", data="payment_type_card")]
        ]
        return keyboard
    
    @staticmethod
    def payment_method_menu():
        """Create payment method selection keyboard."""
        keyboard = [
            [Button.inline("پرداخت کامل 💯", data="payment_method_full")],
            [Button.inline("پرداخت در دو قسط 💸", data="payment_method_installment")]
        ]
        return keyboard
    
    @staticmethod
    def confirm_keyboard():
        """Create confirmation keyboard."""
        keyboard = [
            [Button.inline("تأیید ✅", data="confirm")],
            [Button.inline("انصراف ❌", data="cancel")]
        ]
        return keyboard
    
    @staticmethod
    def admin_payment_approval():
        """Create admin payment approval keyboard."""
        keyboard = [
            [Button.inline("تأیید پرداخت ✅", data="admin_approve")],
            [Button.inline("عدم تأیید پرداخت ❌", data="admin_reject")]
        ]
        return keyboard
    
    @staticmethod
    def back_to_main():
        """Create back to main menu keyboard."""
        keyboard = [
            [Button.inline("🔙 بازگشت به منوی اصلی", data="back_to_main")]
        ]
        return keyboard
    
    @staticmethod
    def second_payment_menu(registration_id):
        """Create second payment menu keyboard."""
        keyboard = [
            [Button.inline("پرداخت قسط دوم 💰", data=f"pay_second_installment_{registration_id}")],
            [Button.inline("🔙 بازگشت", data="back_to_main")]
        ]
        return keyboard
    
    @staticmethod
    def admin_menu():
        """Create admin menu keyboard."""
        keyboard = [
            [Button.text("📊 مدیریت پرداخت‌ها", resize=True)],
            [Button.text("📨 ارسال پیام گروهی", resize=True)],
            [Button.text("🔙 بازگشت به منوی اصلی", resize=True)]
        ]
        return keyboard 