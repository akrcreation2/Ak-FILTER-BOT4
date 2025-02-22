import logging
import logging.config
import asyncio
import os
import sys
from datetime import date, datetime

import pytz
import tgcrypto
from aiohttp import web as webserver
from pyrogram import Client, __version__, types
from pyrogram.raw.all import layer
from pyrogram import utils as pyroutils

# Get logging configurations
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)

# Prevent the bot from stopping after 1 week
logging.getLogger("asyncio").setLevel(logging.CRITICAL - 1)

# Adjust peer id invalid fix
pyroutils.MIN_CHAT_ID = -999999999999
pyroutils.MIN_CHANNEL_ID = -100999999999999

# Import your modules and configurations
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_STR, LOG_CHANNEL
from utils import temp
from Script import script
from plugins.webcode import bot_run

# Get PORT_CODE from environment variables, default to "8080" if not set
PORT_CODE = os.environ.get("PORT", "8080")


class Bot(Client):
    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self, **kwargs):
        # Get banned users and chats from database
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats

        # Start the client and ensure indexes
        await super().start()
        await Media.ensure_indexes()

        # Get bot information and update temp variables
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username

        # Log bot startup and send messages to LOG_CHANNEL
        logging.info(f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")
        logging.info(LOG_STR)
        await self.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT)
        print("mntg4u</>")

        tz = pytz.timezone('Asia/Kolkata')
        today = date.today()
        now = datetime.now(tz)
        time_str = now.strftime("%H:%M:%S %p")
        await self.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_GC_TXT.format(today, time_str))

        # Setup the webserver for bot_run
        runner = webserver.AppRunner(await bot_run())
        await runner.setup()
        bind_address = "0.0.0.0"
        await webserver.TCPSite(runner, bind_address, PORT_CODE).start()

        # Schedule auto restart every 6 hours
        asyncio.create_task(self.auto_restart())

    async def auto_restart(self):
        while True:
            await asyncio.sleep(21600)  # Sleep for 6 hours (21600 seconds)
            logging.info("Restarting bot...")
            await self.send_message(chat_id=LOG_CHANNEL, text="Restarting bot after 6 hours...")
            os.execv(sys.executable, [sys.executable] + sys.argv)

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")

    async def iter_messages(
        self,
        chat_id: int or str,
        limit: int,
        offset: int = 0,
    ) -> types.AsyncGenerator[types.Message, None]:
        """
        Iterate through a chat sequentially.
        """
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current + new_diff + 1)))
            for message in messages:
                yield message
                current += 1

# Create an instance of the bot and run it
app = Bot()
app.run()
