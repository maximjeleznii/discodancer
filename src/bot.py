import os
from discord_components import ComponentsBot

bot = ComponentsBot(command_prefix='%%')


@bot.event
async def on_ready():
    print(f'{bot.user} has logged in.')
    bot.load_extension('cogs.music')
    bot.load_extension('cogs.coinflip')
    bot.load_extension('cogs.eightball')
    bot.load_extension('cogs.msgdelete')
    bot.load_extension('cogs.noreddit')


bot.run(os.environ['token'])
