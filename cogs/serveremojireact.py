import discord
from discord.ext import commands
from .utils.dataIO import dataIO
import os

class ServerEmojiReact():
    def __init__(self, bot):
        self.bot = bot
        self.settings_file = "data/emojireact/settings.json"
        self.settings = dataIO.load_json(self.settings_file)

    @commands.group(pass_context=True)
    async def emojireact(self, ctx):
         if ctx.invoked_subcommand is None:
             await self.bot.send_cmd_help(ctx)

    @emojireact.command(pass_context=True, aliases=["on"])
    async def add(self, ctx):
        self.settings[ctx.message.server.id] = True
        dataIO.save_json(self.settings_file, self.settings)
        await self.bot.send_message(ctx.message.channel, "Okay, I will react to messages containing server emojis!")

    @emojireact.command(pass_context=True, aliases=["del", "rem", "off"])
    async def remove(self, ctx):
        self.settings[ctx.message.server.id] = False
        dataIO.save_json(self.settings_file, self.settings)
        await self.bot.send_message(ctx.message.channel, "Okay, I will not react to messages containing server emojis!")

    async def on_message(self, message):
        channel = message.channel
        if message.server.id not in self.settings:
            return
        if not self.settings[message.server.id]:
            return
        emojis = lambda: [x.rpartition(">")[0].partition("<")[2] for x in message.content.split(' ') if x.startswith('<:') and x.endswith('>')]
        if emojis() == []:
            return
        for emoji in emojis():
            await self.bot.add_reaction(message, emoji)

def check_folders():
    if not os.path.exists("data/emojireact"):
        print("Creating data/emojireact folder...")
        os.makedirs("data/emojireact")


def check_files():
    f = "data/emojireact/settings.json"
    data = {}
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, data)



def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(ServerEmojiReact(bot))
