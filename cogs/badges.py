import discord
from discord.ext import commands
from .utils.chat_formatting import *
from .utils.dataIO import dataIO
from cogs.utils import checks
import aiohttp
import glob
import os

try:
    from PIL import Image
    from PIL import ImageColor
    from PIL import ImageFont
    from PIL import ImageDraw
    from PIL import ImageSequence
    import numpy as np
    from barcode import generate
    from barcode.writer import ImageWriter
    importavailable = True
except ImportError:
    importavailable = False


class Badges:

    def __init__(self, bot):
        self.bot = bot
        self.files = "data/badges/"
        self.blank_template = {"cia":{"code":"CIA", "loc":"data/badges/cia-template.png"}, 
                               "discord":{"code":"DISCORD", "loc":"data/badges/discord-template.png"},
                               "nypd":{"code":"NYPD", "loc":"data/badges/nypd-template.png"},
                               "cicada":{"code":"CICADA", "loc":"data/badges/cicada-template.png"},
                               "ioi":{"code":"IOI", "loc":"data/badges/IOI-template.png"},
                               "fbi":{"code":"FBI", "loc":"data/badges/fbi-template.png"},
                               "nsa":{"code":"NSA", "loc":"data/badges/nsa-template.png"},
                               "gab":{"code":"GAB", "loc":"data/badges/gab-template.png"},
                               "dop":{"code":"DOP", "loc":"data/badges/dop-template.png"},
                               "shit":{"code":"SHIT", "loc":"data/badges/shit-template.png"},
                               "bunker":{"code":"BUNKER", "loc":"data/badges/bunker-template.png"},
                               "dprk":{"code":"DPRK", "loc":"data/badges/nk-template.png"},
                               "kek":{"code":"KEK", "loc": "data/badges/kek-template.png"},
                               "Q":{"code":"Q !ITPb.qbhqo", "loc":"data/badges/Q-template.png"},
                               "dhs":{"code":"SpaceX", "loc":"data/badges/spacex-template.png"},
                               "unsc":{"code":"UNSC", "loc": "data/badges/unsc-template.png"},
                               'Anaheim Ducks':{"code":"ANA", "loc": 'data/badges/Anaheim Ducks-template.png'},
                               'Arizona Coyotes':{"code":"ARI", "loc": 'data/badges/Arizona Coyotes-template.png'},
                               'Boston Bruins':{"code":"BOS", "loc": 'data/badges/Boston Bruins-template.png'},
                               'Buffalo Sabres':{"code":"BUF", "loc": 'data/badges/Buffalo Sabres-template.png'},
                               'Calgary Flames':{"code":"CGY", "loc": 'data/badges/Calgary Flames-template.png'},
                               'Carolina Hurricanes':{"code":"CAR", "loc": 'data/badges/Carolina Hurricanes-template.png'},
                               'Chicago Blackhawks':{"code":"CHI", "loc": 'data/badges/Chicago Blackhawks-template.png'},
                               'Colorado Avalanche':{"code":"COL", "loc": 'data/badges/Colorado Avalanche-template.png'},
                               'Columbus Blue Jackets':{"code":"CBJ", "loc": 'data/badges/Columbus Blue Jackets-template.png'},
                               'Dallas Stars':{"code":"DAL", "loc": 'data/badges/Dallas Stars-template.png'},
                               'Detroit Red Wings':{"code":"DET", "loc":'data/badges/Detroit Red Wings-template.png'},
                               'Edmonton Oilers':{"code":"EDM", "loc":'data/badges/Edmonton Oilers-template.png'},
                               'Florida Panthers':{"code":"FLA", "loc": 'data/badges/Florida Panthers-template.png'},
                               'Los Angeles Kings':{"code":"LAK", "loc": 'data/badges/Los Angeles Kings-template.png'},
                               'Minnesota Wild':{"code":"MIN", "loc": 'data/badges/Minnesota Wild-template.png'},
                               'Montréal Canadiens':{"code":"MTL", "loc": 'data/badges/Montréal Canadiens-template.png'},
                               'Nashville Predators':{"code":"NSH", "loc": 'data/badges/Nashville Predators-template.png'},
                               'New Jersey Devils':{"code":"NJD", "loc": 'data/badges/New Jersey Devils-template.png'},
                               'New York Islanders':{"code":"NYI", "loc": 'data/badges/New York Islanders-template.png'},
                               'New York Rangers':{"code":"NYR", "loc": 'data/badges/New York Rangers-template.png'},
                               'Ottawa Senators':{"code":"OTT", "loc": 'data/badges/Ottawa Senators-template.png'},
                               'Philadelphia Flyers':{"code":"PHI", "loc": 'data/badges/Philadelphia Flyers-template.png'},
                               'Pittsburgh Penguins':{"code":"PIT", "loc": 'data/badges/Pittsburgh Penguins-template.png'},
                               'San Jose Sharks':{"code":"SJS", "loc": 'data/badges/San Jose Sharks-template.png'},
                               'St. Louis Blues':{"code":"STL", "loc": 'data/badges/St. Louis Blues-template.png'},
                               'Tampa Bay Lightning':{"code":"TBL", "loc": 'data/badges/Tampa Bay Lightning-template.png'},
                               'Toronto Maple Leafs':{"code":"TOR", "loc": 'data/badges/Toronto Maple Leafs-template.png'},
                               'Vancouver Canucks':{"code":"VAN", "loc": 'data/badges/Vancouver Canucks-template.png'},
                               'Vegas Golden Knights':{"code":"VGK", "loc": 'data/badges/Vegas Golden Knights-template.png'},
                               'Washington Capitals':{"code":"WSH", "loc":'data/badges/Washington Capitals-template.png'},
                               'Winnipeg Jets':{"code":"WPG", "loc": 'data/badges/Winnipeg Jets-template.png'},
                               'Seattle Thunderbirds': {"code":"STT", "loc": 'data/badges/Seattle Thunderbirds-template.png'}}

        

    async def dl_image(self, url, ext="png"):
        with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                test = await resp.read()
                with open(self.files + "temp/temp." + ext, "wb") as f:
                    f.write(test)

    async def remove_white_barcode(self):
        """https://stackoverflow.com/questions/765736/using-pil-to-make-all-white-pixels-transparent"""
        img = Image.open(self.files + "temp/bar_code_temp.png")
        img = img.convert("RGBA")
        datas = img.getdata()

        newData = []
        for item in datas:
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)

        img.putdata(newData)
        img.save(self.files + "temp/bar_code_temp.png", "PNG")

    async def invert_barcode(self):
        """https://stackoverflow.com/questions/765736/using-pil-to-make-all-white-pixels-transparent"""
        img = Image.open(self.files + "temp/bar_code_temp.png")
        img = img.convert("RGBA")
        datas = img.getdata()

        newData = []
        for item in datas:
            if item[0] == 0 and item[1] == 0 and item[2] == 0:
                newData.append((255, 255, 255))
            else:
                newData.append(item)

        img.putdata(newData)
        img.save(self.files + "temp/bar_code_temp.png", "PNG")

    async def create_badge(self, user, badge):
        avatar = user.avatar_url if user.avatar_url != "" else user.default_avatar_url
        username = user.display_name
        userid = user.id
        department = "GENERAL SUPPORT" if user.top_role.name == "@everyone" else user.top_role.name.upper()
        status = user.status
        if str(user.status) == "online":
            status = "ACTIVE"
        if str(user.status) == "offline":
            status = "COMPLETING TASK"
        if str(user.status) == "idle":
            status = "AWAITING INSTRUCTIONS"
        if str(user.status) == "dnd":
            status = "MIA"
        ext = "png"
        if "gif" in avatar:
            ext = "gif"
        await self.dl_image(avatar, ext)
        temp_barcode = generate("code39", userid, 
                                writer=ImageWriter(), 
                                output="data/badges/temp/bar_code_temp")
        await self.remove_white_barcode()
        fill = (0, 0, 0) # text colour fill
        if badge == "Q":
          fill = (255, 255, 255)
          await self.invert_barcode()
        template = Image.open(self.blank_template[badge]["loc"])
        template = template.convert("RGBA")
        avatar = Image.open(self.files + "temp/temp." + ext)
        barcode = Image.open(self.files + "temp/bar_code_temp.png")
        barcode = barcode.convert("RGBA")
        barcode = barcode.resize((555,125), Image.ANTIALIAS)
        template.paste(barcode, (400,520), barcode)
        # font for user information
        font1 = ImageFont.truetype("data/badges/ARIALUNI.TTF", 30)
        # font for extra information
        font2 = ImageFont.truetype("data/badges/ARIALUNI.TTF", 24)
        draw = ImageDraw.Draw(template)
        # adds username
        
        draw.text((225, 330), str(username), fill=fill, font=font1)
        # adds ID Class
        draw.text((225, 400), self.blank_template[badge]["code"] + "-" + str(user).split("#")[1], fill=fill, font=font1)
        # adds user id
        draw.text((250, 115), str(userid), fill=fill, font=font2)
        # adds user status
        draw.text((250, 175), status, fill=fill, font=font2)
        # adds department from top role
        draw.text((250, 235), department, fill=fill, font=font2)
        # adds user level
        draw.text((420, 475), "LEVEL " + str(len(user.roles)), fill="red", font=font1)
        # adds user level
        draw.text((60, 585), str(user.joined_at), fill=fill, font=font2)
        if ext == "gif":
            for image in glob.glob("data/badges/temp/tempgif/*"):
                os.remove(image)
            gif_list = [frame.copy() for frame in ImageSequence.Iterator(avatar)]
            img_list = []
            num = 0
            for frame in gif_list[:18]:
                watermark = frame.copy()
                watermark = watermark.convert("RGBA")
                watermark = watermark.resize((100,100))
                watermark.putalpha(128)
                id_image = frame.resize((165, 165))
                template.paste(watermark, (845,45, 945,145), watermark)
                template.paste(id_image, (60,95, 225, 260))
                template.save("data/badges/temp/tempgif/{}.png".format(str(num)))
                num += 1
            img_list = [Image.open(file) for file in glob.glob("data/badges/temp/tempgif/*")]
            template.save("data/badges/temp/tempbadge.gif", save_all=True, append_images=img_list, duration=1, loop=10)
        else:
            watermark = avatar.convert("RGBA")
            watermark.putalpha(128)
            watermark = watermark.resize((100,100))
            id_image = avatar.resize((165, 165))
            template.paste(watermark, (845,45, 945,145), watermark)
            template.paste(id_image, (60,95, 225, 260))
            template.save("data/badges/temp/tempbadge.png")

    @commands.command(pass_context=True)
    async def listbadges(self, ctx):
        await self.list_badges(ctx)

    async def list_badges(self, ctx):
        msg = ""
        for template in self.blank_template:
            msg += template + ", "
        await self.bot.send_message(ctx.message.channel, msg[:-2])
    
    @commands.command(pass_context=True, aliases=["badge"])
    async def badges(self, ctx, *, badge):
        """Creates a variety of badges use [p]listbadges to see what is available"""
        if badge.lower() == "list":
            await self.list_badges(ctx)
            return
        is_badge = False
        for template in self.blank_template:
            if badge.lower() in template.lower():
                badge = template
                is_badge = True
        if not is_badge:
            await self.bot.send_message(ctx.message.channel, "{} is not an available badge!".format(badge))
            return
        user = ctx.message.author
        avatar = user.avatar_url if user.avatar_url != "" else user.default_avatar_url
        ext = "png"
        if "gif" in avatar:
            ext = "gif"
        await self.bot.send_typing(ctx.message.channel)
        await self.create_badge(user, badge)
        await self.bot.send_file(ctx.message.channel, "data/badges/temp/tempbadge." + ext)

def check_folder():
    if not os.path.exists("data/badges"):
        print("Creating temporary badge folders folder")
        os.makedirs("data/badges")
        os.makedirs("data/badges/temp")
        os.makedirs("data/badges/temp/tempgif")

def setup(bot):
    check_folder
    if not importavailable:
        raise NameError("You need to run `pip3 install pillow` and `pip3 install numpy` and `pip3 install pybarcode`")
    n = Badges(bot)
    bot.add_cog(n)

