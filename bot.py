import handlers
import requests
from aiogram import Bot, types,executor,Dispatcher
from db import BotDB
import asyncio
from dispatcher import dp
import time
from filters import IsOwnerFilter, IsAdminFilter, MemberCanRestrictFilter
import config

BotDB = BotDB('accountant.db')

if __name__ == "__main__":
    executor.start_polling(dp)