import discord
import asyncio
from .utils.dataIO import dataIO
from discord.ext import commands
from cogs.utils import checks
import os

class Strike:

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json("data/strike/settings.json")


    @commands.command(pass_context=True)
    @checks.mod_or_permissions(kick_members=True)
    async def strike(self, ctx, user:discord.Member, *, message:str):
        if user.id not in self.settings:
            self.settings[user.id] = {}
        strike_num = "Strike {}".format(len(self.settings[user.id].items())+1)
        self.settings[user.id][strike_num] = message
        # self.settings[user.id].append(data)
        dataIO.save_json("data/strike/settings.json", self.settings)
        await self.bot.say("{} on {} for {}".format(strike_num, user.mention, message))

    @commands.command(pass_context=True)
    @checks.mod_or_permissions(kick_members=True)
    async def check_strike(self, ctx, user:discord.Member):
        strikes = ""
        if user.id not in self.settings:
            await self.bot.say("There are no strikes on {}".format(user.mention))
        else:
            for key, value in self.settings[user.id].items():
                strikes += "{}: {}\n".format(key, value)
        
        await self.bot.say(strikes)

def check_folder():
    if not os.path.exists('data/strike'):
        os.mkdir('data/strike')

def check_files():
    data = {}
    f = 'data/strike/settings.json'
    if not os.path.exists(f):
        dataIO.save_json(f, data)

def setup(bot):
    check_folder()
    check_files()
    n = Strike(bot)
    bot.add_cog(n)
