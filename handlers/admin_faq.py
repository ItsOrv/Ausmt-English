from telethon import events, Button
from handlers.admin_utils import admin_state, db, logger, admin_required, edit_or_respond, clear_admin_state
from utils.keyboards import KeyboardManager

async def manage_faq_handler(event):
    """Handle FAQ management request."""
    if not await admin_required(event):
        return
    
    logger.info(f"Admin {event.sender_id} accessing FAQ management")
    
    # Get all FAQs from database
    faqs = db.get_faq()
    
    admin_message = "❓ مدیریت سوالات متداول\n\n"
    if faqs:
        for faq in faqs:
            faq_id, question, answer = faq
            admin_message += f"🔹 شناسه: {faq_id}\n"
            admin_message += f"🔹 سوال: {question}\n"
            admin_message += f"🔹 پاسخ: {answer[:50]}...\n\n"
    else:
        admin_message += "هیچ سوال متداولی در پایگاه داده یافت نشد."
    
    # Add keyboard for FAQ management options
    keyboard = [
        [Button.inline("➕ افزودن سوال", data="add_faq")],
        [Button.inline("✏️ ویرایش سوال", data="edit_faq")],
        [Button.inline("❌ حذف سوال", data="delete_faq")],
        [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
    ]
    
    await edit_or_respond(event, admin_message, buttons=keyboard)

async def add_faq_handler(event):
    """Handle add FAQ request."""
    if not await admin_required(event):
        return
    
    logger.info(f"Admin {event.sender_id} accessing add FAQ form")
    
    # Store state
    admin_state[event.sender_id] = {
        'state': 'adding_faq',
        'step': 'question'
    }
    
    await event.edit("""لطفا سوال متداول را وارد کنید:

برای لغو عملیات، دستور /cancel را ارسال کنید.""")

async def edit_faq_handler(event):
    """Handle edit FAQ request."""
    if not await admin_required(event):
        return
    
    logger.info(f"Admin {event.sender_id} accessing edit FAQ form")
    
    # Get all FAQs
    faqs = db.get_faq()
    
    if not faqs:
        await event.edit("هیچ سوال متداولی برای ویرایش وجود ندارد.", buttons=[
            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
        ])
        return
    
    # Create keyboard for FAQ selection
    keyboard = []
    for faq in faqs:
        faq_id, question, _ = faq
        keyboard.append([Button.inline(f"{question[:40]}...", data=f"edit_faq_{faq_id}")])
    
    keyboard.append([Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")])
    
    await event.edit("لطفا سوال مورد نظر برای ویرایش را انتخاب کنید:", buttons=keyboard)

async def delete_faq_handler(event):
    """Handle delete FAQ request."""
    if not await admin_required(event):
        return
    
    logger.info(f"Admin {event.sender_id} accessing delete FAQ form")
    
    # Get all FAQs
    faqs = db.get_faq()
    
    if not faqs:
        await event.edit("هیچ سوال متداولی برای حذف وجود ندارد.", buttons=[
            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
        ])
        return
    
    # Create keyboard for FAQ selection
    keyboard = []
    for faq in faqs:
        faq_id, question, _ = faq
        keyboard.append([Button.inline(f"{question[:40]}...", data=f"confirm_delete_faq_{faq_id}")])
    
    keyboard.append([Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")])
    
    await event.edit("لطفا سوال مورد نظر برای حذف را انتخاب کنید:", buttons=keyboard)

async def edit_faq_id_handler(event):
    """Handle FAQ selection for editing."""
    if not await admin_required(event):
        return
    
    # Extract FAQ ID from callback data
    faq_id = int(event.data.decode().split('_')[-1])
    
    # Get FAQ data
    faq = None
    faqs = db.get_faq()
    for f in faqs:
        if f[0] == faq_id:
            faq = f
            break
    
    if not faq:
        await event.edit("سوال مورد نظر یافت نشد.", buttons=[
            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
        ])
        return
    
    # Initialize edit state
    admin_state[event.sender_id] = {
        'state': 'editing_faq',
        'step': 'question',
        'faq_id': faq_id,
        'current_question': faq[1],
        'current_answer': faq[2]
    }
    
    await event.edit(f"ویرایش سوال با شناسه {faq_id}\n\nسوال فعلی: {faq[1]}\n\nلطفا سوال جدید را وارد کنید (برای حفظ سوال فعلی، همان را وارد کنید):")

async def confirm_delete_faq_handler(event):
    """Handle confirmation for deleting a FAQ."""
    if not await admin_required(event):
        return
    
    # Extract FAQ ID from callback data
    faq_id = int(event.data.decode().split('_')[-1])
    
    # Get FAQ data
    faq = None
    faqs = db.get_faq()
    for f in faqs:
        if f[0] == faq_id:
            faq = f
            break
    
    if not faq:
        await event.edit("سوال مورد نظر یافت نشد.", buttons=[
            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
        ])
        return
    
    await event.edit(f"آیا از حذف سوال «{faq[1]}» اطمینان دارید؟", buttons=[
        [Button.inline("✅ بله، حذف شود", data=f"delete_faq_confirmed_{faq_id}")],
        [Button.inline("❌ خیر، لغو شود", data="back_to_admin_menu")]
    ])

async def delete_faq_confirmed_handler(event):
    """Handle confirmed FAQ deletion."""
    if not await admin_required(event):
        return
    
    # Extract FAQ ID from callback data
    faq_id = int(event.data.decode().split('_')[-1])
    
    try:
        # Delete FAQ from database
        success = db.delete_faq(faq_id)
        
        if success:
            await event.edit("سوال متداول با موفقیت حذف شد.", buttons=[
                [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
            ])
        else:
            await event.edit("خطا در حذف سوال متداول.", buttons=[
                [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
            ])
        
    except Exception as e:
        logger.error(f"Error deleting FAQ: {e}")
        await event.edit("خطا در حذف سوال متداول.", buttons=[
            [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
        ])

async def process_faq_message(event):
    """Process messages from admin related to FAQ management."""
    sender = await event.get_sender()
    sender_id = sender.id
    
    # Check if admin is adding a FAQ
    if sender_id in admin_state and admin_state[sender_id].get('state') == 'adding_faq':
        current_step = admin_state[sender_id].get('step')
        
        if current_step == 'question':
            # Store FAQ question
            faq_question = event.text
            admin_state[sender_id]['question'] = faq_question
            admin_state[sender_id]['step'] = 'answer'
            
            await event.respond(f"سوال ثبت شد: {faq_question}\n\nلطفا پاسخ سوال را وارد کنید:")
            return True
        
        elif current_step == 'answer':
            # Store FAQ answer
            faq_answer = event.text
            
            # Get stored data
            question = admin_state[sender_id]['question']
            
            # Add FAQ to database
            try:
                faq_id = db.add_faq(question, faq_answer)
                
                # Success message
                await event.respond(f"سوال متداول جدید با موفقیت اضافه شد!\n\nشناسه: {faq_id}\nسوال: {question}\nپاسخ: {faq_answer}", buttons=[
                    [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                ])
                
                # Clear state
                clear_admin_state(sender_id)
                
            except Exception as e:
                logger.error(f"Error adding FAQ: {e}")
                await event.respond("خطا در ثبت سوال متداول. لطفا مجددا تلاش کنید.", buttons=[
                    [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                ])
            return True
    
    # Check if admin is editing a FAQ
    elif sender_id in admin_state and admin_state[sender_id].get('state') == 'editing_faq':
        current_step = admin_state[sender_id].get('step')
        faq_id = admin_state[sender_id].get('faq_id')
        
        if current_step == 'question':
            # Store FAQ question
            faq_question = event.text
            admin_state[sender_id]['question'] = faq_question
            admin_state[sender_id]['step'] = 'answer'
            
            await event.respond(f"سوال جدید: {faq_question}\n\nلطفا پاسخ جدید سوال را وارد کنید:")
            return True
        
        elif current_step == 'answer':
            # Store FAQ answer
            faq_answer = event.text
            
            # Get stored data
            question = admin_state[sender_id]['question']
            
            # Update FAQ in database
            try:
                success = db.update_faq(faq_id, question, faq_answer)
                
                if success:
                    # Success message
                    await event.respond(f"سوال متداول با موفقیت بروزرسانی شد!\n\nشناسه: {faq_id}\nسوال جدید: {question}\nپاسخ جدید: {faq_answer}", buttons=[
                        [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                    ])
                else:
                    await event.respond("سوال متداول مورد نظر یافت نشد یا خطایی در بروزرسانی رخ داد.", buttons=[
                        [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                    ])
                
                # Clear state
                clear_admin_state(sender_id)
                
            except Exception as e:
                logger.error(f"Error updating FAQ: {e}")
                await event.respond("خطا در بروزرسانی سوال متداول. لطفا مجددا تلاش کنید.", buttons=[
                    [Button.inline("🔙 بازگشت به منوی مدیریت", data="back_to_admin_menu")]
                ])
            return True
    
    return False

async def register_handlers(bot):
    """Register FAQ management handlers."""
    bot.add_event_handler(manage_faq_handler, events.CallbackQuery(pattern=r'admin_manage_faq'))
    bot.add_event_handler(add_faq_handler, events.CallbackQuery(pattern=r'add_faq'))
    bot.add_event_handler(edit_faq_handler, events.CallbackQuery(pattern=r'edit_faq'))
    bot.add_event_handler(delete_faq_handler, events.CallbackQuery(pattern=r'delete_faq'))
    bot.add_event_handler(edit_faq_id_handler, events.CallbackQuery(pattern=r'edit_faq_\d+'))
    bot.add_event_handler(confirm_delete_faq_handler, events.CallbackQuery(pattern=r'confirm_delete_faq_\d+'))
    bot.add_event_handler(delete_faq_confirmed_handler, events.CallbackQuery(pattern=r'delete_faq_confirmed_\d+'))
    
    logger.info("Admin FAQ handlers registered successfully") 