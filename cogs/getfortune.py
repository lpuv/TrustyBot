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

    async def getfortune(self, ctx):
        """What is your fortune? Well then, lets find out..."""
        user = ctx.message.author
        page = randint(1,6)
        link = "http://fortunecookieapi.herokuapp.com/v1/fortunes?limit=&skip=&page={}".format(page)
        with aiohttp.ClientSession() as session:
            async with session.get(link) as m:
                result = await m.json()
                message = choice(result)
                return message["message"]

   
    @commands.command(pass_context=True)
    async def tux(self, ctx, *, message=None):
        msg = message if message is not None else await self.getfortune(ctx)
        underscore = "=" * (len(msg) + 2)
        new_msg = "```Markdown\n" + self.image["tux"].format(underscore, msg, underscore) + "```"
        embed = discord.Embed(description=new_msg)
        await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def cowsay(self, ctx, *, message=None):
        msg = message if message is not None else await self.getfortune(ctx)
        underscore = "=" * (len(msg) + 2)
        new_msg = "```Markdown\n" + self.image["cow"].format(underscore, msg, underscore) + "```"
        embed = discord.Embed(description=new_msg)
        await self.bot.send_message(ctx.message.channel, embed=embed)


def setup(bot):
    bot.add_cog(YourFortune(bot))
