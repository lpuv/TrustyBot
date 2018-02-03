from PIL import Image
from PIL import ImageColor
from PIL import ImageSequence
import numpy as np
import glob
import os
import json
import numpy as np
import os
import aiohttp
import discord
from discord.ext import commands

class Feels:
    
    def __init__(self, bot):
        self.bot = bot
        self.files = "data/feels/"

    async def dl_image(self, url, ext="png"):
        with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                test = await resp.read()
                with open(self.files + "temp." + ext, "wb") as f:
                    f.write(test)

    @commands.command(pass_context=True)
    async def feels(self, ctx, user:discord.Member=None):
        if user is None:
            user = ctx.message.author
        await self.bot.send_typing(ctx.message.channel)
        ext = await self.make_feels(user)
        await self.bot.send_file(ctx.message.channel, "data/feels/tempfeels.{}".format(ext))


    async def make_feels(self, user):
        avatar = user.avatar_url if user.avatar_url != "" else user.default_avatar_url
        username = user.display_name
        userid = user.id
        ext = "png"
        if "gif" in avatar:
            ext = "gif"
        await self.dl_image(avatar, ext)
        template = Image.open(self.files + "pepetemplate.png")
        # print(template.info)
        template = template.convert("RGBA")
        colour = user.top_role.colour.to_tuple()
        avatar = Image.open(self.files + "temp." + ext)
        transparency = template.split()[-1].getdata()
        
        
        # avatar = avatar.convert("RGBA")
        # temp2.paste(logo, (150, 60), logo)


        if ext == "gif":
            for image in glob.glob("data/feels/temp/*"):
                os.remove(image)
            gif_list = [frame.copy() for frame in ImageSequence.Iterator(avatar)]
            img_list = []
            num = 0
            for frame in gif_list[:18]:
                data = np.array(template)
                red, green, blue, alpha = data.T
                blue_areas = (red == 0) & (blue == 255) & (green == 0) & (alpha == 255)
                data[..., :-1][blue_areas.T] = colour
                temp2 = Image.fromarray(data)
                frame = frame.convert("RGBA")
                frame = frame.rotate(-30, expand=True)
                frame = frame.resize((150, 150), Image.ANTIALIAS)
                temp2.paste(frame, (150, 60), frame)
                #temp2.save("data/feels/temp/{}.png".format(str(num)))
                img_list.append(temp2)
                num += 1
            # img_list = [Image.open(file).convert("RGBA") for file in glob.glob("data/feels/temp/*")]
            temp2.save("data/feels/tempfeels.gif", save_all=True, append_images=img_list, duration=1, loop=10, transparency=0)
        else:
            data = np.array(template)
            red, green, blue, alpha = data.T
            blue_areas = (red == 0) & (blue == 255) & (green == 0) & (alpha == 255)
            data[..., :-1][blue_areas.T] = colour
            temp2 = Image.fromarray(data)
            temp2 = temp2.convert("RGBA")
            avatar = avatar.convert("RGBA")
            avatar = avatar.rotate(-30, expand=True)
            avatar = avatar.resize((150, 150), Image.ANTIALIAS)
            temp2.paste(avatar, (150, 60), avatar)
            temp2.save("data/feels/tempfeels.png")
        return ext

def check_folder():
    if not os.path.exists("data/feels"):
        print("Creating data/feels folder")
        os.makedirs("data/feels")
    if not os.path.exists("data/feels/temp"):
        print("Creating data/feels/temp folder")
        os.makedirs("data/feels/temp")

def setup(bot):
    check_folder()
    bot.add_cog(Feels(bot))