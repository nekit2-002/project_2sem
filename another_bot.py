#!/usr/bin/env python3
import aiogram as telegram
import asyncio
import logging
import os

from aiohttp import web
from textwrap import dedent

TG_TOKEN = os.environ['TG_TOKEN']
PORT = os.environ.get('PORT', 8080)

bot = telegram.Bot(token=TG_TOKEN)
dispatcher = telegram.Dispatcher(bot)

subscribers = {}

repositories_full = ['nekit2-002/dummy', 'nekit2-002/dummy2']


@dispatcher.message_handler()
async def handle_message(message):
    chat = message.chat.id
    username = message['from'].username

    logging.info(f'got new TG message from {username}, chat: {chat}')

    async def do_listen():
        await message.reply(parse_mode='Markdown',
                            text='Subscribing to all repositories')

        subscribers[username] = (chat, repositories_full)

    async def listen_to():
        repositories_to_listen = []

        await bot.send_message(chat, parse_mode='Markdown', text='''
        Choose the repositories you want to be informed about!
        ''')

        await bot.send_message(chat, parse_mode='Markdown',
                               text=f'{repositories_full}')

        for index in range(len(repositories_full)):

            @dispatcher.message_handler()
            async def handle_name(message):
                if message.text == repositories_full[index]:
                    await bot.send_message(chat, parse_mode='Markdown', text=f'''
                    You have chosen the repository {repositories_full[index]}
                    to listen to.
                    ''')

                    repositories_to_listen.append(f'''
                    {repositories_full[index]}''')

                    subscribers[username] = (chat, repositories_to_listen)

        await handle_name(message)

    async def do_cancel():
        await message.reply(parse_mode='Markdown',
                            text='Cancelling all subscriptions')

        subscribers.pop(username, None)

    async def do_error():
        commands = ', '.join(list(actions.keys()))

        reply = dedent(f'''
            *Unknown command.*
            Available commands: {commands}.
        ''')

        await message.reply(parse_mode='Markdown', text=reply)

    actions = {
        'listen': do_listen,
        "cancel": do_cancel,
        'listen to': listen_to
    }
    action = actions.get(message.text, do_error)
    await action()


routes = web.RouteTableDef()


@routes.post('/github_events')
async def handle_github(request):
    data = await request.json()
    chats_and_repos = list(subscribers.values())
    user_chat, wanted_repos = chats_and_repos[0], chats_and_repos[1]

    repo = data['repository']
    repo_name = repo['full_name']
    repo_url = repo['html_url']

    user = data['pusher']['name']
    branch = data['ref'].replace('refs/heads/', '')

    for commit in data['commits']:

        message = dedent(f'''
            *{user}* has pushed a commit to `{branch}`.
            Repository: [{repo_name}]({repo_url}).
        ''')

        logging.info(message)

        for user in subscribers:
            for repository in range(len(wanted_repos)):
                if repo_name == wanted_repos[repository]:
                    await bot.send_message(user_chat, parse_mode='Markdown',
                                           text=message)

    # Reply with 200 OK
    return web.Response()


@routes.get('/')
async def index(request):
    return web.Response(text='Up and running')


async def run_server():
    app = web.Application()
    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host='0.0.0.0', port=PORT)
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
