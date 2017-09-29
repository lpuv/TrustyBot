import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import dataIO
from .utils.dataIO import fileIO
from cogs.utils import checks
from random import choice
from binascii import unhexlify
import time
import random
import hashlib
import aiohttp
import asyncio
import string
import re


class MentionSpam:

    def __init__(self, bot):
        self.bot = bot
    
    async def check_mention_spam(self, message):
        server = message.server
        author = message.author
        if server is None or server.id not in ["239232811662311425", "321105104931389440"]:
            return False
        max_mentions = 5
        mentions = set(message.mentions)
        if len(mentions) >= max_mentions:
            try:
                await self.bot.kick(author)
            except:
                print("Failed to kick member for mention spam")
            else:
                return True
        return False
    
    async def on_message(self, message):
        await self.check_mention_spam(message)

def setup(bot):
    bot.add_cog(MentionSpam(bot))