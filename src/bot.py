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

bot.run('NzU5NDk3MDU1MDUxNDQ4MzUx.X2-WwA.PArw-2Fep8tkgWbB6ZgDKP3XN6U')
