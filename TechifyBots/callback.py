from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import BadRequest
from Script import text
from config import ADMIN
from TechifyBots.db import tb   # 👈 import DB instance

@Client.on_callback_query()
async def callback_query_handler(client, query: CallbackQuery):
    try:
        if query.data == "start":
            await query.message.edit_caption(
                caption=text.START.format(query.from_user.mention),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("ℹ️ 𝖠𝖻𝗈𝗎𝗍", callback_data="about"),
                     InlineKeyboardButton("📚 𝖧𝖾𝗅𝗉", callback_data="help")],
                    [InlineKeyboardButton("👨‍💻 𝖣𝖾𝗏𝖾𝗅𝗈𝗉𝖾𝗋 👨‍💻", user_id=int(ADMIN))]
                ])
            )

        elif query.data == "help":
            await query.message.edit_caption(
                caption=text.HELP,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 𝖴𝗉𝖽𝖺𝗍𝖾𝗌", url="https://t.me/network_of_kingdom"),
                     InlineKeyboardButton("💬 𝖲𝗎𝗉𝗉𝗈𝗋𝗍", url="https://t.me/shadow_core_chat")],
                    [InlineKeyboardButton("↩️ 𝖡𝖺𝖼𝗄", callback_data="start"),
                     InlineKeyboardButton("❌ 𝖢𝗅𝗈𝗌𝖾", callback_data="close")]
                ])
            )

        elif query.data == "about":
            await query.message.edit_caption(
                caption=text.ABOUT,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("👨‍💻 𝖣𝖾𝗏𝖾𝗅𝗈𝗉𝖾𝗋 👨‍💻", user_id=int(ADMIN))],
                    [InlineKeyboardButton("↩️ 𝖡𝖺𝖼𝗄", callback_data="start"),
                     InlineKeyboardButton("❌ 𝖢𝗅𝗈𝗌𝖾", callback_data="close")]
                ])
            )

        elif query.data == "close":
            await query.message.delete()
            
    except BadRequest:
        # Message not modified (same content)
        await query.answer()
    except Exception as e:
        print(f"Error in callback handler: {e}")
        await query.answer("❌ An error occurred!", show_alert=True)

# ---------------- THUMBNAIL COMMANDS ---------------- #

# /setthumb → user must reply to a photo
@Client.on_message(filters.command("setthumb") & filters.reply)
async def set_thumbnail_handler(client, message):
    try:
        if not message.reply_to_message or not message.reply_to_message.photo:
            return await message.reply("⚠️ Reply to a photo with /setthumb to set your thumbnail.")
        
        file_id = message.reply_to_message.photo.file_id
        success = await tb.set_thumbnail(message.from_user.id, file_id)
        
        if success:
            await message.reply("✅ Thumbnail saved successfully!\n\nIt will be automatically applied to your PDF files.")
        else:
            await message.reply("❌ Failed to save thumbnail. Please try again.")
            
    except Exception as e:
        print(f"Error in set_thumbnail_handler: {e}")
        await message.reply("❌ An error occurred while setting thumbnail.")

# /delthumb → delete thumbnail
@Client.on_message(filters.command("delthumb"))
async def del_thumbnail_handler(client, message):
    try:
        success = await tb.delete_thumbnail(message.from_user.id)
        
        if success:
            await message.reply("🗑️ Thumbnail deleted!")
        else:
            await message.reply("❌ No thumbnail found to delete.")
            
    except Exception as e:
        print(f"Error in del_thumbnail_handler: {e}")
        await message.reply("❌ An error occurred while deleting thumbnail.")

# /showthumb → show current thumbnail
@Client.on_message(filters.command("showthumb"))
async def show_thumbnail_handler(client, message):
    try:
        thumb = await tb.get_thumbnail(message.from_user.id)
        if thumb:
            await message.reply_photo(
                thumb, 
                caption="📸 Your current thumbnail\n\nThis will be automatically applied to your PDF files."
            )
        else:
            await message.reply("❌ You don't have any thumbnail set.\n\nUse /setthumb by replying to a photo to set one.")
            
    except Exception as e:
        print(f"Error in show_thumbnail_handler: {e}")
        await message.reply("❌ An error occurred while fetching your thumbnail.")

# /thumbhelp → show thumbnail help
@Client.on_message(filters.command("thumbhelp"))
async def thumb_help_handler(client, message):
    help_text = """
📚 **Thumbnail Commands Help:**

**/setthumb** - Reply to a photo to set it as your custom thumbnail
**/delthumb** - Delete your current thumbnail  
**/showthumb** - View your current thumbnail
**/thumbhelp** - Show this help message

✨ **How it works:**
1. Send a photo to the bot
2. Reply to that photo with `/setthumb`
3. Upload PDF files - your thumbnail will be applied automatically!
"""
    await message.reply(help_text)