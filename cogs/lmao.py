import discord
import re
from emoji import UNICODE_EMOJI

class LMAO():
    def __init__(self, bot):
        self.bot = bot

    def bot_emojis(self, emoji_id):
        emojis = [emoji.id for emoji in self.bot.get_all_emojis()]
        if emoji_id in emojis:
            return True
        else:
            return False

    async def on_message(self, message):
        if message.channel.is_private:
            return
        channel = message.channel
        if message.server.id not in ["344325990849314816", "321105104931389440"]:
            return
        if message.author.bot:
            return
        new_msg = ""
        emojis = lambda: [x for x in re.split(r"[<> ]+", message.content) if x.startswith(":") and x[-1].isdigit() or x in UNICODE_EMOJI]
        if emojis() == []:
            return
        new_msg = "".join("<" + emoji + ">" for emoji in emojis() if emoji.startswith(":") and self.bot_emojis(emoji.split(":")[-1]))
        # new_msg = new_msg.join(emoji for emoji in emojis() if emoji in UNICODE_EMOJI)
        if new_msg != "":
            await self.bot.send_message(channel, new_msg)

def setup(bot):
    bot.add_cog(LMAO(bot))
