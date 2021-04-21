#!/usr/bin/env python3
import aiogram as telegram
import asyncio
import logging
import os

from aiohttp import web

# * Часть отвечающая за бота

TG_TOKEN = os.environ['TG_TOKEN']

bot = telegram.Bot(token=TG_TOKEN)
dispatcher = telegram.Dispatcher(bot)

lock = asyncio.Lock()
subscribers = dict()


@dispatcher.message_handler()
async def handle_message(message):
    chat_id = message.chat.id
    username = message['from'].username

    async def spam():
        i = 0
        while True:
            i += 1
            await bot.send_message(chat_id, parse_mode='Markdown', text=f'''
            heartbeat `{i}`
            ''')
            await asyncio.sleep(2)

    for key in subscribers:
            print(key)


    if username in subscribers:
        async with lock:
            if message.text == 'unsubscribe':
                subscribers.pop(username).cancel()
                print(subscribers)
                await bot.send_message(chat_id, parse_mode='Markdown', text=f'User `{username}` unsubscribed')
                return

        await message.reply(f'Hi again, {username}!')

        return  # the user is already subscribed

    async with lock:
        subscribers[username] = asyncio.create_task(spam())
        await message.reply(f'Hi, {username}! You have successfully subscribed')


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

