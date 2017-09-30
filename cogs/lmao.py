import discord

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
        emojis = lambda: [x.rpartition(">")[0].partition("<")[2] for x in message.content.split(' ') if x.startswith('<:') and x.endswith('>')]
        if emojis() == []:
            return
        new_msg = "".join("<" + emoji + ">" for emoji in emojis())
        new_msg = await self.bot.send_message(channel, new_msg)
        for emoji in emojis():
            await self.bot.add_reaction(new_msg, emoji)
            await self.bot.add_reaction(message, emoji)
def setup(bot):
    bot.add_cog(LMAO(bot))