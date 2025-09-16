import os
from datetime import datetime
from pytz import timezone
from pyrogram import Client, filters
from aiohttp import web
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN, LOG_CHANNEL, DEFAULT_THUMB  # 👈 added DEFAULT_THUMB
from TechifyBots import db  # 👈 import db functions

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
        print("Bot stopped.")

bot = Bot()

# -------------------- NEW HANDLERS --------------------

# /setthumb → user sends a photo
@bot.on_message(filters.command("setthumb") & filters.reply)
async def set_thumbnail_handler(client, message):
    if not message.reply_to_message.photo:
        return await message.reply("Reply to a photo with /setthumb")
    file_id = message.reply_to_message.photo.file_id
    await db.set_thumbnail(message.from_user.id, file_id)
    await message.reply("✅ Thumbnail saved successfully!")

# /delthumb → delete thumb
@bot.on_message(filters.command("delthumb"))
async def del_thumbnail_handler(client, message):
    await db.delete_thumbnail(message.from_user.id)
    await message.reply("🗑️ Thumbnail deleted!")

# auto apply thumbnail when PDF is uploaded
@bot.on_message(filters.document.mime_type("application/pdf"))
async def pdf_handler(client, message):
    user_id = message.from_user.id
    thumb = await db.get_thumbnail(user_id)

    # 👇 if user has no custom thumb, fall back to DEFAULT_THUMB
    if not thumb and DEFAULT_THUMB:
        thumb = DEFAULT_THUMB

    if thumb:
        await message.reply_document(
            document=message.document.file_id,
            thumb=thumb,
            caption="Here’s your PDF with thumbnail ✅"
        )
    else:
        await message.reply_document(
            document=message.document.file_id,
            caption="Here’s your PDF ✅"
        )

# -------------------- RUN --------------------
bot.run()
