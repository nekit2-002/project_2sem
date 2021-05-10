#!/usr/bin/env python3
import aiogram as telegram
import asyncio
import logging
import os
import re

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
    txt = message.text

    logging.info(f'got new TG message from {username}, chat: {chat}')

    async def do_listen(array):
        await message.reply(parse_mode='Markdown',
                            text='Subscribing to required repositories')

        subscribers[username] = (chat, array)

    async def do_cancel():
        await message.reply(parse_mode='Markdown',
                            text='Cancelling all subscriptions')

        subscribers.pop(username, None)

    async def parser(txt):
        wanted_repos = re.findall(r'nekit2-002/\w*', txt)
        repositories_to_listen = []

        for repo in range(len(wanted_repos)):
            for match in range(len(repositories_full)):
                if wanted_repos[repo] == repositories_full[match]:
                    repositories_to_listen.append(wanted_repos[repo])
                    await do_listen(repositories_to_listen)

        await bot.send_message(chat, parse_mode='Markdown', text=f'''
        The current list of listened repositories is
        `{repositories_to_listen}`!
        ''')

    await parser(txt)


routes = web.RouteTableDef()


@routes.post('/github_events')
async def handle_github(request):
    data = await request.json()

    repo = data['repository']
    repo_name = repo['full_name']
    repo_url = repo['html_url']

    user = data['pusher']['name']
    branch = data['ref'].replace('refs/heads/', '')

    for commit in data['commits']:
        # commit_hash = commit['id'][:8]
        # commit_url = commit['url']

        message = dedent(f'''
            *{user}* has pushed a commit to `{branch}`.
            Repository: [{repo_name}]({repo_url}).
        ''')
        logging.info(message)

        for chat in subscribers.values():
            await bot.send_message(chat, parse_mode='Markdown', text=message)

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
