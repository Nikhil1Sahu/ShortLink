import os
from datetime import datetime
from pytz import timezone
from pyrogram import Client, filters
from aiohttp import web
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN, LOG_CHANNEL, DEFAULT_THUMB
from TechifyBots.db import tb  # 👈 FIXED: Import the class instance, not the module

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route(request):
    return web.Response(text="<h3 align='center'><b>I am Alive</b></h3>", content_type='text/html')

async def web_server():
    app = web.Application(client_max_size=30_000_000)
    app.add_routes(routes)
    return app

class Bot(Client):
    def __init__(self):
        super().__init__(
            "techifybots",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="TechifyBots"),
            workers=200,
            sleep_threshold=15
        )

    async def start(self):
        app = web.AppRunner(await web_server())
        await app.setup()
        try:
            await web.TCPSite(app, "0.0.0.0", int(os.getenv("PORT", 8080))).start()
            print("Web server started.")
        except Exception as e:
            print(f"Web server error: {e}")

        await super().start()
        me = await self.get_me()
        print(f"Bot Started as {me.first_name}")

        if isinstance(ADMIN, int):
            try:
                await self.send_message(ADMIN, f"**{me.first_name} is started...**")
            except Exception as e:
                print(f"Error sending message to admin: {e}")
        if LOG_CHANNEL:
            try:
                now = datetime.now(timezone("Asia/Kolkata"))
                msg = (
                    f"**{me.mention} is restarted!**\n\n"
                    f"📅 Date : `{now.strftime('%d %B, %Y')}`\n"
                    f"⏰ Time : `{now.strftime('%I:%M:%S %p')}`\n"
                    f"🌐 Timezone : `Asia/Kolkata`"
                )
                await self.send_message(LOG_CHANNEL, msg)
            except Exception as e:
                print(f"Error sending to LOG_CHANNEL: {e}")

    async def stop(self, *args):
        await super().stop()
        print(f"{self.me.first_name} Bot stopped.")

bot = Bot()

# -------------------- NEW HANDLERS --------------------

# /setthumb → user sends a photo
@bot.on_message(filters.command("setthumb") & filters.reply)
async def set_thumbnail_handler(client, message):
    try:
        if not message.reply_to_message or not message.reply_to_message.photo:
            return await message.reply("❌ Please reply to a photo with /setthumb")
        
        file_id = message.reply_to_message.photo.file_id
        user_id = message.from_user.id
        
        # Save thumbnail to database
        success = await tb.set_thumbnail(user_id, file_id)  # 👈 FIXED: Changed db to tb
        
        if success:
            await message.reply("✅ Thumbnail saved successfully!\n\nIt will be automatically applied to your PDF files.")
        else:
            await message.reply("❌ Failed to save thumbnail. Please try again.")
            
    except Exception as e:
        print(f"Error in set_thumbnail_handler: {e}")
        await message.reply("❌ An error occurred while setting thumbnail.")

# /delthumb → delete thumb
@bot.on_message(filters.command("delthumb"))
async def del_thumbnail_handler(client, message):
    try:
        user_id = message.from_user.id
        success = await tb.delete_thumbnail(user_id)  # 👈 FIXED: Changed db to tb
        
        if success:
            await message.reply("🗑️ Thumbnail deleted!")
        else:
            await message.reply("❌ No thumbnail found to delete.")
            
    except Exception as e:
        print(f"Error in del_thumbnail_handler: {e}")
        await message.reply("❌ An error occurred while deleting thumbnail.")

# /showthumb → show current thumbnail
@bot.on_message(filters.command("showthumb"))
async def show_thumbnail_handler(client, message):
    try:
        thumb = await tb.get_thumbnail(message.from_user.id)  # 👈 FIXED: Changed db to tb
        if thumb:
            await message.reply_photo(thumb, caption="📸 Your current thumbnail\n\nThis will be applied to your PDF files.")
        else:
            await message.reply("❌ You don't have any thumbnail set.\n\nUse /setthumb by replying to a photo.")
    except Exception as e:
        print(f"Error in show_thumbnail_handler: {e}")
        await message.reply("❌ Could not retrieve thumbnail.")

# auto apply thumbnail when PDF is uploaded
@bot.on_message(filters.document)
async def pdf_handler(client, message):
    try:
        # only process PDFs
        if message.document and message.document.mime_type == "application/pdf":
            user_id = message.from_user.id
            thumb = await tb.get_thumbnail(user_id)  # 👈 FIXED: Changed db to tb
            
            # Download the document first
            download_msg = await message.reply("📥 Downloading your PDF...")
            doc_path = await message.download()
            
            # Edit message to show processing
            await download_msg.edit_text("🔄 Applying thumbnail...")
            
            if thumb:
                await message.reply_document(
                    document=doc_path,
                    thumb=thumb,
                    caption="📄 Here's your PDF with custom thumbnail ✅"
                )
            else:
                await message.reply_document(
                    document=doc_path,
                    caption="📄 Here's your PDF ✅"
                )
            
            # Clean up downloaded file and status message
            import os
            os.remove(doc_path)
            await download_msg.delete()
            
    except Exception as e:
        print(f"Error in pdf_handler: {e}")
        # Send detailed error to yourself and generic message to user
        error_msg = f"❌ PDF Error: {str(e)}"
        if len(error_msg) > 4000:  # Telegram message limit
            error_msg = error_msg[:4000] + "..."
        
        try:
            await message.reply("❌ An error occurred while processing your PDF. Please try again.")
            # Send detailed error to admin or log channel
            if LOG_CHANNEL:
                await client.send_message(LOG_CHANNEL, f"PDF Error for user {message.from_user.id}: {e}")
        except:
            pass

# -------------------- RUN --------------------
bot.run()