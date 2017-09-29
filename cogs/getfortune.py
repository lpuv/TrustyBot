import discord
from discord.ext import commands
from .utils.dataIO import dataIO
import aiohttp
import json
import random
from random import randint
from random import choice
import time


class YourFortune:
    """It's time to get your fortune!!!"""

    def __init__(self, bot):
        self.bot = bot
        self.image = dataIO.load_json("data/getfortune/fortune.json")
        self.tarot = dataIO.load_json("data/getfortune/tarot.json")
        self.STARTTIME = time.time()
        self.ENDTIME = dataIO.load_json("data/getfortune/settings.json")
        self.COOLDOWNTIMER = 60
        self.admins = ["142525247357321216", "218773382617890828"]

    async def getfortune(self, ctx):
        """What is your fortune? Well then, lets find out..."""
        user = ctx.message.author
        page = randint(1,6)
        link = "http://fortunecookieapi.herokuapp.com/v1/fortunes?limit=&skip=&page={}".format(page)
        async with aiohttp.get(link) as m:
            result = await m.json()
            message = choice(result)
            return message["message"]

   
    @commands.command(pass_context=True)
    @commands.cooldown(1, 60, commands.BucketType.server)
    async def tux(self, ctx, *, message=None):
        server = str(ctx.message.server.id)
        user = ctx.message.author.id
        msg = await self.getfortune(ctx)
        if message is None:
            underscore = "=" * (len(msg) + 2)
            await self.bot.say("```Markdown\n" + self.image["tux"].format(underscore, msg, underscore) + "```")
        else:
            underscore = "=" * (len(message) + 2)
            await self.bot.say("```Markdown\n" + self.image["tux"].format(underscore, message, underscore) + "```")

    @commands.command(pass_context=True)
    @commands.cooldown(1, 60, commands.BucketType.server)
    async def cowsay(self, ctx, *, message=None):
        server = str(ctx.message.server.id)
        user = ctx.message.author.id
        msg = await self.getfortune(ctx)
        if message is None:
            underscore = "=" * (len(msg) + 2)
            await self.bot.say("```Markdown\n" + self.image["cow"].format(underscore, msg, underscore) + "```")
        else:
            underscore = "=" * (len(message) + 2)
            await self.bot.say("```Markdown\n" + self.image["cow"].format(underscore, message, underscore) + "```")


def setup(bot):
    bot.add_cog(YourFortune(bot))
