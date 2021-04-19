#!/usr/bin/env python3
import aiogram as telegram
import asyncio
import logging
import os

from aiohttp import web

# * Часть отвечающая за бота

TG_TOKEN = os.environ['TG_TOKEN']
#TG_TOKEN = '1644508993:AAHywAyEf6dPbbVM57Hz0xsimAA8rfG5zWg'

bot = telegram.Bot(token=TG_TOKEN)
dispatcher = telegram.Dispatcher(bot)
subscribers = dict()


@dispatcher.message_handler()
async def handle_message(message):
    chat_id = message.chat.id
    username = message['from'].username

    for key in subscribers:
            print(key)

    async def printing():
        a = 10
        await bot.send_message(chat_id, parse_mode='Markdown', text=f'{a}')


    async def handle_unregister():

        del subscribers[f'{username}']
        print(subscribers)

        await message.reply(f'User {username} has succesfully unsubscribed')

        return subscribers

    async def handle():
        if username in subscribers:
            await message.reply(f'Hi again, {username}!')
            print((subscribers))
            await printing()

        else:
            subscribers[f'{username}'] = printing()
            await message.reply(f'Hi, {username}! You have successfully subscribed')

        return

    if message.text == 'unsubscribe':
        await handle_unregister()
    else:
        await handle()

    # i = 0
    # while True:
    #     i += 1
    #     await bot.send_message(chat_id, parse_mode='Markdown', text=f'''
    #     heartbeat `{i}`
    #     ''')
    #     await asyncio.sleep(5)

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

