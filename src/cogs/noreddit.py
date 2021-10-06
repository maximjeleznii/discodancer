from discord.ext import commands
import discord
import asyncio
from replit import db

class NoRedditCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['noreddit'])
    async def subNoReddit(self, ctx, *args):
        embed = discord.Embed(color=discord.Color.blurple())
        dbKey = 'noReddit_'+str(ctx.author.id)
        if dbKey in db.keys():
            if db[dbKey].lower()=='no':
                db[dbKey] = 'yes'
                embed.title = 'Subscribed'
            else:
                embed.title = 'Already Subscribed'
        else:
            db[dbKey] = 'yes'
            embed.title = 'Subscribed'
        await ctx.send(embed=embed)

    @commands.command(aliases=['yesreddit'])
    async def unsubNoReddit(self, ctx, *args):
        embed = discord.Embed(color=discord.Color.blurple())
        dbKey = 'noReddit_'+str(ctx.author.id)
        if dbKey in db.keys():
            if db[dbKey].lower()=='yes':
                db[dbKey] = 'no'
                embed.title = 'Unsubscribed'
            else:
                embed.title = 'Already Unsubscribed'
        else:
            db[dbKey] = 'no'
            embed.title = 'Unsubscribed'
        await ctx.send(embed=embed)
        
def setup(bot):
    """ Used to add this cog to the bot. """
    bot.add_cog(NoRedditCog(bot))