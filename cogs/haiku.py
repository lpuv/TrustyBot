from discord.ext import commands
import discord
import asyncio
from .utils.dataIO import dataIO
from .utils import checks

try:
    from haikus import HaikuText
    haiku_installed = True
except:
    haiku_installed = False
    

class Haiku:

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    if not haiku_installed:
        bot.pip_install("-e git+https://github.com/wieden-kennedy/haikus#egg=haikus")
        from haikus import HaikuText
    bot.add_cog(Haiku(bot))