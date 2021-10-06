from discord.ext import commands
from replit import db

class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Ready!')
        print('Logged in as ---->', self.bot.user)
        print('ID:', self.bot.user.id)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        print('dab')
        if reaction.emoji.id == 893943169119572018 or reaction.emoji.id == 893943169065033779:
            print('dab1')
            dbKey = 'noReddit_'+str(reaction.message.author.id)
            if dbKey in db.keys():
                if dbKey=='yes':
                    print('dab2')
                    await reaction.clear()

def setup(bot):
    bot.add_cog(EventsCog(bot))