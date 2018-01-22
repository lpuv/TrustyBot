import discord
import aiohttp
import asyncio
import json
import os
from datetime import datetime
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from bs4 import BeautifulSoup

numbs = {
    "next": "➡",
    "back": "⬅",
    "exit": "❌"
}
class Anilist:

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.settings = dataIO.load_json("data/qposts/settings.json")
        self.qposts = dataIO.load_json("data/qposts/qposts.json")
        self.url = "https://anilist.co/api/"
        self.boards = ["greatawakening", "qresearch"]
        self.loop = bot.loop.create_task(self.get_q_posts())

    def __unload(self):
        self.session.close()
        self.loop.cancel()