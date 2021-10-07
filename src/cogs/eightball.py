from discord.ext import commands
import random
import datetime

answers = ['It is certain.',
            'It is decidedly so.', 
            'Without a doubt.',
            'Yes – definitely.',
            'You may rely on it.',
            'Reply hazy, try again.',
            'Ask again later.',
            'Better not tell you now.',
            'Cannot predict now.',
            'Concentrate and ask again.',
            'As I see it, yes.',
            'Most likely.',
            'Outlook good.',
            'Yes.',
            'Signs point to yes.',
            'Don\'t count on it.',
            'My reply is no.',
            'My sources say no.',
            'Outlook not so good.',
            'Very doubtful.']

class EightBallCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['8ball',])
    async def eightball(self, ctx, *args):
        """ Sends a random message from the answeres list. """
        response = ''
        if len(args)<1:
            response = 'Ask a yes or no question!'
        else:
            random.seed(datetime.datetime.now())
            answer = random.randint(0,len(answers))
            response = answers[answer]
        await ctx.reply(response)

def setup(bot):
    """ Used to add this cog to the bot. """
    bot.add_cog(EightBallCog(bot))