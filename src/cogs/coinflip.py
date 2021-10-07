from discord.ext import commands
import random
import datetime

class CoinflipCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['flip', 'coin',])
    async def coinflip(self, ctx, *args):
        """ Ramdomly chooses between heads and tails. """
        response = ''
        random.seed(datetime.datetime.now())
        coin = random.randint(0,1)
        if coin == 0:
            response = 'Heads'
        else:
            response = 'Tails'
        return await ctx.reply(response)

def setup(bot):
    """ Used to add this cog to the bot. """
    bot.add_cog(CoinflipCog(bot))
        