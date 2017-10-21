import discord
from discord.ext import commands
from .utils.dataIO import dataIO
import aiohttp
import json
import random
from random import sample
from random import choice
import time


class TarotReading:
    """It's time to get your fortune!!!"""

    def __init__(self, bot):
        self.bot = bot
        self.tarot_cards = dataIO.load_json("data/tarot/tarot.json")

    def get_colour(self):
        colour =''.join([choice('0123456789ABCDEF')for x in range(6)])
        return int(colour, 16)

    @commands.group(pass_context=True)
    async def tarot(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)
    
    @tarot.command(name="life", pass_context=True)
    async def _life(self, ctx, user: discord.Member=None):
        """Generates your tarot reading using your discord ID as the seed"""
        card_meaning = ["Past", "Present", "Future", "Potential", "Reason"]
        if user is None:
            user = ctx.message.author
        userseed = user.id
        
        random.seed(int(userseed))
        cards = []
        cards = sample((range(1, 78)), 5)
        
        embed = discord.Embed(title="Tarot reading for {}".format(user.display_name),
                              colour=discord.Colour(value=self.get_colour()),
                              timestamp=ctx.message.timestamp)
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.set_thumbnail(url=self.tarot_cards[str(cards[-1])]["card_img"])
        number = 0
        for card in cards:
            embed.add_field(name="{0}: {1}".format(card_meaning[number], self.tarot_cards[str(card)]["card_name"]),
                            value=self.tarot_cards[str(card)]["card_meaning"])
            number += 1
        await self.bot.send_message(ctx.message.channel, embed=embed)
    
    @tarot.command(name="reading", pass_context=True)
    async def _reading(self, ctx, user: discord.Member=None):
        """Generates a random reading at this point in time"""
        card_meaning = ["Past", "Present", "Future", "Potential", "Reason"]
        if user is None:
            user = ctx.message.author
        
        cards = []
        cards = sample((range(1, 78)), 5)
        
        embed = discord.Embed(title="Tarot reading for {}".format(user.display_name),
                              colour=discord.Colour(value=self.get_colour()),
                              timestamp=ctx.message.timestamp)
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        embed.set_thumbnail(url=self.tarot_cards[str(cards[-1])]["card_img"])
        number = 0
        for card in cards:
            embed.add_field(name="{0}: {1}".format(card_meaning[number], self.tarot_cards[str(card)]["card_name"]),
                            value=self.tarot_cards[str(card)]["card_meaning"])
            number += 1
        await self.bot.send_message(ctx.message.channel, embed=embed)


    @tarot.command(name="card", pass_context=True, aliases=["cards"])
    async def _card(self, ctx, *, msg=None):
        """Generates a random card or pulls information on a specific card by name or number"""
        user = ctx.message.author.id
        # msg = message.content
        card = None

        if msg is None:
            card = self.tarot_cards[str(random.randint(1, 78))]

        elif msg.isdigit() and int(msg) > 0 and int(msg) < 79:
            card = self.tarot_cards[str(msg)]
        
        elif not msg.isdigit():
            for cards in self.tarot_cards:
                if msg.lower() in self.tarot_cards[cards]["card_name"].lower():
                    card = self.tarot_cards[cards]
            if card is None:
                await self.bot.say("That card does not exist!")
                return

        embed = discord.Embed(title=card["card_name"],
                              description=card["card_meaning"],
                              colour=discord.Colour(value=self.get_colour()),
                              url=card["card_url"])
        embed.set_image(url=card["card_img"])
        await self.bot.send_message(ctx.message.channel, embed=embed)


def setup(bot):
    bot.add_cog(TarotReading(bot))