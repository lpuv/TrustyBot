import discord

class LMAO():
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        channel = message.channel
        if message.server.id != "344325990849314816":
            return
        if message.author.bot:
            return
        new_msg = ""
        emojis = []
        for emoji in message.server.emojis:
            if emoji.id in message.content:
                emojis.append(":" + emoji.name + ":" + emoji.id)
                new_msg += "<:" + emoji.name + ":" + emoji.id + "> "
        if new_msg != "":
            new_msg = await self.bot.send_message(channel, new_msg)
            for emoji in emojis:
                await self.bot.add_reaction(new_msg, emoji)
                await self.bot.add_reaction(message, emoji)

def setup(bot):
    bot.add_cog(LMAO(bot))