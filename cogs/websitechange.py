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
    
    @commands.command(hidden=True, pass_context=True)
    @checks.admin_or_permissions(manage_channels=True)
    async def addwebcheck(self, ctx, website, channel=None):
        if website in self.settings:
            websitelist = self.settings
        else:
            self.settings[website] = {"hash": "", "channel" : []}
        channelname = self.bot.get_channel(channel)

        if channel is None:
            channel = ctx.message.channel.id
        if "<#" in channel:
            channel = channel.strip("<#>")

        if channel in self.settings[website]["channel"]:
            await self.bot.say("I am already posting in <#{}>".format(channel))
            return
        self.settings[website]["channel"].append(channel)
        await self.bot.say("{0} Added to <#{1}>!".format(website, channel))
        try:
            with aiohttp.ClientSession() as session:
                async with session.get(website) as resp:
                    data = await resp.read()
                    self.settings[website]["hash"] = hashlib.sha256(data).hexdigest()
            await asyncio.sleep(1)
        except:
            print("Something must be wrong with {}".format(website))
        dataIO.save_json(self.settings_file, self.settings)
    
    @commands.command(hidden=True, pass_context=True)
    @checks.admin_or_permissions(manage_channels=True)
    async def delwebcheck(self, ctx, website, channel=None):
        try:
            websitelist = self.settings[website]
        except KeyError:
            await self.bot.say("{} is not in my list of websites!"
                               .format(website))
            return

        channelname = self.bot.get_channel(channel)
        if channel is None:
            channel = ctx.message.channel.id
        if "<#" in channel:
            channel = channel.strip("<#>")

        if channel in websitelist["channel"]:
            if len(websitelist["channel"]) < 2:
                self.settings[website].pop(website, None)
            else:
                websitelist["channel"].remove(channel)
            dataIO.save_json(self.settings_file, self.settings)
            await self.bot.say("{0} removed from <#{1}>!"
                               .format(website, channel))
        else:
            await self.bot.say("{0} doesn't seem to be posting in <#{1}>!"
                               .format(website, channel))

    async def post_changes(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed:
            for key in list(self.settings):
                with aiohttp.ClientSession() as session:
                    async with session.get(key) as resp:
                        data = await resp.read()
                        datahash = hashlib.sha256(data).hexdigest()
                        if datahash != self.settings[key]["hash"]:
                            for channel in self.settings[key]["channel"]:
                                await self.bot.send_message(self.bot.get_channel(channel), "{} has changed!".format(key))
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
    loop = asyncio.get_event_loop()
    loop.create_task(n.post_changes())
    bot.add_cog(n)