import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import dataIO
from cogs.utils import checks
import asyncio
import os
import urllib.request
import aiohttp
import json
import time

class ActivityChecker():

    def __init__(self, bot):
        self.bot = bot
        self.settings_file = "data/activity/settings.json"
        self.log_file = "data/activity/log.json"
        self.settings = dataIO.load_json(self.settings_file)
        self.log = dataIO.load_json(self.log_file)

    @commands.group(pass_context=True)
    @checks.mod_or_permissions(kick_members=True)
    async def activity(self, ctx):
        """Setup an activity checker channel"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @activity.group(pass_context=True)
    async def remove(self, ctx):
        """Removes activity checking from a certain channel or server!"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @activity.group(pass_context=True)
    async def add(self, ctx):
        """Adds activity checking roles, channel, or server!"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @remove.command(pass_context=True, name="server")
    async def rem_server(self, ctx, server:discord.server=None):
        """Removes a server from the activity checker"""
        if server is None:
            server = ctx.message.server
        if server.id in self.settings:
            del self.settings[server.id]
        dataIO.save_json(self.settings_file, self.settings)
        await self.bot.say("Done! No more activity checking in {}!".format(server.name))

    @remove.command(pass_context=True, name="roles")
    async def rem_roles(self, ctx, role:discord.Role=None):
        """Add certain roles to ignore. Send no role to default to everyone."""
        if role is None:
            self.settings[ctx.message.server.id]["ignored_roles"] = []
        else:
            self.settings[ctx.message.server.id]["ignored_roles"].append(role.name)
        dataIO.save_json(self.settings_file, self.settings)

    @activity.command(pass_context=True)
    async def refresh(self, ctx, channel:discord.channel=None, server:discord.server=None):
        """Refreshes the activity checker to start right now"""
        if server is None:
            server = ctx.message.server
        if channel is None:
            channel = ctx.message.channel
        if "channel" in self.settings[server.id] and channel.id != self.settings[server.id]["channel"]:
            channel = self.bot.get_channel(id=self.settings[server.id]["channel"])
        if server.id in self.settings:
            role = self.settings[server.id]["ignored_roles"]
        await self.build_list(ctx, channel, server, role)

    async def build_list(self, ctx, channel, server, role):
        """Builds a new list of all server members"""
        cur_time = time.time()
        self.log[server.id] = {}
        for member in server.members:
            self.log[server.id][member.id] = cur_time
        dataIO.save_json(self.log_file, self.log)
        return

    @activity.command(pass_context=True)
    async def set(self, ctx, channel:discord.Channel=None, role:discord.Role=None):
        """Sets the channel for messaging users and offers to refresh the list"""
        server = ctx.message.server
        if channel is None:
            channel = ctx.message.channel
        if server.id in self.settings:
            msg = ctx.message
            await self.bot.say("This server is already checking for activity! Do you want to refresh it?")
            msg = await self.bot.wait_for_message(author=ctx.message.author, timeout=15)
            if msg is None:
                return
            if "yes" in msg.content:
                await self.build_list(ctx, channel, server, role)
        await self.build_list(ctx, channel, server, role)

    def check_roles(self, member, roles):
        for role in roles:
            if role in member.roles:
                return True
        return False

    async def activity_checker(self):
        while self is self.bot.get_cog("ActivityChecker"):
            for server_id in self.settings:
                server = self.bot.get_server(id=server_id)
                channel = self.bot.get_channel(id=self.settings[server.id]["channel"])
                roles = self.settings[server.id]["ignored_roles"]
                cur_time = time.time()
                for member_id in self.settings[server.id]:
                    if not member_id.isdigit() and isinstance(member_id, str):
                        continue
                    member = server.get_member(member_id)
                    if self.check_roles(member, roles):
                        continue
                    last_msg_time = cur_time - self.settings[server.id][member.id]
                    if last_msg_time > 60:
                        msg = await self.bot.send_message(channel, "{} you haven't talked in over a week! React to this message to stay!"
                                                          .format(member.mention, last_msg_time))
                        self.settings[server.id][member.id] = msg.id
                        await self.bot.add_reaction(msg, "☑")
                        dataIO.save_json(self.settings_file, self.settings)



    async def on_message(self, message):
        server = message.server
        author = message.author
        if server.id not in self.settings:
            return
        if author.id not in self.settings[server.id]:
            self.settings[server.id][author.id] = time.time()
        self.settings[server.id][author.id] = time.time()
        dataIO.save_json(self.settings_file, self.settings)

def check_folder():
    if not os.path.exists("data/activity"):
        print("Creating data/activity folder")
        os.makedirs("data/activity")


def check_file():
    data = {}
    log = "data/activity/log.json"
    if not dataIO.is_valid_json(log):
        print("Creating default log.json...")
        dataIO.save_json("data/activity/log.json", data)
    settings = "data/activity/settings.json"
    if not dataIO.is_valid_json(settings):
        print("Creating default settings.json...")
        dataIO.save_json("data/activity/settings.json", data)


def setup(bot):
    check_folder()
    check_file()
    n = ActivityChecker(bot)
    # loop = asyncio.get_event_loop()
    # loop.create_task(n.activity_checker())
    bot.add_cog(n)