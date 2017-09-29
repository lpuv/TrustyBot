import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import dataIO
from .utils.dataIO import fileIO
from cogs.utils import checks
from random import choice
from pywinauto.application import Application


class DiscordPlaysPokemon:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def startgame(self):
        app = Application().start("D:\\Games\\Pokemon\\VisualBoyAdvance.exe'Yellow.gbc'")

    async def on_message(self, message):
        server = message.server
        channel = message.channel


def setup(bot):
    n = DiscordPlaysPokemon(bot)
    bot.add_cog(n)
