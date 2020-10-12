import re

from discord.ext import commands
import lavalink
import discord
import random
import datetime

class CoinflipCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['flip', 'coin',])
    async def coinflip(self, ctx, *args):
        """ Ramdomly chooses between heads and tails. """
        embed = discord.Embed(color=discord.Color.blurple())
        random.seed(datetime.datetime.now())
        coin = random.randint(0,1)
        if coin == 0:
            embed.title = 'Heads'
        else:
            embed.title = 'Tails'
        await ctx.send(embed=embed)

def setup(bot):
    """ Used to add this cog to the bot. """
    bot.add_cog(CoinflipCog(bot))
        