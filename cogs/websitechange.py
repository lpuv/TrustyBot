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
import os

class WebsiteChangeChecker:

    def __init__(self, bot):
        self.bot = bot
        self.settings_file = "data/websitechange/settings.json"
        self.settings = dataIO.load_json(self.settings_file)
        self.loop = bot.loop.create_task(self.post_changes())
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    def __unload(self):
        self.loop.cancel()
    
    @commands.command(hidden=True, pass_context=True)
    @checks.admin_or_permissions(manage_channels=True)
    async def addwebcheck(self, ctx, website, channel:discord.Channel=None):
        if website in self.settings:
            websitelist = self.settings
        else:
            self.settings[website] = {"hash": "", "channel" : []}
        if channel is None:
            channel = ctx.message.channel

        if channel.id in self.settings[website]["channel"]:
            await self.bot.say("I am already posting in ".format(channel.mention))
            return
        self.settings[website]["channel"].append(channel.id)
        await self.bot.say("{0} Added to {1}!".format(website, channel.mention))
        try:
            async with self.session.get(website) as resp:
                data = await resp.read()
                self.settings[website]["hash"] = hashlib.sha256(data).hexdigest()
        except:
            print("Something must be wrong with {}".format(website))
        dataIO.save_json(self.settings_file, self.settings)
    
    @commands.command(hidden=True, pass_context=True)
    @checks.admin_or_permissions(manage_channels=True)
    async def delwebcheck(self, ctx, website, channel:discord.Channel=None):
        try:
            websitelist = self.settings[website]
        except KeyError:
            await self.bot.say("{} is not in my list of websites!"
                               .format(website))
            return

        if channel is None:
            channel = ctx.message.channel

        if channel.id in websitelist["channel"]:
            if len(websitelist["channel"]) < 2:
                self.settings[website].pop(website, None)
            else:
                websitelist["channel"].remove(channel.id)
            dataIO.save_json(self.settings_file, self.settings)
            await self.bot.say("{0} removed from {1}!"
                               .format(website, channel.mention))
        else:
            await self.bot.say("{0} doesn't seem to be posting in {1}!"
                               .format(website, channel.mention))

    async def post_changes(self):
        await self.bot.wait_until_ready()
        while self is self.bot.get_cogs("WebsiteChangeChecker"):
            for key in list(self.settings):
                async with self.session.get(key) as resp:
                    data = await resp.read()
                datahash = hashlib.sha256(data).hexdigest()
                if datahash != self.settings[key]["hash"]:
                    for channels in self.settings[key]["channel"]:
                        channel = self.bot.get_channel(channels)
                        await self.bot.send_message(channel, "{} has changed!".format(key))
                        self.settings[key]["hash"] = datahash
                        dataIO.save_json(self.settings_file, self.settings)
            await asyncio.sleep(120)

        

def check_folder():
    if not os.path.exists("data/websitechange"):
        print("Creating data/websitechange folder")
        os.makedirs("data/websitechange")


def check_file():
    data = {}
    f = "data/websitechange/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, data)

def setup(bot):
    check_folder()
    check_file()
    n = WebsiteChangeChecker(bot)
    bot.add_cog(n)