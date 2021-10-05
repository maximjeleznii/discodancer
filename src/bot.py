import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='%%')

@bot.event
async def on_ready():
    print(f'{bot.user} has logged in.')
    bot.load_extension('cogs.music')
    bot.load_extension('cogs.coinflip')
    bot.load_extension('cogs.eightball')
    bot.load_extension('cogs.msgdelete')

bot.run('NzU1NDk5Nzk2NjYzMzY5ODI0.X2EMBA.bZBzYUmC8tIarsoxD7Sbg1QHABk')
