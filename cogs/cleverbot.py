from discord.ext import commands
from cogs.utils import checks
from .utils.dataIO import dataIO
import os
import aiohttp
import discord

API_URL = "https://www.cleverbot.com/getreply"


class CleverbotError(Exception):
    pass

class NoCredentials(CleverbotError):
    pass

class InvalidCredentials(CleverbotError):
    pass

class APIError(CleverbotError):
    pass

class OutOfRequests(CleverbotError):
    pass

class OutdatedCredentials(CleverbotError):
    pass


class Cleverbot():
    """Cleverbot"""

    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json("data/cleverbot/settings.json")
        self.instances = {}
        self.food = {"sandwich": "data/cleverbot/sandwich.jpg", 
                     "asada": "data/cleverbot/asada.jpg",
                     "asado": "data/cleverbot/asado.jpg",
                     "sushi": "data/cleverbot/sushi.jpg",
                     "chicken": "data/cleverbot/chicken.jpg"}

    @commands.group(no_pm=True, invoke_without_command=True, pass_context=True)
    async def cleverbot(self, ctx, *, message):
        """Talk with cleverbot"""
        author = ctx.message.author
        channel = ctx.message.channel
        try:
            result = await self.get_response(author, message)
        except NoCredentials:
            await self.bot.send_message(channel, "The owner needs to set the credentials first.\n"
                                                 "See: `[p]cleverbot apikey`")
        except APIError:
            await self.bot.send_message(channel, "Error contacting the API.")
        except InvalidCredentials:
            await self.bot.send_message(channel, "The token that has been set is not valid.\n"
                                                 "See: `[p]cleverbot apikey`")
        except OutOfRequests:
            await self.bot.send_message(channel, "You have ran out of requests for this month. "
                                                 "The free tier has a 5000 requests a month limit.")
        except OutdatedCredentials:
            await self.bot.send_message(channel, "You need a valid cleverbot.com api key for this to "
                                                 "work. The old cleverbot.io service will soon be no "
                                                 "longer active. See `[p]help cleverbot apikey`")
        else:
            await self.bot.say(result)

    @cleverbot.command(pass_context=True)
    @checks.mod_or_permissions(manage_channels=True)
    async def toggle(self, ctx):
        """Toggles reply on mention"""
        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = {"TOGGLE" : True, "channel":""}
        self.settings[server.id]["TOGGLE"] = not self.settings["TOGGLE"]
        if self.settings[server.id]["TOGGLE"]:
            await self.bot.say("I will reply on mention.")
        else:
            await self.bot.say("I won't reply on mention anymore.")
        dataIO.save_json("data/cleverbot/settings.json", self.settings)
    
    @cleverbot.command(pass_context=True)
    @checks.mod_or_permissions(manage_channels=True)
    async def channel(self, ctx, channel: discord.Channel):
        """Toggles channel for automatic replies"""
        server = ctx.message.server
        if server.id not in self.settings:
            self.settings[server.id] = {"TOGGLE" :False, "channel":""}
        self.settings[server.id]["channel"] = channel.id
        await self.bot.say("I will reply in {}".format(channel))
        dataIO.save_json("data/cleverbot/settings.json", self.settings)

    @cleverbot.command()
    @checks.is_owner()
    async def apikey(self, key: str):
        """Sets token to be used with cleverbot.com
        You can get it from https://www.cleverbot.com/api/
        Use this command in direct message to keep your
        token secret"""
        self.settings["cleverbot_key"] = key
        self.settings.pop("key", None)
        self.settings.pop("user", None)
        dataIO.save_json("data/cleverbot/settings.json", self.settings)
        await self.bot.say("Credentials set.")

    async def get_response(self, author, text):
        payload = {}
        payload["key"] = self.get_credentials()
        payload["cs"] = self.instances.get(author.id, "")
        payload["input"] = text
        session = aiohttp.ClientSession()

        async with session.get(API_URL, params=payload) as r:
            if r.status == 200:
                data = await r.json()
                self.instances[author.id] = data["cs"] # Preserves conversation status
            elif r.status == 401:
                raise InvalidCredentials()
            elif r.status == 503:
                raise OutOfRequests()
            else:
                raise APIError()
        await session.close()
        return data["output"]

    def get_credentials(self):
        if "cleverbot_key" not in self.settings:
            if "key" in self.settings:
                raise OutdatedCredentials() # old cleverbot.io credentials
        try:
            return self.settings["cleverbot_key"]
        except KeyError:
            raise NoCredentials()

    async def on_message(self, message):
        server = message.server
        if server.id not in self.settings:
            self.settings[server.id] = {"TOGGLE" :True, "channel":""}
            dataIO.save_json("data/cleverbot/settings.json", self.settings)
        if not self.settings[server.id]["TOGGLE"] or message.server is None:
            return

        if not self.bot.user_allowed(message):
            return

        author = message.author
        channel = message.channel

        if message.author.id != self.bot.user.id:
            to_strip = "@" + author.server.me.display_name + " "
            text = message.clean_content
            if not text.startswith(to_strip) and message.channel.id != self.settings[server.id]["channel"]:
                return
            text = text.replace(to_strip, "", 1)
            if "make me" in text.lower() and "sudo" not in text.lower():
                food = text.lower().split(" ")[-1]
                if food in self.food:
                    await self.bot.send_typing(channel)
                    await self.bot.send_message(channel, "Make your own {}!".format(food))
                    return
            if "sudo make me" in text.lower():
                food = text.lower().split(" ")[-1]
                if food in self.food:
                    if "chicken" in text.lower():
                        await self.bot.send_typing(channel)
                        await self.bot.send_file(channel, self.food["chicken"], content="OK, OK, here's your damn chicken {}!".format(food))
                        return
                    else:
                        await self.bot.send_typing(channel)
                        await self.bot.send_file(channel, self.food[food], content="OK, OK, here's your damn {}!".format(food))
                        return
            if text.lower() == "what is your real name?":
                await self.bot.send_typing(channel)
                await self.bot.send_message(channel,"I'm OpSec. Duh!")
                return
            await self.bot.send_typing(channel)
            try:
                response = await self.get_response(author, text)
            except NoCredentials:
                await self.bot.send_message(channel, "The owner needs to set the credentials first.\n"
                                                     "See: `[p]cleverbot apikey`")
            except APIError:
                await self.bot.send_message(channel, "Error contacting the API.")
            except InvalidCredentials:
                await self.bot.send_message(channel, "The token that has been set is not valid.\n"
                                                     "See: `[p]cleverbot apikey`")
            except OutOfRequests:
                await self.bot.send_message(channel, "You have ran out of requests for this month. "
                                                     "The free tier has a 5000 requests a month limit.")
            except OutdatedCredentials:
                await self.bot.send_message(channel, "You need a valid cleverbot.com api key for this to "
                                                     "work. The old cleverbot.io service will soon be no "
                                                     "longer active. See `[p]help cleverbot apikey`")
            else:
                await self.bot.send_message(channel, response)


def check_folders():
    if not os.path.exists("data/cleverbot"):
        print("Creating data/cleverbot folder...")
        os.makedirs("data/cleverbot")


def check_files():
    f = "data/cleverbot/settings.json"
    data = {"TOGGLE" : True}
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, data)


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Cleverbot(bot))