import asyncio
import discord
import re
import os
import random
import string
import json
import time
import html
import codecs
from   random import shuffle
from discord.ext import commands


class LiarsDice:

    # Init with the bot reference, and a reference to the deck file
    def __init__(self, bot, file = None):
        self.bot = bot
        self.games = []
        self.maxBots = 5 # Max number of bots that can be added to a game - don't count toward max players
        self.maxPlayers = 10 # Max players for ranjom joins
        self.maxDeadTime = 3600 # Allow an hour of dead time before killing a game
        self.checkTime = 300 # 5 minutes between dead time checks
        self.winAfter = 10 # 10 wins for the game
        self.botWaitMin = 5 # Minimum number of seconds before the bot makes a decision (default 5)
        self.botWaitMax = 30 # Max number of seconds before a bot makes a decision (default 30)
        self.userTimeout = 300 # 5 minutes to timeout
        self.utCheck = 30 # Check timeout every 30 seconds
        self.utWarn = 60 # Warn the user if they have 60 seconds or less before being kicked
        self.charset = "1234567890"
        self.botName = 'Rando Cardrissian'
        self.minMembers = 3
        self.loopsleep = 0.05
        self.playerscups = {}
        self.lastbet = (0,0)
        self.wordconvert = {1: ["one", "ones"], 2: ["two", "twos"], 3: ["three", "threes"], 
                            4: ["four", "fours"], 5: ["five", "fives"], 6: ["six", "sixes"]}
        # self.bot.loop.create_task(self.checkDead())
        # self.bot.loop.create_task(self.checkUserTimeout())
    
    @commands.command(pass_context=True)
    async def newcup(self, ctx):
        author = ctx.message.author
        if author.id not in self.playerscups:
            self.playerscups[author.id] = {"cup":[], "dice": 5}
        self.playerscups[author.id]["cup"].clear()
        playersdice = self.playerscups[author.id]["dice"]            
        for i in range(0, playersdice):
            self.playerscups[author.id]["cup"].append(random.randint(1, 6))
        await self.bot.say(str(self.playerscups[author.id]["cup"]))
    
    @commands.command(pass_context=True)
    async def bet(self, ctx, *, bet):
        #stuff here
        counter = 0
        word1 = bet.split(" ")[0]
        word2 = bet.split(" ")[1]
        for words in list(self.wordconvert.values()):
            if word1 in words:
                bet.replace(word1, str(list(self.wordconvert.keys())[counter]))
            if word2 in words:
                bet.replace(word2, str(list(self.wordconvert.keys())[counter]))
            counter += 1
        if bet.split(" ")[0].isdigit() and bet.split(" ")[1].isdigit():
            await self.bot.say(bet)
        return


def setup(bot):
    bot.add_cog(LiarsDice(bot))
