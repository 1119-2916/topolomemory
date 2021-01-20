import discord
import sys
import os
import asyncio
import time
import sched
import cv2
import threading
from game_master import GameMaster

client = discord.Client()


def read_token():
    token = ''
    try:
        token_file = open('../key/token', 'r')
        token = token_file.read().replace('\n', '')
    except:
        print('failed to find or read token file. check your token file')
    finally:
        return token


def read_active_channel_id():
    channel_id = -1
    try:
        channel_id_file = open('../key/channel_id', 'r')
        channel_id = int(channel_id_file.read())
    except:
        print('failed to find or read channel id file. check your channel id file')
    finally:
        return channel_id


class MultiThreadGameMaster:

    def __init__(self, channel=None, gm=None):
        self.channel = channel
        self.gm = gm
        self.mutex_lock = asyncio.Lock()
        self.scheduled_task = None
        self.sleep_timer = 6

    def set_sleep_timer(self, time):
        self.sleep_timer = time

    def is_running(self):
        return self.scheduled_task is not None and (not self.scheduled_task.cancelled() or self.scheduled_task.done())

    def set_channel(self, channel):
        self.channel = channel

    def calc_index(self, str):
        alpha = str[1]
        num = str[0]
        if str[0].isalpha:
            alpha = str[0]
            num = str[1]
        ret = (int(num)-1) * 4
        if alpha == 'A' or alpha == 'a':
            return ret
        elif alpha == 'B' or alpha == 'b':
            return ret + 1
        elif alpha == 'C' or alpha == 'c':
            return ret + 2
        elif alpha == 'D' or alpha == 'd':
            return ret + 3
        else:
            return -1

    async def check_card_set(self, index1, index2):
        await self.mutex_lock.acquire()
        self.scheduled_task.cancel()
        # todo index encode
        if self.gm.check_card_set(self.calc_index(index1), self.calc_index(index2)):
            self.gm.erase_card_pair(self.calc_index(index1), self.calc_index(index2))
        cv2.imwrite('./gamepic.png', self.gm.generate_gameboard())
        await self.channel.send('', file=discord.File('./gamepic.png'))
        self.scheduled_task = asyncio.create_task(self.task())
        self.mutex_lock.release()

    async def task(self):
        try:
            # await asyncio.sleep(self.sleep_timer)
            time.sleep(self.sleep_timer)
            await self.mutex_lock.acquire()
            try:
                self.gm.random_card_play()
                cv2.imwrite('./gamepic.png', self.gm.generate_gameboard())
                await self.channel.send('', file=discord.File('./gamepic.png'))
                self.scheduled_task = asyncio.create_task(self.task())
            except asyncio.CancelledError:
                raise
            finally:
                self.mutex_lock.release()
        except asyncio.CancelledError:
            raise

    def reset(self):
        self.gm.game_reset()
        if self.scheduled_task is not None:
            self.scheduled_task.cancel()
            self.scheduled_task = None


# init
img_dir = '../image'
bot = GameMaster(os.path.join(img_dir, 'board.png'))
bot.load_image(img_dir)
mtgm = MultiThreadGameMaster(gm=bot)
token = read_token()
active_channel_id = read_active_channel_id()
lock = asyncio.Lock()


# bot を終了するコマンド
async def run_quit(message):
    await message.channel.send('botを終了しました。')
    sys.exit()


def get_cmd_list():
    return """
答え方: A2 C4 みたいに
始めるとき: -start
一旦やめる: -reset
botを落とす(再起動は出来ません): -bye
これを表示: -cmd か -help か --help か -h か -man か --man
"""


def check(str):
    if len(str) != 2:
        return False
    return str[0].isdigit() and str[1].isalpha() or str[1].isdigit() and str[0].isalpha()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.channel.id != active_channel_id:
        return

    await lock.acquire()
    global mtgm
    if client.user in message.mentions:
        # コマンドのパース
        print(message.content)
        cmd_list = list(filter(lambda x: len(x) > 0, message.content.split(' ')))
        if len(cmd_list) > 1:
            cmd = cmd_list[1]
            print('receive : ' + cmd)
            if cmd == '-echo':
                response = bot.echo(message.content)
                await message.channel.send(response)
            elif cmd == '-kick();':
                print('log : kick call')
                await message.channel.send('ヒィンｗ')
            elif cmd == '-kick()' or cmd == '-kick' or cmd == '-kick;':
                print('log : failed kick call')
                await message.channel.send('申し訳ないのですが、 kick(); は kick(); の形式以外認められません…')
            elif cmd.startswith('-kick(') and cmd.endsWith(');'):
                print('log : failed kick call')
                await message.channel.send('error: too many arguments to function ‘void kick()’')
            elif cmd == '-bye':
                print('log : bye call')
                await run_quit(message)
            elif cmd == '-cmd' or cmd == '-man' or cmd == '--man' or cmd == '-help' or cmd == '--help' or cmd == '-h':
                print('log : cmd call')
                response = get_cmd_list()
                await message.channel.send(response)
            elif cmd == '-reset':
                bot.game_reset()
                mtgm.reset()
                await message.channel.send('hard reset.')
            elif cmd == '-pro':
                print('log : pro call')
                await message.channel.send('はいプロ 世界一トポロメモリーが上手 トポロメモリー界のtourist トポロメモリーするために生まれてきた者')
            elif cmd == '-start':
                print('log : start call')
                if not mtgm.is_running():
                    mtgm.reset()
                    mtgm.set_channel(message.channel)
                    await message.channel.send('ゲームを開始します')
                    await mtgm.task()
                else:
                    await message.channel.send('ゲーム中です')
            elif cmd[0] == '-':
                print('log : -XXX command call')
                print(cmd[1:len(cmd)])

    elif mtgm.is_running():  # 答えの確認
        print('check answer : ' + message.content)
        cmd_list = list(filter(lambda x: len(x) > 0, message.content.split(' ')))
        if len(cmd_list) == 2:
            if check(cmd_list[0]) and check(cmd_list[1]):
                await mtgm.check_card_set(cmd_list[0], cmd_list[1])

    lock.release()


client.run(token)
