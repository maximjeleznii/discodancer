from discord.ext import commands
import discord

class NoRedditCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['noreddit'])
    async def subNoReddit(self, ctx, *args):
        response = ''
        role = discord.utils.get(ctx.guild.roles, name='No Reddit')
        if role in ctx.author.roles:
            response = 'Already Subscribed'
        else:
            await ctx.author.add_roles(role)
            response = 'Subscribed'
        await ctx.reply(response)

    @commands.command(aliases=['yesreddit'])
    async def unsubNoReddit(self, ctx, *args):
        response = ''
        role = discord.utils.get(ctx.guild.roles, name='No Reddit')
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            response = ' Unsubscribed'
        else:
            response = 'Already Unsubscribed'
        await ctx.reply(response)
        
def setup(bot):
    """ Used to add this cog to the bot. """
    bot.add_cog(NoRedditCog(bot))