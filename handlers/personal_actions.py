from dispatcher import dp
import config
from aiogram import Bot,types,executor,Dispatcher
from bot import BotDB
import json
import asyncio
import re
import requests
from bs4 import BeautifulSoup as BS
import time
import string

@dp.message_handler(commands = ["start", "help"])
async def start(message: types.Message):
    await message.answer("Привет!\n Я модератор, слежу за порядком в этом чате 🙂")

@dp.message_handler(commands=['id_users'])
async def id(message: types.Message):
    await message.reply(f"Ваш ID: {message.from_user.id}")

@dp.message_handler(commands = ["well_USD"])
async def start_ud(message: types.Message):
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

@dp.message_handler(commands = ("start_news"))
async def start_new(message: types.Message):
    print("Запуск новостей - успешно!")
    while True:
        if str(message.from_user.id) == config.ADMIN_ID:
            url = 'https://habr.com/ru/news/'
            r = requests.get(url)
            soup = BS(r.text, 'lxml')
            result = soup.find("a", { "class" : "tm-article-snippet__title-link" }).text
            res_url = soup.find(class_='tm-article-snippet__title-link')['href']
            await asyncio.sleep(20000)
            await message.bot.send_message(-1001533296339, f'⚡️#IT_Новости\n<a href="https://habr.com{res_url}">{result}</a>')  
        else:
            await message.reply(f"Увы, эту команду может отправлять только админ")

# -1001533296339

@dp.message_handler()
async def filter_mes(message: types.Message):
        if {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.text.split(' ')}.intersection(set(json.load(open('mat.json')))) != set():
            await message.delete()

@dp.message_handler(content_types=["new_chat_members"])
async def start_commandr(message: types.Message):
    msg = await message.reply(f"Добро пожаловать!\nЕсли вы пришли по какому-то вопросу, то их вы можете задавать здесь.\n Также можете по желанию подписаться на канал - @ait_bro01z")
    await asyncio.sleep(600)
    await msg.delete()
    await message.delete()