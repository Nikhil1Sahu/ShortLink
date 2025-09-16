from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from Script import text
from config import ADMIN
from TechifyBots.db import tb   # 👈 import DB instance

@Client.on_callback_query()
async def callback_query_handler(client, query: CallbackQuery):
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

# ---------------- THUMBNAIL COMMANDS ---------------- #

# /setthumb → user must reply to a photo
@Client.on_message(filters.command("setthumb") & filters.reply)
async def set_thumbnail_handler(client, message):
    if not message.reply_to_message.photo:
        return await message.reply("⚠️ Reply to a photo with /setthumb to set your thumbnail.")
    file_id = message.reply_to_message.photo.file_id
    await tb.set_thumbnail(message.from_user.id, file_id)
    await message.reply("✅ Thumbnail saved successfully!")

# /delthumb → delete thumbnail
@Client.on_message(filters.command("delthumb"))
async def del_thumbnail_handler(client, message):
    await tb.delete_thumbnail(message.from_user.id)
    await message.reply("🗑️ Thumbnail deleted!")

# /showthumb → show current thumbnail
@Client.on_message(filters.command("showthumb"))
async def show_thumbnail_handler(client, message):
    thumb = await tb.get_thumbnail(message.from_user.id)
    if thumb:
        await message.reply_photo(thumb, caption="📌 Your current thumbnail")
    else:
        await message.reply("❌ You don’t have any thumbnail set.")
