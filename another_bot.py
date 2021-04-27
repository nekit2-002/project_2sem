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
repositories_to_listen = []


@dispatcher.message_handler()
async def handle_message(message):
    chat = message.chat.id
    username = message['from'].username

    logging.info(f'got new TG message from {username}, chat: {chat}')

    async def do_listen():
        await message.reply(parse_mode='Markdown',
                            text='Subscribing to all repositories')

        repositories_to_listen = repositories_full

        subscribers[username] = (chat, repositories_to_listen)

    async def listen_to():
        await bot.send_message(chat, parse_mode='Markdown', text='''
        Choose the repository you want to be informed about!
        ''')
        await bot.send_message(chat, parse_mode='Markdown',
                               text=f'{repositories_full}')

        response = message.text

        for repository in range(len(repositories_full)):
            if response == repository:
                await bot.send_message(chat, parse_mode='Markdown', text=f'''
                You have chosen the repository {repository} to listen to.
                ''')

                repositories_to_listen.append(f'{repository}')

                subscribers[username] = (chat, repositories_to_listen)

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
        'listen_to': listen_to
    }
    action = actions.get(message.text, do_error)
    await action()


routes = web.RouteTableDef()
keys = subscribers.keys()
values = list(subscribers.values())


@routes.post('/github_events')
async def handle_github(request):
    data = await request.json()

    repo = data['repository']
    repo_name = repo['full_name']
    repo_url = repo['html_url']

    user = data['pusher']['name']
    branch = data['ref'].replace('refs/heads/', '')

    for commit in data['commits']:
        commit_hash = commit['id'][:8]
        commit_url = commit['url']

        message = dedent(f'''
            *{user}* has pushed [{commit_hash}]({commit_url}) to `{branch}`.
            Repository: [{repo_name}]({repo_url}).
        ''')

        logging.info(message)
        for i in range(len(subscribers)):
            for chat in values[i][0]:
                for name in range(len(keys)):
                    for rep in range(len(repositories_to_listen)):
                        if repo_name == rep:
                            await bot.send_message(chat,
                                                   parse_mode='Markdown',
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
