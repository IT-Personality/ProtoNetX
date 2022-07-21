from dispatcher import dp
import handlers
import requests
from aiogram import Bot, types,executor,Dispatcher
from db import BotDB
from dbx import Database
import asyncio
import datetime
import time
from main_news import check_news_update
from aiogram.utils.markdown import hbold, hunderline, hcode, hlink
from aiogram.dispatcher.filters import Text

BotDB = BotDB('accountant.db')

dbx = Database('database.db')

if __name__ == "__main__":
    executor.start_polling(dp)