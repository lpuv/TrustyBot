import aiohttp
import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks

'''Translator cog 

Cog credit to aziz#5919 for the idea and 
 
Links

Wiki                                                https://goo.gl/3fxjSA
Github                                              https://goo.gl/oQAQde
Support the developer                               https://goo.gl/Brchj4
Invite the bot to your server                       https://goo.gl/aQm2G7
Join the official development server                https://discord.gg/uekTNPj
'''


class Translate:
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.url = "https://translation.googleapis.com"
        self.api = dataIO.load_json("data/google/settings.json")
        self.languages = dataIO.load_json("data/google/flags.json")

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def addflag(self, ctx, flag_1, flag_2=None):
        """Sets a custom flag to another flag"""
        new_data = []
        if flag_2 is not None:
            new_data = self.languages[flag_2]
        if flag_1 not in self.languages:
            self.languages[flag_1] = new_data
            dataIO.save_json("data/google/flags.json", self.languages)
        else:
            await self.bot.say("{} is already in the list!".format(flag_1))

    @commands.command(pass_context=True)
    async def translate(self, ctx, to_language, *, message):
        language_code = None
        for flag in self.languages:
            try:
                self.languages[flag] = {"code":self.languages[flag]["languages"][0]["iso639_1"],
                                        "name": self.languages[flag]["name"]}
            except:
                pass
        dataIO.save_json("data/google/flags.json", self.languages)


    async def on_reaction_add(self, reaction, user):
        """Translates the message based off the flag added"""
        if reaction.emoji not in self.languages:
            return
        if reaction.message.channel.server.id == "398545820149874688":
            return
        if reaction.message.embeds != []:
            to_translate = reaction.message.embeds[0]["description"]
        else:
            to_translate = reaction.message.clean_content    
        target = self.languages[reaction.emoji]["code"]
        formatting = "text"
        
        try:
            async with self.session.get(self.url + "/language/translate/v2", params={"q":to_translate, "target":target,"key":self.api["key"], "format":formatting}) as resp:
                data = await resp.json()
        except:
            return
        translated_text = data["data"]["translations"][0]["translatedText"]
        detected_lang = data["data"]["translations"][0]["detectedSourceLanguage"]
        author = reaction.message.author
        em = discord.Embed(colour=author.top_role.colour, description=translated_text)
        em.set_author(name=author.display_name, icon_url=author.avatar_url)
        em.set_footer(text="{} to {}".format(detected_lang.upper(), target.upper()))
        await self.bot.send_message(reaction.message.channel, embed=em)

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def translateset(self, ctx, api_key):
        self.api["key"] = api_key
        dataIO.save_json("data/google/settings.json", self.api)
        await self.bot.say("API key set.")

def setup(bot):
    bot.add_cog(Translate(bot))