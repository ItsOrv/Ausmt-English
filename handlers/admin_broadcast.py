from telethon import events, Button
from handlers.admin_utils import admin_state, db, logger, is_admin, admin_required, edit_or_respond, clear_admin_state
from utils.keyboards import KeyboardManager

async def broadcast_message_handler(event):
    """Handler for sending broadcast messages."""
    if not await admin_required(event):
        return
    
    sender_id = (await event.get_sender()).id
    admin_state[sender_id] = {'state': 'awaiting_broadcast_message'}
    
    broadcast_message = """لطفا پیام خود را برای ارسال به همه کاربران ربات وارد کنید:

برای لغو عملیات، دستور /cancel را ارسال کنید."""
    
    try:
        await event.edit(broadcast_message)
    except Exception as e:
        if "MessageNotModifiedError" in str(e):
            # Message already shows the same content
            await event.answer("لطفا پیام خود را برای ارسال گروهی وارد کنید.", alert=True)
        else:
            logger.error(f"Error editing message in broadcast_message_handler: {e}")
            # Try to delete and send a new message
            try:
                await event.delete()
                await event.respond(broadcast_message)
            except Exception as e2:
                logger.error(f"Error handling broadcast message: {e2}")
                await event.respond(broadcast_message)

async def confirm_broadcast_handler(event):
    """Handler for confirming broadcast message."""
    if not await admin_required(event):
        return
    
    sender_id = (await event.get_sender()).id
    
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
                await event.client.send_message(user_id[0], f"**پیام از طرف انجمن زبان**:\n\n{broadcast_message}")
                successful_sends += 1
            except Exception as e:
                logger.error(f"Error sending broadcast to user {user_id[0]}: {e}")
        
        # Clear admin state
        clear_admin_state(sender_id)
        
        await event.client.send_message(sender_id, f"پیام گروهی با موفقیت به {successful_sends} کاربر از {len(users)} کاربر ارسال شد.",
                              buttons=KeyboardManager.back_to_main())

async def cancel_broadcast_handler(event):
    """Handler for cancelling broadcast message."""
    if not await admin_required(event):
        return
    
    sender_id = (await event.get_sender()).id
    
    # Clear admin state
    clear_admin_state(sender_id)
    
    await event.edit("ارسال پیام گروهی لغو شد.", buttons=KeyboardManager.back_to_main())

async def admin_message_handler(event):
    """Handler for processing admin broadcast messages."""
    sender = await event.get_sender()
    sender_id = sender.id
    
    if not await is_admin(event):
        return
    
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
            [Button.inline("✅ بله، ارسال شود", data="confirm_broadcast")],
            [Button.inline("❌ خیر، لغو شود", data="cancel_broadcast")]
        ])
        return True
    return False

async def register_handlers(bot):
    """Register broadcast handlers."""
    bot.add_event_handler(broadcast_message_handler, events.CallbackQuery(pattern=r'admin_broadcast'))
    bot.add_event_handler(confirm_broadcast_handler, events.CallbackQuery(pattern=r'confirm_broadcast'))
    bot.add_event_handler(cancel_broadcast_handler, events.CallbackQuery(pattern=r'cancel_broadcast'))
    
    logger.info("Admin broadcast handlers registered successfully") 