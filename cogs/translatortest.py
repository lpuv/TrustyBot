import discord
import aiohttp
import asyncio
import json
import os
from datetime import datetime
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks

class TranslatorTest:

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json("data/translatortest/settings.json")
        self.loop = bot.loop.create_task(self.delete_messages())
        self.ignore_list = ["398545969647714323",
                            "398646922941825035",
                            "398646980332486657",
                            "398647024205168641",
                            "398647093297938432",
                            "398647117780090882",
                            "398671435221958656",
                            "399455201221672991"]

    def __unload(self):
        self.loop.cancel()

    async def delete_messages(self):
        await self.bot.wait_until_ready()
        while self is self.bot.get_cog("TranslatorTest"):
            server = self.bot.get_server(id="398545820149874688")
            for channel in server.channels:
                if channel.id in self.ignore_list:
                    continue
                try:
                    async for message in self.bot.logs_from(channel, limit=1000):
                        if not message.pinned:
                            await self.bot.delete_message(message)
                    # print("deleted messages in {}".format(channel.name))
                except:
                    # print("Couldn't delete in {}: {}".format(channel.name, channel.id))
                    pass
            print("deleted messages")
            await asyncio.sleep(self.settings[0])

    @commands.command(pass_context=True)
    async def ttrate(self, ctx, time:int):
        """Set the seconds before deleting messages in each channel"""
        self.settings = [time]
        dataIO.save_json("data/translatortest/settings.json", self.settings)
        await self.bot.say("Channel purge time set to {} seconds".format(time))


def check_folder():
    if not os.path.exists("data/translatortest"):
        print("Creating data/translatortest folder")
        os.makedirs("data/translatortest")

def check_file():
    data = [120]
    f = "data/translatortest/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, data)

def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(TranslatorTest(bot))