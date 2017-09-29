import discord
from discord.ext import commands
from cogs.utils import checks

class MassNickChange:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def changeusernicks(self, ctx, nickname=None):
        users = ""
        members = list(ctx.message.server.members)
        for user in members:
            try:
                await self.bot.change_nickname(ctx.message.server.get_member(user.id), nickname)
            except:
                await self.bot.say("I could not change {}".format(user.mention))
                pass
        if nickname is None:
            await self.bot.say("Done! All usernames reset!")
        else:
            await self.bot.say("Done! All users are now named {}!".format(nickname))

def setup(bot):
    bot.add_cog(MassNickChange(bot))