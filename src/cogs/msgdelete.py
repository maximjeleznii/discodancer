import re

from discord.ext import commands
import discord

class MsgDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['clear',])
    @commands.has_permissions(manage_messages = True)
    @commands.bot_has_permissions(manage_messages = True)
    async def delete(self, ctx, *args):
        """ Deletes a number of messages from either the bot or the user. """
        if not ctx.author.permissions_in(ctx.channel).manage_messages:
            return await ctx.send('You are unable to use this command.')

        embed = discord.Embed(color=discord.Color.blurple())
        delOnlyTarget = True
        maxDelLim = 20
        delLim = 10
        delTarget = self.bot.user

        if len(args) == 0:
            #default
        elif len(args) == 1:
            if args[0].isdigit():
                delLim = int(args[0])+1
            elif 'me' in args[0]:
                delTarget = ctx.author
            elif 'all' in args[0]:
                delOnlyTarget = False
        elif len(args) == 2:
            if 'me' in args[0]:
                delTarget = ctx.author
                if args[1].isdigit():
                    delLim = int(args[1])+1
            elif 'all' in args[0]:
                delOnlyTarget = False
                if args[1].isdigit():
                    delLim = int(args[1])+1
        else:
            return

        if delLim > maxDelLim:
            delLim = maxDelLim

        def is_me(m):
            return m.author == delTarget

        if delOnlyTarget:
            deleted = await ctx.channel.purge(limit=delLim, check=is_me, bulk=True)
            embed.description = f'Deleted {len(deleted)} message(s) from {delTarget.display_name}'
        else:
            deleted = await ctx.channel.purge(limit=delLim, bulk=True)
            embed.description = f'Deleted {len(deleted)} message(s)'
        return await ctx.send(embed= embed)


def setup(bot):
    """ Used to add this cog to the bot. """
    bot.add_cog(MsgDelete(bot))