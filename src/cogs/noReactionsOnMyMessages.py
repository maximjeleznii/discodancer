import re

from discord.ext import commands
import discord

class NoReactionsOnMyMessagesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def sub2NoReactions(self, ctx, *args):
        
      

def setup(bot):
    """ Used to add this cog to the bot. """
    bot.add_cog(NoReactionsOnMyMessagesCog(bot))