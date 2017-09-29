import discord
from discord.ext import commands
import re

class Covfefe:

    def __init__(self, bot):
        self.bot = bot
    
    def covfefe(self, x, k='aeiouy])'):
        try:
            b,c,v=re.findall(f'(.*?[{k}([^{k}.*?([{k}',x)[0];return b+c+(('bcdfgkpstvz'+c)['pgtvkgbzdfs'.find(c)]+v)*2
        except:
            return None
    
    @commands.command(pass_context=True)
    async def covefy(self, ctx, msg):
        """covfefe"""
        newword = self.covfefe(msg)
        if newword is not None:
            await self.bot.say(newword)
        else:
            await self.bot.say("I cannot covfefeify that word")

def setup(bot):
    bot.add_cog(Covfefe(bot))