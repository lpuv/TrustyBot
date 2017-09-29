import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import dataIO
from .utils.dataIO import fileIO
from cogs.utils import checks
from random import choice
from binascii import unhexlify
from binascii import a2b_uu
import random
import hashlib
import aiohttp
import asyncio


class DNADecode:

    def __init__(self, bot):
        self.bot = bot
        self.table = {
    "A": ["00", "01", "10", "11", "00", "00", "00", "01", "01", "01", "10", "10", "10", "11", "11", "11"],
    "G": ["01", "10", "11", "00", "11", "10", "01", "11", "00", "10", "11", "00", "01", "00", "01", "10"],
    "C": ["10", "11", "00", "01", "10", "11", "10", "10", "11", "00", "01", "11", "00", "01", "00", "01"],
    "T": ["11", "00", "01", "10", "01", "01", "11", "00", "10", "11", "00", "01", "11", "10", "10", "00"]
    }
        # A = 00
        # G = 10
        # C = 11
        # T = 01
    def remove_non_ascii(self, data):
        msg = b""
        for char in data:
            if char in range(0, 127):
                msg += bytes(chr(char).encode("utf8"))
        return msg

    def search_words(self, data):
        count = 0
        try:
            for char in data:
                if ord(char) in range(47, 122):
                    count += 1
        except TypeError:
            for char in data:
                if char in range(47, 122):
                    count += 1
        try:
            if(count/len(data)) >= 0.75:
                return True
        except ZeroDivisionError:
            return False
        return False

    @commands.command(pass_context=True)
    async def binary(self, ctx, *, message: str):
        message = message.strip(" ")
        binary = ' '.join(bin(x)[2:].zfill(8) for x in message.encode('UTF-8'))
        await self.bot.say(binary)

    @commands.command(pass_context=True)
    async def dnaencode(self, ctx, *, message: str):
        dna = {"00": "A", "01": "T", "10": "G", "11": "C"}
        message = message.strip(" ")
        binary = ' '.join(bin(x)[2:].zfill(8) for x in message.encode('UTF-8')).replace(" ", "")
        binlist = [binary[i:i+2] for i in range(0, len(binary), 2)]
        newmsg = ""
        count = 0
        for letter in binlist:
            newmsg += dna[letter]
            count += 1
            if count == 4:
                count = 0
                newmsg += " "
        await self.bot.say(newmsg)


    @commands.command(pass_context=True)
    async def dna(self,ctx, *, message: str):
        message = message.strip(" ")
        mapping = {}
        replacement = ""
        # for i in range(0, 15):
        skip = [" ", "\n", "\r"]
        for character in message:
            if character in skip:
                continue
            replacement += self.table[character][5]
        try:
            n = int("0b" + replacement, 2)
            mapping[5] = n.to_bytes((n.bit_length() + 7) // 8, 'big').decode("utf8", "ignore")
        except TypeError:
            pass
        replacement = ""
        await self.bot.say("```" + mapping[5] + "```")
            # print(mapping[i])
        # for result in mapping.values():
            # if self.search_words(result):
                # await self.bot.say("```" + result[:1500] + "```")


def setup(bot):
    n = DNADecode(bot)
    bot.add_cog(n)