#!/usr/bin/env python3
import aiogram as telegram
import asyncio
import logging
#import os

from aiohttp import web

# * Часть отвечающая за бота

#TG_TOKEN = os.environ.get('TG_TOKEN')
TG_TOKEN = '1644508993:AAHywAyEf6dPbbVM57Hz0xsimAA8rfG5zWg'

bot = telegram.Bot(token=TG_TOKEN)
dispatcher = telegram.Dispatcher(bot)


@dispatcher.message_handler()
async def send_welcome(message):
    await message.reply('Hi! You have successfully subscribed')


    async def post_updates(chat_id):
        logging.info('starting new updater')

        i = 0
        while True:
            i += 1
            await bot.send_message(chat_id, parse_mode='Markdown', text=f'''
            heartbeat `{i}`
        ''')

            await asyncio.sleep(5)
    await asyncio.create_task(post_updates(message.chat.id))

# * Часть связанная с сервером

routes = web.RouteTableDef()

@routes.post('/github_events')
async def handle_github(request):
    logging.info('received new event')

    # Reply with 200 OK
    return web.Response()


async def run_server():
    app = web.Application()
    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner)
    await site.start()

    # Sleep forever
    await asyncio.Event().wait()


async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting server...')

    await asyncio.gather(
        dispatcher.start_polling(),
        run_server(),
    )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

