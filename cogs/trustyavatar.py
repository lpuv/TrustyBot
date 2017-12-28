import discord
from discord.ext import commands
from random import choice, randint
import asyncio
import aiohttp


class TrustyAvatar:
    """Changes the bot's image every so often"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.url = ["https://imgur.com/5BzptFg.png", # Sad
                    "https://imgur.com/b4Qpz6V.png", # Angry
                    "https://imgur.com/nJXLjip.png", # Watching
                    "https://imgur.com/Pwz7rzs.png", # Are you kidding me
                    "https://imgur.com/bvh93u4.png", # Happy
                    "https://imgur.com/VXIUHMb.png", # Quizzical
                    "https://imgur.com/0aVJqlS.png"] # Neutral
        self.christmas = ["https://imgur.com/SkNB8Pr.png", # Sad
                          "https://imgur.com/J98wFhk.png", # Watching
                          "https://imgur.com/gRUfLKI.png", # Angry
                          "https://imgur.com/khUrr4x.png", # Are you kidding me
                          "https://imgur.com/PqVdPj0.png", # Happy
                          "https://imgur.com/UGOuOp4.png", # Neutral
                          "https://imgur.com/1Bm9t68.png"] # Quizzical
        self.loop = bot.loop.create_task(self.change_avatar())
    
    def __unload(self):
        self.session.close()
        self.loop.cancel()
    
    async def change_avatar(self):
        await self.bot.wait_until_ready()
        while self is self.bot.get_cog("TrustyAvatar"):
            try:
                async with self.session.get(choice(self.url)) as r:
                    data = await r.read()
                await self.bot.edit_profile(self.bot.settings.password, avatar=data)
            except Exception as e:
                print(e)
            await asyncio.sleep(randint(60, 600))

def setup(bot):
    n = TrustyAvatar(bot)
    bot.add_cog(n)
