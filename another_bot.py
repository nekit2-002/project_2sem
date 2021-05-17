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
    repositories_to_listen = []

    logging.info(f'got new TG message from {username}, chat: {chat}')

    async def do_listen(array):
        await message.reply(parse_mode='Markdown',
                            text='Subscribing to required repositories')

        subscribers[username] = (chat, array)

    async def do_cancel(array):
        await message.reply(parse_mode='Markdown',
                            text='Cancelling required subscriptions')

        chats_and_repos = subscribers.get(username)
        current_repos = chats_and_repos[1]

        for phrase in range(len(array)):
            repo_to_cancel = re.findall(r'nekit2-002/\w*', array[phrase])
            print(array)
            print(current_repos)
            print(repo_to_cancel)

            for repo in range(len(current_repos)):
                if repo_to_cancel[0] == current_repos[repo]:
                    current_repos.pop(repo)
                    break

        changes = dedent(f'''
            One of the listened repositories has been deleted!
            The current list is:
            `{current_repos}`
            ''')

        await bot.send_message(chat, parse_mode='Markdown', text=changes)

    async def parser(txt):
        wanted_repos = re.findall(r'nekit2-002/\w*', txt)
        to_cancel = re.findall(r'cancel nekit2-002/\w*', txt)

        if wanted_repos == [] and to_cancel == []:
            greeting = dedent(f'''
            Hello, `{username}`! This bot is created to check new commits
            of certain repositories of *nekit2-002* user on Gitub.
            To listen to new commits type the name of the repository like this:
            *nekit2-002/name_of_the_repo*.

            To cancel the subscribtion type:
            *cancel nekit2-002/name_of_the_repo*.

            The current list of avaluable repositories is:
            `{repositories_full}`
            ''')

            await bot.send_message(chat, parse_mode='Markdown', text=greeting)

            return

        if username in subscribers:
            current_listen = subscribers.get(username)[1]

            if len(to_cancel) != 0:
                await do_cancel(to_cancel)
                return

            for i in range(len(wanted_repos)):
                current_listen.append(wanted_repos[i])

            changes = dedent(f'''
            The listened list of repositories has changed! The current list is:
            `{current_listen}`
            ''')

            await bot.send_message(chat, parse_mode='Markdown', text=changes)

        else:
            for repo in range(len(wanted_repos)):
                for match in range(len(repositories_full)):
                    if wanted_repos[repo] == repositories_full[match]:
                        repositories_to_listen.append(wanted_repos[repo])
                        await do_listen(repositories_to_listen)

                    elif len(to_cancel) != 0:
                        await do_cancel()

            show = dedent(f'''
            The current list of listened repositories is:
            `{repositories_to_listen}`!''')

            await bot.send_message(chat, parse_mode='Markdown', text=show)

    await parser(txt)


routes = web.RouteTableDef()


@routes.post('/github_events')
async def handle_github(request):
    data = await request.json()

    repo = data['repository']
    repo_name = repo['full_name']
    repo_url = repo['html_url']
    commit_msg = data['commits'][3]

    user = data['pusher']['name']
    branch = data['ref'].replace('refs/heads/', '')

    for user_in_sub in subscribers:
        chats_and_repos = subscribers.get(user_in_sub)
        chat = chats_and_repos[0]
        user_repos = chats_and_repos[1]

        message = dedent(f'''
            *{user}* has pushed a commit to `{branch}`.

            The commentary to the commit was:
            *{commit_msg}*

            Repository: [{repo_name}]({repo_url}).
        ''')

        for reposit in range(len(user_repos)):
            if repo_name == user_repos[reposit]:
                logging.info(message)

                await bot.send_message(chat, parse_mode='Markdown',
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
