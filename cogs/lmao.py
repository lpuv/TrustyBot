import discord
import re

class LMAO():
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        channel = message.channel
        if message.server.id not in ["344325990849314816", "321105104931389440"]:
            return
        if message.author.bot:
            return
        new_msg = ""
        emojis = lambda: [x for x in re.split(r"[<> ]+", message.content) if x.startswith(":") and x[-1].isdigit()]
        print(emojis())
        if emojis() == []:
            return
        new_msg = "".join("<" + emoji + ">" for emoji in emojis())
        new_msg = await self.bot.send_message(channel, new_msg)

def setup(bot):
    bot.add_cog(LMAO(bot))
