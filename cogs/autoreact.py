import discord
from __main__ import settings
import asyncio

class reactions:
    def __init__(self, bot):
        self.bot = bot
        self.emoji = {
         "L": "\U0001f1f1",
         "M": "\U0001f1f2",
         "A": "\U0001f1e6",
         "O": "\U0001f1f4",
         "JOY": "\U0001f602",
         "CJOY": "\U0001f639",
         "R": "\U0001f1f7",
         "E": "\U0001f1ea",
         "K": "\U0001f1f0",
         "T": "\U0001f1f9",
         "MIDDLEFINGER": "\U0001f595",
         "FINGERCROSS": "\U0001f91e",
         "F": "\U0001f1eb",
         "U": "\U0001f1fa",
         "C": "\U0001f1e8",
         "Y": "\U0001f1fe",
         "O": "\U0001f1f4",
         "POINT": "\U0001f446",
         "FIST": "\U0001f91c",
         "BUMP": "\U0001f91b",
         "S": "\U0001f1f8",
         "D": "\U0001f1e9",
         "G": "\U0001f1ec",
         "I": "\U0001f1ee",
         "FIRE": "\U0001f525",
         "OK": "\U0001f44c",
         "CLAP": "\U0001f44f",
         "COOL": "\U0001f60e",
         "N": "\U0001f1f3",
         "100": "\U0001F4AF",
         "COOKING": "\U0001F373"}

    async def listener(self, message):
        channel = message.channel
        if message.author.id != self.bot.user.id:
            try:
                if message.content.upper() == "LMAO":
                    words = "L M A O JOY CJOY"
                    async for x in self.bot.logs_from(channel, before=message.timestamp, limit=1):
                        for letter in words.split(" "):
                            asyncio.sleep(1)
                            await self.bot.add_reaction(x, self.emoji[letter])

                if message.content.lower() == "this":
                    async for x in self.bot.logs_from(channel, before=message.timestamp, limit=1):
                        await self.bot.add_reaction(x, self.emoji["100"])

                if message.content.lower() == "roasted":
                    words = "COOKING R O A S T E D FIRE"
                    async for x in self.bot.logs_from(channel, before=message.timestamp, limit=1):
                        for letter in words.split(" "):
                            asyncio.sleep(1)
                            await self.bot.add_reaction(x, self.emoji[letter])

                if "no u" in message.content.lower():
                    words = "N O U"
                    async for x in self.bot.logs_from(channel, before=message.timestamp, limit=1):
                        for letter in words.split(" "):
                            asyncio.sleep(1)
                            await self.bot.add_reaction(x, self.emoji[letter])

                if "diaf" in message.content.lower():
                    words = "D I A F FIRE"
                    async for x in self.bot.logs_from(channel, before=message.timestamp, limit=1):
                        for letter in words.split(" "):
                            asyncio.sleep(1)
                            await self.bot.add_reaction(x, self.emoji[letter])

                if "rekt" in message.content.lower():
                    words = "R E K T"
                    async for x in self.bot.logs_from(channel, before=message.timestamp, limit=1):
                        for letter in words.split(" "):
                            asyncio.sleep(1)
                            await self.bot.add_reaction(x, self.emoji[letter])

                if "fucker" in message.content.lower():
                    words = "MIDDLEFINGER F U C K E R BUMP"
                    async for x in self.bot.logs_from(channel, before=message.timestamp, limit=1):
                        for letter in words.split(" "):
                            asyncio.sleep(1)
                            await self.bot.add_reaction(x, self.emoji[letter])

                if "idgaf" in message.content.lower():
                    words = "I D G A F COOL"
                    async for x in self.bot.logs_from(channel, before=message.timestamp, limit=1):
                        for letter in words.split(" "):
                            asyncio.sleep(1)
                            await self.bot.add_reaction(x, self.emoji[letter])

                if "sotru" in message.content.lower():
                    words = "S O CLAP T R U OK"
                    async for x in self.bot.logs_from(channel, before=message.timestamp, limit=1):
                        for letter in words.split(" "):
                            asyncio.sleep(1)
                            await self.bot.add_reaction(x, self.emoji[letter])

            except discord.Forbidden:
                pass

def setup(bot):
    n = reactions(bot)
    bot.add_listener(n.listener, "on_message")
    bot.add_cog(n)
