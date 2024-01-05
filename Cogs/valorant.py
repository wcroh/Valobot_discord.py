from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Literal  # noqa: F401

from discord import Interaction, app_commands, ui
from discord.ext import commands, tasks
from discord.utils import MISSING
from utils.endpoint import API_ENDPOINT
from utils.embed import GetEmbed
import asyncio

from bot import ValoBot
from utils.auth import Auth
from utils.resources import setup_emoji
from utils.cache import fetch_price

if TYPE_CHECKING:
    from bot import ValorantBot

class ValoCog(commands.Cog, name = 'Valorant'):
    """Valorant API Commands"""
    
    def __init__(self, bot: ValoBot) -> None:
        self.bot: ValoBot = bot
        self.auth = Auth()
        self.db : dict = {}
        self.endpoint : API_ENDPOINT = None
        
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """When the bot is ready"""
        self.endpoint = API_ENDPOINT()
    
    @app_commands.command(name='우진')
    async def woojin(self, interaction: Interaction) -> None:
        woojin_id = 1002033065205432430
        if interaction.user.id == 1002033065205432430:
            await interaction.response.send_message('우진님이 지금 발로란트를 같이 할 사람을 찾고 있어요!'
            )
        elif interaction.user.id == 353551869471096835:
            await interaction.response.send_message(f'<@{woojin_id}> 우진아 발로하자!'
            )
        else: await interaction.response.send_message('우진이 수능 고생했다!🥳🥳🥳🥳🥳')
        
    @app_commands.command(name='유경')
    async def yuki(self, interaction: Interaction) -> None:
        if interaction.user.id == 1136338502930415727:
            await interaction.response.send_message('나는 너무 예뻐 이렇게 태어나준 내 자신에게 고마워!!🥳🥳🥳🥳🥳')
        else :await interaction.response.send_message('유경이 생일 축하해!!🥳🥳🥳🥳🥳')
    
    @app_commands.command(name='로그인', description='라이엇 계정으로 로그인')
    @app_commands.describe(id='아이디를 입력하세요', pw = '패스워드를 입력하세요')
    async def login(self, interaction:Interaction, id:str, pw:str) -> None:
        user_id = interaction.user.id

        authenticate = await self.auth.authenticate(username=id, password=pw)
        print('pass authenticate')
        if authenticate['auth'] == 'response':
            await interaction.response.defer(ephemeral=True)
            self.db[user_id] = {'id':id,'pw':pw}
            print('saved db')
            access_token = authenticate['data']['access_token']
            puuid, name, tag = await self.auth.get_userinfo(access_token)
            print('user info 성공')
            return await interaction.followup.send(content=f'{name}#{tag}로 로그인 성공!', ephemeral=True)
        else:
            return await interaction.response.send_message(content=f'로그인 오류, 다시 로그인해주세요!(/로그인)')
        
        
    @app_commands.command(name='스킨', description='상점에서 스킨을 받아옵니다.')
    async def store(self, interaction:Interaction):
        user_id = interaction.user.id
        await interaction.response.defer(ephemeral=False)
        
        if user_id in self.db.keys():
            id = self.db[user_id]['id']
            pw = self.db[user_id]['pw']
            user_data = await self.auth.temp_auth(id,pw)
            await setup_emoji(self.bot, interaction.guild)
            
            endpoint = await self.get_endpoint(user_data)
            
            skin_price = endpoint.store_fetch_offers()
            fetch_price(skin_price)
        
            data = endpoint.store_fetch_storefront()
            
            embeds = GetEmbed.store(endpoint.player, data, self.bot)
            await interaction.followup.send(embeds=embeds)
            
        else:
            return await interaction.response.send_message(content=f'(로그인 정보가 없습니다, 다시 로그인해주세요!(/로그인)')
        
    async def get_endpoint(self, user_data):
        endpoint = self.endpoint
        endpoint.activate(user_data)
        return endpoint
        
async def setup(bot: ValoBot) -> None:
    await bot.add_cog(ValoCog(bot))