import discord
import aiohttp
import asyncio
import json
import os
from datetime import datetime
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from random import choice as randchoice

numbs = {
    "next": "➡",
    "back": "⬅",
    "exit": "❌"
}
class Anilist:

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.url = "https://anilist.co/api/"
        self.settings = dataIO.load_json("data/anilist/settings.json")


    def __unload(self):
        self.session.close()

    async def check_auth(self):
        time_now = datetime.utcnow()
        params = self.settings["api"]
        params["grant_type"] = "client_credentials"
        if "token" not in self.settings:
            async with self.session.post(self.url + "auth/access_token", params=params) as resp:
                data = await resp.json()
            print(data)
            self.settings["token"] = data
        if time_now > datetime.utcfromtimestamp(self.settings["token"]["expires"]):
            async with self.session.post(self.url + "auth/access_token", params=params) as resp:
                data = await resp.json()
            print("new token saved")
            self.settings["token"] = data
        dataIO.save_json("data/anilist/settings.json", self.settings)
        header = {"access_token": self.settings["token"]["access_token"]}
        return header

    def random_colour(self):
        return int(''.join([randchoice('0123456789ABCDEF')for x in range(6)]), 16)

    async def search_menu(self, ctx, post_list: list,
                         message: discord.Message=None,
                         page=0, timeout: int=30):
        """menu control logic for this taken from
           https://github.com/Lunar-Dust/Dusty-Cogs/blob/master/menu/menu.py"""
        s = post_list[page]
        title = "{} | {}".format(s["title_english"], s["title_japanese"])
        url = "https://anilist.co/anime/{}/".format(s["id"])
        created_at = s["start_date"]
        created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S+09:00") # "2006-07-03T00:00:00+09:00"
        
        em = discord.Embed( colour=discord.Colour(value=self.random_colour()))
        if s["description"] is not None:
            desc = s["description"].replace("<br>", "\n")
            desc = desc.replace("<em>", "*")
            desc = desc.replace("</em>", "*")
            em.description = desc
        em.set_thumbnail(url=s["image_url_lge"])
        em.set_author(name=title, url=url, icon_url=s["image_url_sml"])
        em.set_footer(text="Start Date ")
        em.timestamp = created_at
        if not message:
            message =\
                await self.bot.send_message(ctx.message.channel, embed=em)
            await self.bot.add_reaction(message, "⬅")
            await self.bot.add_reaction(message, "❌")
            await self.bot.add_reaction(message, "➡")
        else:
            message = await self.bot.edit_message(message, embed=em)
        react = await self.bot.wait_for_reaction(
            message=message, user=ctx.message.author, timeout=timeout,
            emoji=["➡", "⬅", "❌"]
        )
        if react is None:
            await self.bot.remove_reaction(message, "⬅", self.bot.user)
            await self.bot.remove_reaction(message, "❌", self.bot.user)
            await self.bot.remove_reaction(message, "➡", self.bot.user)
            return None
        reacts = {v: k for k, v in numbs.items()}
        react = reacts[react.reaction.emoji]
        if react == "next":
            next_page = 0
            if page == len(post_list) - 1:
                next_page = 0  # Loop around to the first item
            else:
                next_page = page + 1
            try:
                await self.bot.remove_reaction(message, "➡", ctx.message.author)
            except:
                pass
            return await self.search_menu(ctx, post_list, message=message,
                                         page=next_page, timeout=timeout)
        elif react == "back":
            next_page = 0
            if page == 0:
                next_page = len(post_list) - 1  # Loop around to the last item
            else:
                next_page = page - 1
            try:
                await self.bot.remove_reaction(message, "⬅", ctx.message.author)
            except:
                pass
            return await self.search_menu(ctx, post_list, message=message,
                                         page=next_page, timeout=timeout)
        else:
            return await\
                self.bot.delete_message(message)



    @commands.command(pass_context=True)
    async def anisearch(self, ctx, *, search):
        header = await self.check_auth()
        async with self.session.get(self.url + "anime/search/{}".format(search), params=header) as resp:
            print(str(resp.url))
            data = await resp.json()
        dataIO.save_json("data/anilist/sample.json", data)
        if "error" not in data:
            await self.search_menu(ctx, data)
        else:
            await self.bot.say("{} was not found!".format(search))

    @commands.command(pass_context=True)
    async def anitest(self, ctx, *, search=None):
        header1 = await self.check_auth()
        header2 = header1
        header2["status"] = "currently airing"
        header2["full_page"] = True
        anime_list = []
        async with self.session.get(self.url + "browse/anime", params=header2) as resp:
            print(str(resp.url))
            data = await resp.json()
        for anime in data:
            if not anime["adult"]:
                async with self.session.get(self.url + "anime/{}/airing".format(anime["id"]), params=header1) as resp:
                    ani_data = await resp.json()
                    # print(anime["title_english"])
                    anime_list.append(ani_data)
        dataIO.save_json("data/anilist/sample.json", data)
        

    @commands.group(pass_context=True, name='aniset')
    @checks.is_owner()
    async def _aniset(self, ctx):
        """Command for setting required access information for the API.
        To get this info, visit https://apps.twitter.com and create a new application.
        Once the application is created, click Keys and Access Tokens then find the
        button that says Create my access token and click that. Once that is done,
        use the subcommands of this command to set the access details"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @_aniset.command(name='creds')
    @checks.is_owner()
    async def set_creds(self, client_id:str, client_secret:str):
        """Sets the access credentials. See [p]help tweetset for instructions on getting these"""
        self.settings["api"]["client_id"] = client_id
        self.settings["api"]["client_secret"] = client_secret
        dataIO.save_json("data/anilist/settings.json", self.settings)
        await self.bot.say('Set the access credentials!')


def check_folder():
    if not os.path.exists("data/anilist"):
        print("Creating data/anilist folder")
        os.makedirs("data/anilist")


def check_file():
    data = {"api":{'client_id': '', 'client_secret': ''}}
    f = "data/anilist/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, data)

def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(Anilist(bot))