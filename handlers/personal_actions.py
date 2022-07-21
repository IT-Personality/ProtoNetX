import string
from dispatcher import dp
import config
from aiogram import Bot,types,executor,Dispatcher
from bot import BotDB
import string
from dbx import Database
import datetime
import json
import re
import requests
from bs4 import BeautifulSoup as BS
import time
from main_news import check_news_update
from aiogram.utils.markdown import hbold, hlink
from aiogram.dispatcher.filters import Text

dbx = Database('database.db')

@dp.message_handler(commands = ["start", "help"])
async def start(message: types.Message):
    await message.answer("Привет!\n Я - бот который который делает полезные вещи! 🙂")

@dp.message_handler(commands=['id_users'])
async def id(message: types.Message):
    await message.reply(f"Ваш ID: {message.from_user.id}")

@dp.message_handler(commands = ["well_USD"])
async def start(message: types.Message):
    url = 'https://www.currency.me.uk/convert/usd/rub'
    r = requests.get(url)
    soup = BS(r.text, 'lxml')
    result = soup.find("span", { "class" : "mini ccyrate" }).text
    res = (result)
    await message.reply(res)

@dp.message_handler(commands = ["well_EUR"])
async def start(message: types.Message):
    url = 'https://finance.rambler.ru/currencies/EUR/'
    r = requests.get(url)
    soup = BS(r.text, 'lxml')
    result = soup.find("div", { "class" : "finance-currency-plate__currency" }).text
    res = f"1 EUR 🔻 {result}RUB"
    await message.reply(res)

@dp.message_handler(commands=['id_chat'])
async def chat(message: types.Message):
    await message.reply(f"ID чата: {message.chat.id}")

@dp.message_handler(commands=["ban"], commands_prefix="/")
async def stabs(message: types.Message):
    if str(message.from_user.id) == config.ADMIN_ID:
        if not message.reply_to_message:
            await message.reply("Команда должна быть ответом на сообщение!")
            return
        await message.bot.delete_message(config.CHAT_ID, message.message_id)
        await message.bot.kick_chat_member(config.CHAT_ID, user_id=message.reply_to_message.from_user.id)
        await message.answer("ProtoNetX успешно забанил указанного пользователя!\n Хе-хе)")
    else:
        await message.reply("Отправлять команду бана может только Админ!")

@dp.message_handler(commands="all_news")
async def get_all_news(message: types.Message):
    if str(message.from_user.id) == config.ADMIN_ID:
        with open("news.json") as file:
            news_dict = json.load(file)

        for k, v in sorted(news_dict.items()):
            news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
                f"{hlink(v['article_title'], v['article_url'])}"
            await message.answer(news)

@dp.message_handler(commands="last_fave_news")
async def get_last_five_news(message: types.Message):
    if str(message.from_user.id) == config.ADMIN_ID:
        with open("news.json") as file:
            news_dict = json.load(file)

        for k, v in sorted(news_dict.items())[-5:]:
            news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
                f"{hlink(v['article_title'], v['article_url'])}"

            await message.answer(news)

@dp.message_handler(commands="fresh_news")
async def get_fresh_news(message: types.Message):
    if str(message.from_user.id) == config.ADMIN_ID:
        fresh_news = check_news_update()

        if len(fresh_news) >= 1:
            for k, v in sorted(fresh_news.items()):
                news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
                    f"{hlink(v['article_title'], v['article_url'])}"

                await message.answer(news)
        else:
            await message.answer("Пока нет свежих новостей...")

@dp.message_handler(commands = ("spent", "earned", "s", "e"))
async def start(message: types.Message):
    cmd_variants = (('/spent', '/s'), ('/earned', '/e'))
    operation = '-' if message.text.startswith(cmd_variants[0]) else '+'

    value = message.text
    for i in cmd_variants:
        for j in i:
            value = value.replace(j, '').strip()

    if(len(value)):
        x = re.findall(r"\d+(?:.\d+)?", value)
        if(len(x)):
            value = float(x[0].replace(',', '.'))

            BotDB.add_record(message.from_user.id, operation, value)

            if(operation == '-'):
                await message.reply("✅ Запись о <u><b>расходе</b></u> успешно внесена!")
            else:
                await message.reply("✅ Запись о <u><b>доходе</b></u> успешно внесена!")
        else:
            await message.reply("Не удалось определить сумму!")
    else:
        await message.reply("Не введена сумма!")

@dp.message_handler(commands = ("history", "h"))
async def start(message: types.Message):
    cmd_variants = ('/history', '/h')
    within_als = {
        "day": ('today', 'day', 'сегодня', 'день'),
        "month": ('month', 'месяц'),
        "year": ('year', 'год'),
    }

    cmd = message.text
    for r in cmd_variants:
        cmd = cmd.replace(r, '').strip()

    within = 'day'
    if(len(cmd)):
        for k in within_als:
            for als in within_als[k]:
                if(als == cmd):
                    within = k

    records = BotDB.get_records(message.from_user.id, within)

    if(len(records)):
        answer = f"🕘 История операций за {within_als[within][-1]}\n\n"

        for r in records:
            answer += "<b>" + ("➖ Расход" if not r[2] else "➕ Доход") + "</b>"
            answer += f" - {r[3]}"
            answer += f" <i>({r[4]})</i>\n"

        await message.reply(answer)
    else:
        await message.reply("Записей не обнаружено!") 


@dp.message_handler()
async def filter_mes(message: types.Message):
        if not dbx.user_exists(message.from_user.id):
            dbx.add_user(message.from_user.id)
        if not dbx.mute(message.from_user.id):
            print(".")
        else:
            await message.delete()

        if {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.text.split(' ')}.intersection(set(json.load(open('cenz.json')))) != set():
            await message.delete()

@dp.message_handler(content_types=["new_chat_members"])
async def start_commandr(message: types.Message):
    await message.answer("Добро пожаловать!\nЕсли вы пришли по какому-то вопросу, то их вы можете задавать здесь.\n Также можете по желанию подписаться на канал - @ait_bro01z")

@dp.message_handler(content_types=["left_chat_member"])
async def start_command(message: types.Message):
    await message.delete()