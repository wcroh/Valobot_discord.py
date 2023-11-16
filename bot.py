from __future__ import annotations

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import aiohttp
import asyncio

from utils.cache import get_cache

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

BOT_PREFIX = '/'
initial_extensions = ['Cogs.valorant']

class ValoBot(commands.Bot):
    bot_app_info: discord.AppInfo
    
    def __init__(self) -> None:
        super().__init__(command_prefix=BOT_PREFIX, case_insensitive=True, intents=intents)
        self.bot_version = '1.0.0'
        self.session : aiohttp.ClientSession = None
        
    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner
        
    async def on_ready(self)-> None:
        await self.tree.sync()
        print(f"{self.user}로 로그인!\n\n 발로봇 준비 완료!")
        print(f"Version: {self.bot_version}")
        
        activity_type = discord.ActivityType.listening
        await self.change_presence(activity=discord.Activity(type=activity_type, name=">__<"))

    async def setup_hook(self) -> None:
        if self.session is None:
            self.session = aiohttp.ClientSession()

        try:
            self.owner_id = int(os.getenv('OWNER_ID'))
        except ValueError:
            self.bot_app_info = await self.application_info()
            self.owner_id = self.bot_app_info.owner.id

        self.setup_cache()
        await self.load_cogs()
        
    async def load_cogs(self) -> None:
        for ext in initial_extensions:
            await self.load_extension(ext)
    
    @staticmethod
    def setup_cache() -> None:
        try:
            open('data/cache.json')
        except FileNotFoundError:
            get_cache()
            
    async def close(self) -> None:
        await self.session.close()
        await super().close()
    
    async def start(self) -> None:
        return await super().start(os.getenv('TOKEN'), reconnect=True)
    
def run_bot() -> None:
    bot = ValoBot()
    asyncio.run(bot.start())
    
if __name__ == '__main__':
    run_bot()
        