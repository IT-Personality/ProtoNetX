from filters import IsOwnerFilter, IsAdminFilter, MemberCanRestrictFilter
import logging
import asyncio
from aiogram import Bot, types,executor,Dispatcher
import config

logging.basicConfig(level=logging.INFO)
if not config.BOT_TOKEN:
    exit("No token provided")

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

dp.filters_factory.bind(IsOwnerFilter)
dp.filters_factory.bind(IsAdminFilter)
dp.filters_factory.bind(MemberCanRestrictFilter)